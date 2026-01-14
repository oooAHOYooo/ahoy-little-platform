from flask import Flask, render_template, jsonify, request, session, send_from_directory, make_response, redirect, url_for
try:
    from flask_session import Session as FlaskSession
except Exception:  # ImportError or env issues
    FlaskSession = None
from flask_login import current_user, login_required
import os
import json
import uuid
from datetime import datetime, timedelta, timezone
import random
import hashlib
from functools import wraps
# Removed: user_manager.py (consolidated to database-based auth)
from dotenv import load_dotenv
load_dotenv()
import re, pathlib
from pathlib import Path

from config import get_config
from extensions import bcrypt, login_manager, limiter, init_cors
from utils.auth import admin_required, get_effective_user
from utils.observability import init_sentry
from utils.logging_init import init_logging, init_request_logging
from utils.security_headers import attach_security_headers, create_csp_report_blueprint
from utils.csrf_init import init_csrf
# Removed: blueprints/auth.py (consolidated into api/auth)
from blueprints.api.auth import bp as api_auth_bp
from blueprints.activity import bp as activity_bp
# Removed: blueprints/playlists.py and blueprints/bookmarks.py (shadowed by API blueprints)
# Removed: blueprints/collections.py (feature removed)
# Removed: gamify blueprint (feature removed)
from blueprints.payments import bp as payments_bp
from routes.boost_stripe import bp as boost_stripe_bp
from routes.boost_stripe import boost_api_bp
from routes.stripe_webhooks import bp as stripe_webhooks_bp
from services.listening import start_session as listening_start_session, end_session as listening_end_session
from services.user_resolver import resolve_db_user_id
from db import get_session
from models import UserArtistFollow
from models import Purchase

# Initialize search index on app startup
def initialize_search_index():
    """Initialize the search index with all content"""
    try:
        from search_indexer import search_index
        
        data_sources = {
            'music': 'static/data/music.json',
            'shows': 'static/data/shows.json',
            'artists': 'static/data/artists.json'
        }
        
        search_index.reindex(data_sources)
        print(f"✅ Search index initialized with {search_index.total_docs} documents")
        
    except Exception as e:
        print(f"❌ Error initializing search index: {e}")

def startup_logging(app):
    """Log startup configuration for operational visibility"""
    import structlog
    import os
    from utils.observability import get_release
    
    logger = structlog.get_logger()
    
    # Logging configuration
    flask_env = os.getenv("FLASK_ENV", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging_mode = "json" if flask_env == "production" else "console"
    
    # Sentry configuration
    sentry_dsn = os.getenv("SENTRY_DSN")
    sentry_enabled = bool(sentry_dsn)
    release = get_release()
    
    # Rate limiting configuration
    rate_limit_default = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")
    rate_limit_auth = os.getenv("RATE_LIMIT_AUTH", "10 per minute")
    
    # Security configuration
    csrf_enabled = True
    security_headers_enabled = flask_env == "production"
    
    # Emit startup logs
    logger.info("Application startup",
               logging_mode=logging_mode,
               level=log_level,
               request_id=None)
    
    logger.info("Sentry configuration",
               sentry_enabled=sentry_enabled,
               environment=flask_env,
               release=release,
               request_id=None)
    
    logger.info("Rate limiting configuration",
               default_limit=rate_limit_default,
               auth_limit=rate_limit_auth,
               request_id=None)
    
    logger.info("Security configuration",
               csrf_enabled=csrf_enabled,
               security_headers_enabled=security_headers_enabled,
               request_id=None)

def create_app():
    app = Flask(__name__)

    # Fast & flexible: accept both "/route" and "/route/" everywhere.
    # This prevents redirect surprises and keeps dev UX smooth.
    app.url_map.strict_slashes = False

    app.config.from_object(get_config())
    
    # Initialize structured logging
    init_logging()

    # minimal config safe for CI
    app.config.setdefault("JSON_SORT_KEYS", False)
    
    # If you use Flask-Limiter, this avoids scary warnings in CI logs.
    if os.getenv("CI"):
        app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")

    # SECRET_KEY is loaded from config.py (which enforces production requirement)
    # No need to override here - config.py handles it properly
    # Initialize server-side sessions (filesystem by default per config)
    if FlaskSession is not None:
        FlaskSession(app)
    else:
        print("⚠️  Flask-Session not available; using client-side cookies only. Activate venv or install Flask-Session.")
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    init_cors(app)
    login_manager.login_view = "auth_page"
    
    # Initialize observability
    init_sentry(app)
    
    # Initialize request logging
    init_request_logging(app)
    
    # Initialize security headers
    attach_security_headers(app)
    
    # Register CSP report blueprint
    app.register_blueprint(create_csp_report_blueprint())
    
    # Initialize CSRF protection
    csrf = init_csrf(app)
    
    # Log startup configuration
    startup_logging(app)
    
    # Register blueprints
    # Removed: blueprints/auth.py (consolidated into api/auth)
    from blueprints.api.playlists import bp as api_playlists_bp
    from blueprints.api.bookmarks import bp as api_bookmarks_bp
    from blueprints.api.tips import bp as api_tips_bp
    
    app.register_blueprint(api_auth_bp)  # Session-based API auth
    app.register_blueprint(api_playlists_bp)  # Database-based playlists API (takes precedence)
    app.register_blueprint(api_bookmarks_bp)  # Database-based bookmarks API (takes precedence)
    app.register_blueprint(api_tips_bp)  # Tips/boost API
    app.register_blueprint(activity_bp)
    # Removed: playlists_bp and bookmarks_bp - shadowed by API blueprints, never reached
    # Use blueprints/api/playlists.py and blueprints/api/bookmarks.py instead
    # Removed: collections_bp (feature removed)
    # Removed: gamify_api_bp (feature removed)
    app.register_blueprint(payments_bp)
    app.register_blueprint(boost_stripe_bp)
    app.register_blueprint(boost_api_bp)
    app.register_blueprint(stripe_webhooks_bp)
    
    # Initialize search index
    with app.app_context():
        initialize_search_index()

    # Register Click CLI commands
    # Removed: gamify CLI commands (feature removed)

    # Health check endpoint
    @app.get("/healthz")
    def healthz():
        from ahoy.version import __version__
        return jsonify({"ok": True, "version": __version__}), 200

    # Readiness check that actually verifies DB connectivity
    @app.get("/readyz")
    def readyz():
        try:
            from db import get_session
            from sqlalchemy import text
            with get_session() as session:
                session.execute(text("SELECT 1"))
            return jsonify({"status": "ready"}), 200
        except Exception as e:
            return jsonify({"status": "error", "detail": str(e)}), 500

    # Operational self-test endpoint
    @app.get("/ops/selftest")
    def ops_selftest():
        try:
            from db import get_session
            from sqlalchemy import text
            from models import User
            from alembic.runtime.migration import MigrationContext

            with get_session() as session:
                # 1) Basic connectivity
                session.execute(text("SELECT 1"))

                # 2) ORM query
                users_count = session.query(User).count()

                # 3) Alembic current revision in DB
                connection = session.connection()
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()

            return jsonify({
                "ready": True,
                "alembic": current_rev or "unknown",
                "counts": {"users": int(users_count)}
            }), 200
        except Exception as e:
            return jsonify({
                "ready": False,
                "detail": str(e)
            }), 500

    # Sentry test route (production only)
    @app.get("/_boom")
    def sentry_test():
        """Test route for Sentry error tracking - only works in production"""
        import os
        if os.getenv("FLASK_ENV") == "production" or os.getenv("SENTRY_TEST_ROUTE") == "true":
            raise Exception("Sentry test exception - this is intentional")
        return jsonify({"error": "Not found"}), 404

    # Context processor to inject login flag into templates
    @app.context_processor
    def inject_login_flag():
        from flask_login import current_user
        return {"LOGGED_IN": current_user.is_authenticated}

    # Expose Stripe publishable key in templates
    @app.context_processor
    def inject_stripe_publishable_key():
        try:
            key = app.config.get("STRIPE_PUBLISHABLE_KEY", "")
        except Exception:
            key = ""
        return {"STRIPE_PUBLISHABLE_KEY": key}

    # Enable compression (optional)
    try:
        from flask_compress import Compress
        Compress(app)
        print("✅ Compression enabled")
    except ImportError:
        print("⚠️  Flask-Compress not available, compression disabled")

    # Downloads routes
    DOWNLOADS_DIR = Path("downloads")
    DIST_DIR = Path("dist")
    
    @app.route('/downloads')
    def downloads_page():
        """Landing page to download latest desktop builds."""
        import requests
        from datetime import datetime
        
        def _format_size(n: int) -> str:
            """Format file size in human-readable format"""
            units = ["B", "KB", "MB", "GB", "TB"]
            size = float(n)
            idx = 0
            while size >= 1024 and idx < len(units) - 1:
                size /= 1024.0
                idx += 1
            return f"{size:.1f} {units[idx]}"
        
        def _get_file_type(filename: str) -> dict:
            """Determine file type and platform from filename"""
            filename_lower = filename.lower()
            if filename_lower.endswith('.dmg'):
                return {'type': 'installer', 'platform': 'macOS', 'icon': '🍎', 'description': 'DMG Installer (Recommended)'}
            elif filename_lower.endswith('.app'):
                return {'type': 'standalone', 'platform': 'macOS', 'icon': '🍎', 'description': 'App Bundle (Standalone)'}
            elif 'setup.exe' in filename_lower or filename_lower.endswith('-setup.exe'):
                return {'type': 'installer', 'platform': 'Windows', 'icon': '🪟', 'description': 'Setup Installer (Recommended)'}
            elif filename_lower.endswith('.exe'):
                return {'type': 'standalone', 'platform': 'Windows', 'icon': '🪟', 'description': 'Executable (Standalone)'}
            elif filename_lower.endswith('.tar.gz') or filename_lower.endswith('.tgz'):
                return {'type': 'archive', 'platform': 'Linux', 'icon': '🐧', 'description': 'Linux Archive'}
            elif filename_lower.endswith('.apk'):
                return {'type': 'installer', 'platform': 'Android', 'icon': '🤖', 'description': 'Android APK'}
            return {'type': 'other', 'platform': 'Unknown', 'icon': '📦', 'description': 'Download'}
        
        # Try to fetch latest release from GitHub
        release_assets = []
        release_tag = "No releases yet"
        
        try:
            # Use GitHub API to get latest release
            github_token = os.getenv('GITHUB_TOKEN')
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            # Get repository info from git remote or use default
            repo_owner = "oooAHOYooo"  # Update this to match your GitHub username
            repo_name = "ahoy-little-platform"
            
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                release_data = response.json()
                release_tag = release_data.get('tag_name', 'Unknown')
                
                # Filter and format assets
                for asset in release_data.get('assets', []):
                    asset_name = asset['name']
                    asset_size = asset['size']
                    size_mb = asset_size / (1024 * 1024)
                    
                    # Only include desktop/Android assets
                    if any(platform in asset_name for platform in ['macOS', 'Windows', 'Linux', 'Android', 'dmg', 'exe', 'Setup', '.app']):
                        file_info = _get_file_type(asset_name)
                        release_assets.append({
                            'name': asset_name,
                            'size_bytes': asset_size,
                            'size_mb': f"{size_mb:.1f}",
                            'size_label': _format_size(asset_size),
                            'download_url': asset['browser_download_url'],
                            **file_info
                        })
                
                # Sort by platform preference, then by type (installer first)
                platform_order = {'macOS': 0, 'Windows': 1, 'Linux': 2, 'Android': 3}
                type_order = {'installer': 0, 'standalone': 1, 'archive': 2, 'other': 3}
                release_assets.sort(key=lambda x: (
                    platform_order.get(x.get('platform', 'Other'), 99),
                    type_order.get(x.get('type', 'other'), 99)
                ))
        
        except Exception as e:
            print(f"Error fetching GitHub release: {e}")
            # Fallback to local files if GitHub fails
            pass
        
        # Collect local files from both dist/ and downloads/ directories
        local_files = []
        
        # Check dist/ directory (where build scripts put files)
        if DIST_DIR.exists():
            try:
                # Collect files first, then sort safely
                dist_files = []
                for p in DIST_DIR.iterdir():
                    try:
                        if p.is_file() and not p.name.startswith('.'):
                            dist_files.append(p)
                    except (OSError, PermissionError):
                        # Skip files that can't be accessed
                        continue
                
                # Sort by modification time with error handling
                try:
                    dist_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                except (OSError, PermissionError):
                    # If sorting fails, use unsorted list
                    pass
                
                for p in dist_files:
                    try:
                        file_stat = p.stat()
                        file_info = _get_file_type(p.name)
                        local_files.append({
                            'name': p.name,
                            'size_bytes': file_stat.st_size,
                            'size_label': _format_size(file_stat.st_size),
                            'size_mb': f"{file_stat.st_size / (1024 * 1024):.1f}",
                            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            'url': f"/downloads/dist/{p.name}",
                            **file_info
                        })
                    except (OSError, PermissionError):
                        # Skip files that can't be accessed
                        continue
            except Exception as e:
                print(f"Error processing dist/ directory: {e}")
        
        # Check downloads/ directory (for manually placed files)
        if DOWNLOADS_DIR.exists():
            try:
                # Collect files first, then sort safely
                download_files = []
                for p in DOWNLOADS_DIR.iterdir():
                    try:
                        if p.is_file() and not p.name.startswith('.'):
                            download_files.append(p)
                    except (OSError, PermissionError):
                        # Skip files that can't be accessed
                        continue
                
                # Sort by modification time with error handling
                try:
                    download_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                except (OSError, PermissionError):
                    # If sorting fails, use unsorted list
                    pass
                
                for p in download_files:
                    try:
                        file_stat = p.stat()
                        file_info = _get_file_type(p.name)
                        local_files.append({
                            'name': p.name,
                            'size_bytes': file_stat.st_size,
                            'size_label': _format_size(file_stat.st_size),
                            'size_mb': f"{file_stat.st_size / (1024 * 1024):.1f}",
                            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            'url': f"/downloads/{p.name}",
                            **file_info
                        })
                    except (OSError, PermissionError):
                        # Skip files that can't be accessed
                        continue
            except Exception as e:
                print(f"Error processing downloads/ directory: {e}")
        
        # Sort local files by platform and type
        if local_files:
            platform_order = {'macOS': 0, 'Windows': 1, 'Linux': 2, 'Android': 3}
            type_order = {'installer': 0, 'standalone': 1, 'archive': 2, 'other': 3}
            local_files.sort(key=lambda x: (
                platform_order.get(x.get('platform', 'Other'), 99),
                type_order.get(x.get('type', 'other'), 99)
            ))
        
        # Use GitHub assets if available, otherwise use local files
        if release_assets:
            return render_template('downloads.html', files=None, release_assets=release_assets, release_tag=release_tag)
        else:
            return render_template('downloads.html', files=local_files, release_assets=None, release_tag="Local Builds")

    @app.route('/downloads/<path:filename>')
    def download_artifact(filename):
        """Serve built desktop artifacts from downloads/ directory."""
        if not DOWNLOADS_DIR.exists():
            return jsonify({'error': 'No downloads available'}), 404
        try:
            return send_from_directory(str(DOWNLOADS_DIR), filename, as_attachment=True)
        except Exception:
            return jsonify({'error': 'File not found'}), 404
    
    @app.route('/downloads/dist/<path:filename>')
    def download_dist_artifact(filename):
        """Serve built desktop artifacts from dist/ directory."""
        if not DIST_DIR.exists():
            return jsonify({'error': 'No builds available'}), 404
        try:
            return send_from_directory(str(DIST_DIR), filename, as_attachment=True)
        except Exception:
            return jsonify({'error': 'File not found'}), 404

    @app.route('/')
    def home():
        """Main discovery page with Now Playing feed"""
        response = make_response(render_template('home.html'))
        response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
        return response

    return app

# Create the app instance for backward compatibility
app = create_app()
# ==== Forgiving Artist API (slug or case-insensitive name) ==================
ARTISTS_PATH = pathlib.Path("static/data/artists.json")

def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").strip().lower()).strip("-")

def _load_artists_flat():
    try:
        data = load_json_data('artists.json', {'artists': []})
        return data.get('artists', [])
    except Exception:
        return []

@app.get("/api/artist/<slug_or_name>")
def api_artist(slug_or_name):
    key = (slug_or_name or "").strip().lower()
    artists = _load_artists_flat()
    # slug match
    for a in artists:
        if _slugify(a.get("slug") or a.get("name", "")) == key:
            return jsonify(a)
    # case-insensitive name match
    for a in artists:
        if (a.get("name", "").strip().lower()) == key:
            return jsonify(a)
    return jsonify({"error": "not_found"}), 404
# ===========================================================================
# ==== JSON Sitemap: GET /api/_sitemap =======================================
from urllib.parse import unquote
from flask import jsonify

def _generate_sitemap(flask_app):
    def is_method(m): return m in ("GET","POST","PUT","PATCH","DELETE")
    routes, seen = [], {}
    for rule in flask_app.url_map.iter_rules():
        if rule.endpoint == "static":  # skip static
            continue
        methods = tuple(sorted([m for m in rule.methods if is_method(m)]))
        info = {
            "rule": unquote(str(rule)),
            "endpoint": rule.endpoint,
            "methods": list(methods),
            "blueprint": rule.endpoint.split(".", 1)[0] if "." in rule.endpoint else None,
        }
        routes.append(info)
        seen.setdefault((info["rule"], methods), []).append(info["endpoint"])

    duplicates = [
        {"rule": r, "methods": list(m), "endpoints": eps}
        for (r, m), eps in seen.items() if len(eps) > 1
    ]
    routes.sort(key=lambda r: (r["rule"], r["methods"]))
    return {"routes": routes, "duplicates": duplicates}

@app.get("/api/_sitemap")
def api_sitemap():
    return jsonify(_generate_sitemap(app))
# ============================================================================

@app.route('/checkout')
def checkout_page():
    """
    Universal checkout entrypoint (GET)
    Accepts query params:
      type, artist_id, amount, item_id, qty, title
    Renders a CSRF-protected form that POSTS to /checkout/process
    """
    from decimal import Decimal
    from utils.csrf import generate_csrf_token
    from blueprints.payments import calculate_boost_fees
    q = request.args
    kind = (q.get('type') or 'boost').strip()
    artist_id = q.get('artist_id') or ''
    amount = q.get('amount') or ''
    title = q.get('title') or ''
    item_id = q.get('item_id') or ''
    qty = int(q.get('qty') or '1')

    stripe_fee = platform_fee = total = None
    try:
        amt = Decimal(str(amount or '0'))
        if kind in ['boost', 'tip'] and amt > 0:
            stripe_fee, platform_fee, total, _, _ = calculate_boost_fees(amt)
        else:
            total = amt
    except Exception:
        total = None

    return render_template(
        'checkout.html',
        kind=kind,
        artist_id=artist_id,
        amount=amount,
        item_id=item_id,
        qty=qty,
        title=title,
        stripe_fee=float(stripe_fee) if stripe_fee is not None else None,
        platform_fee=float(platform_fee) if platform_fee is not None else None,
        total=float(total) if total is not None else None,
        csrf_token=generate_csrf_token(),
    )


@app.route('/checkout/process', methods=['POST'])
def checkout_process():
    """
    Universal checkout processor (POST)
    Validates CSRF, records a Purchase, and (optionally) creates Stripe PI.
    Note: This route uses custom CSRF validation, not Flask-WTF's automatic validation.
    """
    from utils.csrf import validate_csrf, generate_csrf_token, CSRF_SESSION_KEY
    import structlog
    logger = structlog.get_logger()
    
    # Debug CSRF validation - log everything
    sent_token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    session_token = session.get(CSRF_SESSION_KEY)
    
    # Log all form data for debugging
    logger.info("CSRF validation attempt",
                sent_token_present=bool(sent_token),
                sent_token_preview=sent_token[:20] + "..." if sent_token and len(sent_token) > 20 else sent_token,
                session_token_present=bool(session_token),
                session_token_preview=str(session_token)[:20] + "..." if session_token and len(str(session_token)) > 20 else str(session_token),
                form_keys=list(request.form.keys()),
                session_keys=list(session.keys()) if session else [])
    
    # Check if session is working
    if not session_token:
        logger.error("No CSRF token in session! Session might not be persisting.")
        # Generate a new token and try again
        new_token = generate_csrf_token()
        logger.info("Generated new CSRF token", token_preview=new_token[:20] + "...")
        return render_template('checkout.html', 
                             error="Session expired. Please try again.", 
                             csrf_token=new_token,
                             kind=request.form.get('type', 'boost'),
                             artist_id=request.form.get('artist_id', ''),
                             amount=request.form.get('amount', ''),
                             item_id=request.form.get('item_id', ''),
                             qty=int(request.form.get('qty', '1'))), 400
    
    if not validate_csrf():
        logger.warning("CSRF validation failed",
                      sent_token_present=bool(sent_token),
                      session_token_present=bool(session_token),
                      tokens_match=(sent_token == str(session_token)) if (sent_token and session_token) else False)
        # Re-render checkout with a new token and error
        return render_template('checkout.html', 
                             error="Invalid CSRF token. Please refresh and try again.", 
                             csrf_token=generate_csrf_token(),
                             kind=request.form.get('type', 'boost'),
                             artist_id=request.form.get('artist_id', ''),
                             amount=request.form.get('amount', ''),
                             item_id=request.form.get('item_id', ''),
                             qty=int(request.form.get('qty', '1'))), 400

    form = request.form
    kind = (form.get('type') or 'boost').strip()
    artist_id = form.get('artist_id') or None
    item_id = form.get('item_id') or None
    qty = int(form.get('qty') or '1')
    try:
        amount = float(form.get('amount') or '0')
    except Exception:
        amount = 0.0
    try:
        total = float(form.get('total') or form.get('computed_total') or amount)
    except Exception:
        total = amount

    user_id = None
    try:
        user_id = session.get('user_id') or session.get('uid') or None
        if user_id:
            user_id = int(user_id)
    except Exception:
        user_id = None

    # Persist a pending purchase
    from db import get_session
    purchase_id = None
    with get_session() as s:
        p = Purchase(
            type=kind,
            user_id=user_id,
            artist_id=str(artist_id) if artist_id else None,
            item_id=str(item_id) if item_id else None,
            qty=qty,
            amount=amount,
            total=total,
            status='pending',
        )
        s.add(p)
        s.flush()
        purchase_id = p.id
        s.commit()

    # Placeholder: mark paid_test and redirect to success
    return redirect(url_for('checkout_success', pid=purchase_id))

# Exempt checkout_process from Flask-WTF CSRF after route is registered
_csrf_ext = app.extensions.get('csrf')
if _csrf_ext is not None:
    _csrf_ext.exempt(checkout_process)


@app.route('/success')
def checkout_success():
    pid = request.args.get('pid')
    artist_id = None
    amount = None
    try:
        if pid:
            from db import get_session
            from models import Purchase
            with get_session() as s:
                p = s.query(Purchase).filter(Purchase.id == int(pid)).first()
                if p:
                    artist_id = p.artist_id
                    amount = p.amount
    except Exception:
        artist_id = None
        amount = None
    return render_template('success.html', pid=pid, artist_id=artist_id, amount=amount)


# Debug routes removed - debug functionality available via /debug endpoint

try:
    from flask_compress import Compress
    Compress(app)
    print("✅ Compression enabled")
except ImportError:
    print("⚠️  Flask-Compress not available, compression disabled")

# Cache configuration
CACHE_TIMEOUT = 300  # 5 minutes

# In-memory cache for JSON data files (prevents repeated disk I/O)
_json_data_cache = {}
_json_file_mtimes = {}

# Removed: USERS_FILE, ACTIVITY_FILE, load_users(), save_users() - using database now

def load_json_data(filename, default=None, cache_duration=300):
    """Load JSON data from file with in-memory caching and file modification time checking"""
    import os
    from time import time
    
    filepath = f'static/data/{filename}'
    cache_key = filepath
    
    # Check if file exists
    if not os.path.exists(filepath):
        return default or {}
    
    # Get file modification time
    try:
        current_mtime = os.path.getmtime(filepath)
    except OSError:
        current_mtime = 0
    
    # Check cache validity
    if cache_key in _json_data_cache:
        cached_data, cached_time, cached_mtime = _json_data_cache[cache_key]
        # Cache is valid if:
        # 1. Not expired (within cache_duration seconds)
        # 2. File hasn't been modified
        if (time() - cached_time < cache_duration and 
            cached_mtime == current_mtime):
            return cached_data
    
    # Load from disk
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update cache
        _json_data_cache[cache_key] = (data, time(), current_mtime)
        
        # Clean up old cache entries (older than 1 hour)
        cleanup_time = time() - 3600
        keys_to_remove = [
            k for k, (_, t, _) in _json_data_cache.items() 
            if t < cleanup_time
        ]
        for k in keys_to_remove:
            _json_data_cache.pop(k, None)
        
        return data
    except FileNotFoundError:
        return default or {}
    except json.JSONDecodeError as e:
        # Log the error and return default
        import logging
        logging.error(f'JSON decode error in {filename}: {e}')
        return default or {}
    except Exception as e:
        # Catch any other errors
        import logging
        logging.error(f'Error loading {filename}: {e}')
        return default or {}


def _etag_for_static_json(filename: str) -> str | None:
    """Create a weak ETag for static/data JSON files based on mtime + size.

    This enables 304 Not Modified responses, reducing payload + parse time.
    """
    try:
        p = Path("static") / "data" / filename
        st = p.stat()
        return f'W/"{int(st.st_mtime)}-{int(st.st_size)}"'
    except Exception:
        return None


def _cached_json_response(filename: str, default: dict, max_age_seconds: int = 300):
    """Return a JSON response with Cache-Control + ETag (conditional GET)."""
    etag = _etag_for_static_json(filename)
    cache_control = f"public, max-age={int(max_age_seconds)}"

    # Conditional GET
    inm = request.headers.get("If-None-Match")
    if etag and inm == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = cache_control
        resp.headers["Vary"] = "Accept-Encoding"
        return resp

    data = load_json_data(filename, default, cache_duration=max_age_seconds)
    resp = jsonify(data)
    resp.headers["Cache-Control"] = cache_control
    resp.headers["Vary"] = "Accept-Encoding"
    if etag:
        resp.headers["ETag"] = etag
    return resp

# Replaced auth_required with Flask-Login's @login_required
# Use: from flask_login import login_required


@app.route('/music')
def music():
    """Music library page"""
    response = make_response(render_template('music.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/shows')
def shows():
    """Shows/video content page"""
    response = make_response(render_template('shows.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/live-tv')
def live_tv_page():
    """Live TV page with four channels and guide."""
    response = make_response(render_template('live_tv.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/artists')
def artists():
    """Artists directory page"""
    response = make_response(render_template('artists.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/podcasts')
def podcasts_page():
    """Podcasts hub page"""
    def slugify(s: str) -> str:
        s = (s or '').strip().lower()
        s = re.sub(r"['’]", '', s)
        s = re.sub(r'[^a-z0-9]+', '-', s)
        s = re.sub(r'-{2,}', '-', s).strip('-')
        return s or 'show'

    def extract_show_name(title: str) -> str:
        t = (title or '').strip()
        lower = t.lower()
        # Known patterns
        if lower.startswith('the rob show'):
            return 'The Rob Show'
        if lower.startswith('my friend'):
            return 'My Friend'
        if lower.startswith('found cassettes'):
            return 'Found Cassettes'
        if lower.startswith("tyler's show"):
            return "Tyler's Show"
        # Fallback: take leading segment before " - " and strip episode numbering
        head = re.split(r'\s*[-–—]\s*', t, maxsplit=1)[0].strip()
        head = re.sub(r'\s*#\s*\d+.*$', '', head).strip()
        return head or 'Podcast'

    # Keep existing “spot” slugs working while we move to data-driven shows.
    slug_aliases = {
        'The Rob Show': 'rob',
        'Rob Meglio Show': 'rob',
        'Poets & Friends': 'poets-and-friends',
        "Tyler’s New Broadcast": 'tyler-broadcast',
        "Tyler's New Broadcast": 'tyler-broadcast',
        "Tyler's Show": 'tylers-show',
    }

    def build_podcasts_payload():
        """
        Build the podcasts payload expected by templates from static/data/podcastCollection.json.
        Each distinct show gets its own URL slug at /podcasts/<slug>.
        """
        collection = load_json_data('podcastCollection.json', {'podcasts': []})
        items = list(collection.get('podcasts', []) or [])

        active_items = [p for p in items if p.get('active', True)]
        active_items.sort(
            key=lambda p: (str(p.get('date') or p.get('releaseDate') or ''), int(p.get('id') or 0)),
            reverse=True
        )

        episodes = []
        for p in active_items:
            title = p.get('title') or 'Untitled Episode'
            show_name = extract_show_name(title)
            show_slug = slug_aliases.get(show_name) or slugify(show_name)
            episodes.append({
                'id': str(p.get('id') or title),
                'title': title,
                'description': p.get('description') or '',
                'date': p.get('date') or p.get('releaseDate') or '',
                'duration': '',  # not provided in collection
                'duration_seconds': 0,
                'audio_url': p.get('mp3url') or '',
                'artwork': p.get('thumbnail') or '/static/img/default-cover.jpg',
                'show_slug': show_slug,
                'show_title': show_name,
            })

        # Group into shows
        shows_by_slug = {}
        for e in episodes:
            s = shows_by_slug.setdefault(e['show_slug'], {
                'slug': e['show_slug'],
                'title': e.get('show_title') or e['show_slug'],
                'description': '',
                'artwork': e.get('artwork') or '/static/img/default-cover.jpg',
                'last_updated': e.get('date') or '',
                'episodes': [],
            })
            s['episodes'].append({
                'id': e['id'],
                'title': e['title'],
                'description': e['description'],
                'date': e['date'],
                'duration': e['duration'],
                'duration_seconds': e['duration_seconds'],
                'audio_url': e['audio_url'],
                'artwork': e['artwork'],
            })

        # Stable ordering in hub: newest-updated first
        shows = list(shows_by_slug.values())
        shows.sort(key=lambda s: str(s.get('last_updated') or ''), reverse=True)

        return {'shows': shows, 'episodes': episodes}

    data = build_podcasts_payload()
    return render_template('podcasts.html', podcasts=data)

@app.route('/podcasts/<show_slug>')
def podcast_show_page(show_slug):
    """Podcast show detail page"""
    # Build the same payload as the hub, then pick the requested show.
    # (Kept simple/inline to avoid refactoring outside this feature branch.)
    collection = load_json_data('podcastCollection.json', {'podcasts': []})
    items = list(collection.get('podcasts', []) or [])
    active_items = [p for p in items if p.get('active', True)]
    active_items.sort(
        key=lambda p: (str(p.get('date') or p.get('releaseDate') or ''), int(p.get('id') or 0)),
        reverse=True
    )

    def slugify(s: str) -> str:
        s = (s or '').strip().lower()
        s = re.sub(r"['’]", '', s)
        s = re.sub(r'[^a-z0-9]+', '-', s)
        s = re.sub(r'-{2,}', '-', s).strip('-')
        return s or 'show'

    def extract_show_name(title: str) -> str:
        t = (title or '').strip()
        lower = t.lower()
        if lower.startswith('the rob show'):
            return 'The Rob Show'
        if lower.startswith('my friend'):
            return 'My Friend'
        if lower.startswith('found cassettes'):
            return 'Found Cassettes'
        if lower.startswith("tyler's show"):
            return "Tyler's Show"
        head = re.split(r'\s*[-–—]\s*', t, maxsplit=1)[0].strip()
        head = re.sub(r'\s*#\s*\d+.*$', '', head).strip()
        return head or 'Podcast'

    slug_aliases = {
        'The Rob Show': 'rob',
        'Rob Meglio Show': 'rob',
        'Poets & Friends': 'poets-and-friends',
        "Tyler’s New Broadcast": 'tyler-broadcast',
        "Tyler's New Broadcast": 'tyler-broadcast',
        "Tyler's Show": 'tylers-show',
    }

    episodes = []
    for p in active_items:
        title = p.get('title') or 'Untitled Episode'
        show_name = extract_show_name(title)
        sslug = slug_aliases.get(show_name) or slugify(show_name)
        episodes.append({
            'id': str(p.get('id') or title),
            'title': title,
            'description': p.get('description') or '',
            'date': p.get('date') or p.get('releaseDate') or '',
            'duration': '',
            'duration_seconds': 0,
            'audio_url': p.get('mp3url') or '',
            'artwork': p.get('thumbnail') or '/static/img/default-cover.jpg',
            'show_slug': sslug,
            'show_title': show_name,
        })

    show_eps = [e for e in episodes if e['show_slug'] == show_slug]
    if not show_eps:
        # Allow show pages to exist even before episodes arrive if they are in the “known” aliases.
        # Otherwise, 404.
        known_slugs = set(slug_aliases.values())
        if show_slug not in known_slugs:
            return render_template('404.html'), 404

    # Get description from first episode or use a default
    description = ''
    if show_eps:
        # Try to get description from show metadata or first episode
        description = show_eps[0].get('description', '') or ''
        # If episode description is too specific, use a generic one
        if description and len(description) < 50:
            description = f"Episodes and conversations from {show_eps[0].get('show_title', show_slug.replace('-', ' ').title())}."
    
    show = {
        'slug': show_slug,
        'title': (show_eps[0].get('show_title') if show_eps else show_slug.replace('-', ' ').title()),
        'description': description or f"Episodes and conversations from {show_eps[0].get('show_title', show_slug.replace('-', ' ').title()) if show_eps else show_slug.replace('-', ' ').title()}.",
        'artwork': (show_eps[0].get('artwork') if show_eps else '/static/img/default-cover.jpg'),
        'last_updated': (show_eps[0].get('date') if show_eps else ''),
        'episodes': [
            {k: e[k] for k in ['id', 'title', 'description', 'date', 'duration', 'duration_seconds', 'audio_url', 'artwork']}
            for e in show_eps
        ],
    }
    return render_template('podcast_show.html', show=show)

@app.route('/events')
def events_page():
    """Upcoming live Ahoy events (separate from /dashboard and /performances)."""
    events_data = load_json_data('events.json', {'events': []})
    videos_data = load_json_data('videos.json', {'videos': []})
    response = make_response(render_template('events.html', events=events_data, videos=videos_data))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/performances')
def performances():
    """Performances page"""
    response = make_response(render_template('performances.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/merch')
def merch():
    """Merch store page"""
    from storage import read_json
    products = read_json('data/products.json', {})
    merch_catalog = read_json('data/merch.json', {"items": []})
    response = make_response(render_template('merch.html', products=products, merch=merch_catalog))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/player')
def player():
    """Full-screen player page"""
    media_id = request.args.get('id')
    media_type = request.args.get('type', 'music')  # music, show, video
    return render_template('player.html', media_id=media_id, media_type=media_type)

@app.route('/artists/featured')
def featured_artists():
    """Featured artists page"""
    artists_data = load_json_data('artists.json', {'artists': []})
    featured = [a for a in artists_data.get('artists', []) if a.get('featured', False)]
    return render_template('artists/featured.html', artists=featured)

@app.route('/artist/<artist_slug>')
def artist_profile(artist_slug):
    """Individual artist profile page (slug or case-insensitive name)"""
    artists_data = load_json_data('artists.json', {'artists': []})
    artist = None
    
    for a in artists_data.get('artists', []):
        slug = (a.get('slug') or a.get('name', '').lower().replace(' ', '-'))
        if slug == artist_slug or a.get('name', '').lower() == artist_slug.replace('-', ' ').lower():
            artist = a
            break
    
    if not artist:
        return render_template('404.html'), 404
    
    # Get user's follow status if logged in
    is_following = False
    user_id = resolve_db_user_id()
    if user_id and artist:
        artist_id = artist.get('slug') or artist.get('id') or artist.get('name')
        try:
            with get_session() as db_session:
                follow = db_session.query(UserArtistFollow).filter(
                    UserArtistFollow.user_id == user_id,
                    UserArtistFollow.artist_id == str(artist_id)
                ).first()
                is_following = follow is not None
        except Exception:
            pass
    
    return render_template('artist_detail.html', artist=artist, is_following=is_following)

@app.route('/my-saves')
def my_saves():
    """Legacy route: redirect to Bookmarks"""
    from flask import redirect
    return redirect('/bookmarks', code=302)

@app.route("/bookmarks")
def bookmarks_page():
    """Server-rendered bookmarks page (uses Flask + file store for logged-in users)"""
    # If logged in, read server-side bookmarks so page renders on first paint.
    uid = None
    if current_user.is_authenticated:
        uid = f"user:{current_user.id}"
    items = []
    if uid:
        from pathlib import Path
        import json
        data_path = Path("data/bookmarks.json")
        if data_path.exists():
            data = json.loads(data_path.read_text(encoding="utf-8"))
            items = list(data.get("users", {}).get(uid, {}).get("items", {}).values())
    return render_template("bookmarks.html", items=items)

@app.route('/playlists')
def playlists_index():
    """List user playlists"""
    from storage import read_json
    data = read_json("data/playlists.json", {"playlists": []})
    # Optionally filter by current_user
    playlists = data["playlists"]
    if current_user.is_authenticated:
        playlists = [p for p in playlists if p.get("owner") == str(current_user.id)]
    return render_template("playlists.html", playlists=playlists)

# API Endpoints
@app.route('/api/now-playing')
@limiter.exempt
def api_now_playing():
    """Get curated now playing feed with 30s previews - randomized on each request"""
    # Use cached data (cache_duration=60 for more frequent updates)
    music_data = load_json_data('music.json', {'tracks': []}, cache_duration=60)
    shows_data = load_json_data('shows.json', {'shows': []}, cache_duration=60)
    
    # Combine and curate content for discovery feed
    feed_items = []
    
    # Get all available tracks and shows
    all_tracks = music_data.get('tracks', [])
    all_shows = shows_data.get('shows', [])
    
    # Filter for content with preview URLs
    tracks_with_preview = [t for t in all_tracks if t.get('preview_url')]
    shows_with_preview = [s for s in all_shows if s.get('trailer_url')]
    
    # Randomly select tracks (up to 8)
    selected_tracks = random.sample(tracks_with_preview, min(len(tracks_with_preview), 8))
    for track in selected_tracks:
        feed_items.append({
            'id': track['id'],
            'type': 'music',
            'title': track['title'],
            'artist': track['artist'],
            'preview_url': track['preview_url'],
            'cover_art': track['cover_art'],
            'duration': 30,  # Preview length
            'full_url': track['audio_url'],
            'duration_seconds': track.get('duration_seconds', 180),
            'description': track.get('description', ''),
            'genre': track.get('genre', '')
        })
    
    # Randomly select shows (up to 5)
    selected_shows = random.sample(shows_with_preview, min(len(shows_with_preview), 5))
    for show in selected_shows:
        feed_items.append({
            'id': show['id'],
            'type': 'show',
            'title': show['title'],
            'artist': show.get('host', 'Ahoy Indie Media'),
            'preview_url': show['trailer_url'],
            'cover_art': show['thumbnail'],
            'duration': 30,
            'full_url': show['video_url'],
            'duration_seconds': show.get('duration_seconds', 300),
            'description': show.get('description', ''),
            'genre': show.get('genre', '')
        })
    
    # Shuffle for discovery - this will be different on each request
    random.shuffle(feed_items)
    
    # Limit to 12 items for better performance
    feed_items = feed_items[:12]
    
    response = jsonify({'feed': feed_items})
    # Cache for 1 minute (content is randomized per request, but structure is stable)
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

    # Minimal listening hooks (optional endpoints for client player)
    @app.post('/api/listening/start')
    def api_listening_start():
        try:
            data = request.get_json(silent=True) or {}
            media_type = (data.get('media_type') or '').strip() or 'track'
            media_id = (data.get('media_id') or '').strip()
            source = (data.get('source') or 'manual').strip()
            uid = resolve_db_user_id()
            if not uid:
                return jsonify({'error': 'not_authenticated'}), 401
            sid = listening_start_session(uid, media_type, media_id, source)
            return jsonify({'session_id': sid})
        except Exception as e:
            return jsonify({'error': 'failed', 'detail': str(e)}), 400

    @app.post('/api/listening/end')
    def api_listening_end():
        try:
            data = request.get_json(silent=True) or {}
            sid = (data.get('session_id') or '').strip()
            if not sid:
                return jsonify({'error': 'missing_session_id'}), 400
            seconds = listening_end_session(sid)
            return jsonify({'seconds': int(seconds or 0)})
        except Exception as e:
            return jsonify({'error': 'failed', 'detail': str(e)}), 400

@app.route('/api/products')
@limiter.exempt
def api_products():
    """Get products data (subscriptions, themes, limits)"""
    from storage import read_json
    products = read_json('data/products.json', {})
    return jsonify(products)

# Weather API cache to prevent duplicate requests and timeouts
_weather_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': timedelta(minutes=10)  # Cache for 10 minutes
}

@app.route('/api/weather')
def api_weather():
    """Get weather information for New Haven, CT with caching"""
    import requests
    from datetime import datetime
    
    # New Haven, CT coordinates
    lat = request.args.get('lat', '41.3083')
    lon = request.args.get('lon', '-72.9279')
    
    # Check cache first
    now = datetime.now()
    if (_weather_cache['data'] is not None and 
        _weather_cache['timestamp'] is not None and
        now - _weather_cache['timestamp'] < _weather_cache['cache_duration']):
        # Return cached data
        cached = _weather_cache['data'].copy()
        cached['cached'] = True
        return jsonify(cached)
    
    try:
        # Use wttr.in API for free weather data (no API key required)
        # Format: ?format=j1 returns JSON
        # Reduced timeout to fail faster and prevent blocking
        url = f"https://wttr.in/New+Haven,CT?format=j1"
        
        response = requests.get(url, timeout=3, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AhoyWeather/1.0)'
        })
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract current weather data
            current = data.get('current_condition', [{}])[0]
            # Get temp_F - wttr.in returns it as a string
            # Make sure we're using temp_F, not FeelsLikeF
            temp_f = current.get('temp_F')
            if not temp_f:
                temp_f = '--'
            condition = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
            weather_code = str(current.get('weatherCode', '113'))  # Ensure it's a string
            
            # Map weather codes to emojis (wttr.in uses WMO codes)
            icon_map = {
                '113': '☀️',  # Clear/Sunny
                '116': '⛅',  # Partly cloudy
                '119': '☁️',  # Cloudy
                '122': '☁️',  # Overcast
                '143': '🌫️',  # Mist
                '176': '🌦️',  # Patchy rain
                '179': '🌨️',  # Patchy snow
                '182': '🌨️',  # Patchy sleet
                '185': '🌨️',  # Patchy freezing drizzle
                '200': '⛈️',  # Thundery outbreaks
                '227': '🌨️',  # Blowing snow
                '230': '🌨️',  # Blizzard
                '248': '🌫️',  # Fog
                '260': '🌫️',  # Freezing fog
                '263': '🌦️',  # Patchy light drizzle
                '266': '🌦️',  # Light drizzle
                '281': '🌨️',  # Freezing drizzle
                '284': '🌨️',  # Heavy freezing drizzle
                '293': '🌦️',  # Patchy light rain
                '296': '🌦️',  # Light rain
                '299': '🌧️',  # Moderate rain
                '302': '🌧️',  # Heavy rain
                '305': '🌧️',  # Heavy rain
                '308': '🌧️',  # Heavy rain
                '311': '🌨️',  # Light freezing rain
                '314': '🌨️',  # Moderate or heavy freezing rain
                '317': '🌨️',  # Light sleet
                '320': '🌨️',  # Moderate or heavy sleet
                '323': '🌨️',  # Patchy light snow
                '326': '🌨️',  # Patchy moderate snow
                '329': '🌨️',  # Patchy heavy snow
                '332': '🌨️',  # Moderate snow
                '335': '🌨️',  # Patchy heavy snow
                '338': '🌨️',  # Heavy snow
                '350': '🌨️',  # Ice pellets
                '353': '🌦️',  # Light rain shower
                '356': '🌧️',  # Moderate or heavy rain shower
                '359': '🌧️',  # Torrential rain shower
                '362': '🌨️',  # Light sleet showers
                '365': '🌨️',  # Moderate or heavy sleet showers
                '368': '🌨️',  # Light snow showers
                '371': '🌨️',  # Moderate or heavy snow showers
                '374': '🌨️',  # Light showers of ice pellets
                '377': '🌨️',  # Moderate or heavy showers of ice pellets
                '386': '⛈️',  # Patchy light rain with thunder
                '389': '⛈️',  # Moderate or heavy rain with thunder
                '392': '⛈️',  # Patchy light snow with thunder
                '395': '⛈️',  # Moderate or heavy snow with thunder
            }
            
            icon = icon_map.get(weather_code, '☀️')
            
            # Convert temperature to integer if possible
            # Handle string temperature from API
            try:
                if temp_f and temp_f != '--':
                    # Remove any whitespace and convert
                    temp_clean = str(temp_f).strip()
                    temp_int = int(temp_clean)
                else:
                    temp_int = '--'
            except (ValueError, TypeError) as e:
                # If parsing fails, try to get it from the raw response
                print(f"Temperature parsing error: {e}, raw value: {temp_f}")
                temp_int = '--'
            
            result = {
                'temperature': temp_int,
                'condition': condition.lower().replace(' ', '_'),
                'description': condition,
                'icon': icon,
                'location': 'New Haven, CT',
                'timestamp': datetime.now().isoformat(),
                'cached': False
            }
            
            # Update cache
            _weather_cache['data'] = result.copy()
            _weather_cache['timestamp'] = now
            
            return jsonify(result)
    except Exception as e:
        # Fallback to cached data if available, otherwise return default
        if _weather_cache['data'] is not None:
            cached = _weather_cache['data'].copy()
            cached['cached'] = True
            cached['error'] = 'Using cached data due to API error'
            return jsonify(cached)
        
        # Fallback to a default if API fails and no cache
        print(f"Weather API error: {e}")
        return jsonify({
            'temperature': '--',
            'condition': 'unknown',
            'description': 'Weather unavailable',
            'icon': '☀️',
            'location': 'New Haven, CT',
            'timestamp': datetime.now().isoformat(),
            'cached': False
        })

@app.route('/api/agenda')
def api_agenda():
    """Get agenda data for the current day"""
    from datetime import datetime, timedelta
    import random
    
    today = datetime.now()
    
    # Mock agenda items
    agenda_items = [
        {
            'id': 1,
            'time': '09:00',
            'title': 'Morning Music Discovery',
            'description': 'Explore new indie tracks',
            'type': 'music',
            'priority': 'high'
        },
        {
            'id': 2,
            'time': '14:00',
            'title': 'Live Show: Indie Spotlight',
            'description': 'Watch today\'s featured performance',
            'type': 'show',
            'priority': 'medium'
        },
        {
            'id': 3,
            'time': '19:00',
            'title': 'Evening Playlist',
            'description': 'Wind down with curated tracks',
            'type': 'music',
            'priority': 'low'
        }
    ]
    
    # Add some random events
    random_events = [
        {'time': '11:30', 'title': 'Artist Interview', 'description': 'Exclusive artist chat', 'type': 'show'},
        {'time': '16:00', 'title': 'New Release Alert', 'description': 'Fresh tracks just dropped', 'type': 'music'},
        {'time': '20:30', 'title': 'Community Chat', 'description': 'Connect with other fans', 'type': 'community'}
    ]
    
    # Add 1-2 random events
    selected_events = random.sample(random_events, random.randint(1, 2))
    agenda_items.extend(selected_events)
    
    # Sort by time
    agenda_items.sort(key=lambda x: x['time'])
    
    return jsonify({
        'date': today.strftime('%A, %B %d, %Y'),
        'day_of_week': today.strftime('%A'),
        'items': agenda_items
    })

@app.route('/api/user/homepage-layout', methods=['GET', 'POST'])
def api_homepage_layout():
    """Get or save user's custom homepage layout"""
    if request.method == 'GET':
        # Return default layout for now
        default_layout = {
            'widgets': [
                {'id': 'weather', 'position': 0, 'enabled': True},
                {'id': 'agenda', 'position': 1, 'enabled': True},
                {'id': 'featured', 'position': 2, 'enabled': True},
                {'id': 'now_playing', 'position': 3, 'enabled': True},
                {'id': 'quick_actions', 'position': 4, 'enabled': True},
                {'id': 'recent_activity', 'position': 5, 'enabled': True}
            ]
        }
        return jsonify(default_layout)
    
    elif request.method == 'POST':
        # Save user's layout (in a real app, save to database)
        layout_data = request.get_json()
        # For demo, just return success
        return jsonify({'success': True, 'message': 'Layout saved successfully'})

@app.route('/api/music')
@limiter.exempt
def api_music():
    """Get all music data"""
    return _cached_json_response("music.json", {"tracks": []}, max_age_seconds=300)

@app.route('/radio')
def radio_page():
    """Ahoy Radio - continuous play from all music."""
    return render_template('radio.html')

# @app.route('/merch')
def merch_page():
    """Ahoy Merch Store"""
    return render_template('merch.html')

@app.route('/api/shows')
@limiter.exempt
def api_shows():
    """Get all shows/video content"""
    return _cached_json_response("shows.json", {"shows": []}, max_age_seconds=300)

@app.route('/api/live-tv/channels')
@limiter.exempt
def api_live_tv_channels():
    """Return four Live TV channels built from available media content."""
    shows_data = load_json_data('shows.json', {'shows': []})
    # Note: Response caching added below after processing

    def normalize_show(item):
        # Map show to a unified structure
        return {
            'id': item.get('id'),
            'title': item.get('title'),
            'type': 'show',  # treated as video for player behavior
            'video_url': item.get('video_url') or item.get('mp4_link') or item.get('trailer_url'),
            'thumbnail': item.get('thumbnail'),
            'duration_seconds': item.get('duration_seconds') or 0,
            'description': item.get('description') or '',
            'category': (item.get('category') or '').lower(),
            'tags': item.get('tags') or [],
        }

    shows = [normalize_show(s) for s in shows_data.get('shows', []) if s.get('video_url') or s.get('mp4_link') or s.get('trailer_url')]

    # Channel categorization
    music_videos = [s for s in shows if (s.get('category') == 'music video' or 'music-video' in s.get('tags', []) or 'musicvideos' in ' '.join(s.get('tags', [])))]
    films = [s for s in shows if (s.get('category') == 'short film' or s.get('category') == 'film' or 'short-film' in s.get('tags', []))]
    live_shows = [s for s in shows if (s.get('category') == 'broadcast' or 'live' in ' '.join(s.get('tags', [])) or 'episode' in s.get('category', ''))]

    # Misc: everything not already in the other channels (video only)
    included_ids = {s['id'] for s in music_videos + films + live_shows}
    misc_videos = [s for s in shows if s['id'] not in included_ids]
    misc = misc_videos
    
    # Daily-seeded shuffle so the mix changes every day but stays stable within the day
    def daily_shuffle(items, salt=''):
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        seed_src = f'{today}:{salt}'
        seed = int(hashlib.sha1(seed_src.encode('utf-8')).hexdigest()[:8], 16)
        rnd = random.Random(seed)
        items_copy = [i for i in items]
        rnd.shuffle(items_copy)
        return items_copy

    channels = [
        {
            'id': 'misc',
            'name': 'Misc',
            'items': daily_shuffle(misc, 'misc'),
        },
        {
            'id': 'music-videos',
            'name': 'Music Videos',
            'items': daily_shuffle(music_videos, 'music'),
        },
        {
            'id': 'films',
            'name': 'Films',
            'items': daily_shuffle(films, 'films'),
        },
        {
            'id': 'live-shows',
            'name': 'Live Shows',
            'items': daily_shuffle(live_shows, 'live'),
        },
    ]

    response = jsonify({'channels': channels})
    # Cache for 5 minutes (content changes daily but structure is stable)
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response

@app.route('/api/show/<show_id>')
def api_show(show_id):
    """Get individual show by ID"""
    shows_data = load_json_data('shows.json', {'shows': []})
    show = next((s for s in shows_data.get('shows', []) if s.get('id') == show_id), None)
    
    if not show:
        return jsonify({'error': 'Show not found'}), 404
    
    return jsonify(show)

@app.route('/api/artists')
@limiter.exempt
def api_artists():
    """Get artists directory"""
    return _cached_json_response("artists.json", {"artists": []}, max_age_seconds=300)

@app.route('/api/artists/featured')
@limiter.exempt
def api_featured_artists():
    """Get featured artists"""
    # Same backing file as /api/artists, so allow client caching too
    etag = _etag_for_static_json("artists.json")
    inm = request.headers.get("If-None-Match")
    if etag and inm == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "public, max-age=300"
        resp.headers["Vary"] = "Accept-Encoding"
        return resp

    artists_data = load_json_data('artists.json', {'artists': []})
    featured = [a for a in artists_data.get('artists', []) if a.get('featured', False)]
    resp = jsonify({'artists': featured})
    resp.headers["Cache-Control"] = "public, max-age=300"
    resp.headers["Vary"] = "Accept-Encoding"
    if etag:
        resp.headers["ETag"] = etag
    return resp

@app.route('/artists/<artist_id>/follow', methods=['POST'])
def follow_artist(artist_id):
    """Follow or unfollow an artist"""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Normalize artist_id (could be slug, id, or name)
    artists_data = load_json_data('artists.json', {'artists': []})
    artist = None
    for a in artists_data.get('artists', []):
        a_slug = _slugify(a.get('slug') or a.get('name', ''))
        a_id = str(a.get('id') or '')
        a_name = (a.get('name') or '').strip().lower()
        artist_id_normalized = _slugify(artist_id)
        
        if (a_slug == artist_id_normalized or 
            a_id == artist_id or 
            a_name == artist_id.strip().lower()):
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Use slug, id, or name as the artist identifier
    artist_identifier = artist.get('slug') or artist.get('id') or artist.get('name')
    
    try:
        with get_session() as db_session:
            # Check if already following
            existing = db_session.query(UserArtistFollow).filter(
                UserArtistFollow.user_id == user_id,
                UserArtistFollow.artist_id == str(artist_identifier)
            ).first()
            
            if existing:
                # Unfollow
                db_session.delete(existing)
                db_session.commit()
                return jsonify({'following': False, 'message': 'Unfollowed artist'}), 200
            else:
                # Follow
                follow = UserArtistFollow(
                    user_id=user_id,
                    artist_id=str(artist_identifier)
                )
                db_session.add(follow)
                db_session.commit()
                return jsonify({'following': True, 'message': 'Following artist'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performances')
def api_performances():
    """Get performances data"""
    # For now, return shows data as performances
    shows_data = load_json_data('shows.json', {'shows': []})
    performances = []
    
    for show in shows_data.get('shows', []):
        # Convert shows to performances format
        performance = {
            'id': show.get('id'),
            'title': show.get('title'),
            'artist': show.get('host') or show.get('artist'),
            'venue': show.get('venue', 'Unknown Venue'),
            'date': show.get('published_date'),
            'thumbnail': show.get('thumbnail'),
            'video_url': show.get('video_url') or show.get('mp4_link'),
            'description': show.get('description'),
            'category': show.get('category', 'concert'),
            'duration': show.get('duration_seconds', 0),
            'featured': show.get('featured', False)
        }
        performances.append(performance)
    
    return jsonify({'performances': performances})

@app.route('/api/artist/<artist_name>')
def api_artist_profile(artist_name):
    """Get specific artist data"""
    artists_data = load_json_data('artists.json', {'artists': []})
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})

    # Normalize
    try:
        slug_from_param = _slugify(artist_name)
    except Exception:
        slug_from_param = (artist_name or '').strip().lower()

    # Find artist by slug or name (case-insensitive)
    artist = None
    for a in artists_data.get('artists', []):
        a_slug = _slugify(a.get('slug') or a.get('name', ''))
        if a_slug == slug_from_param or (a.get('name', '').strip().lower() == artist_name.strip().lower()):
            artist = a
            break

    if not artist:
        return jsonify({'error': 'Artist not found'}), 404

    artist_slug = _slugify(artist.get('slug') or artist.get('name', ''))
    artist_name_lc = (artist.get('name', '') or '').strip().lower()

    # Collect tracks: by slug, by name, or by tag match
    artist_tracks = []
    for t in music_data.get('tracks', []):
        t_slug = (t.get('artist_slug') or '').strip().lower()
        t_name = (t.get('artist') or '').strip().lower()
        tags = [str(x).strip().lower() for x in (t.get('tags') or [])]
        if t_slug == artist_slug or t_name == artist_name_lc or artist_slug in tags:
            artist_tracks.append(t)

    # Collect shows: by host_slug, by host name, or tag
    artist_shows = []
    for s in shows_data.get('shows', []):
        h_slug = (s.get('host_slug') or '').strip().lower()
        h_name = (s.get('host') or '').strip().lower()
        tags = [str(x).strip().lower() for x in (s.get('tags') or [])]
        if h_slug == artist_slug or h_name == artist_name_lc or artist_slug in tags:
            artist_shows.append(s)

    return jsonify({'artist': artist, 'tracks': artist_tracks, 'shows': artist_shows})

@app.route('/api/artists/<int:artist_id>/music')
def api_artist_music(artist_id):
    """Get artist's music tracks"""
    music_data = load_json_data('music.json', {'tracks': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    # Find artist by ID
    artist = None
    for a in artists_data.get('artists', []):
        if a.get('id') == artist_id:
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Get artist's tracks
    artist_tracks = [t for t in music_data.get('tracks', []) if t.get('artist_id') == artist_id or t.get('artist') == artist.get('name')]
    
    return jsonify(artist_tracks)

@app.route('/api/artists/<int:artist_id>/shows')
def api_artist_shows(artist_id):
    """Get artist's shows"""
    shows_data = load_json_data('shows.json', {'shows': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    # Find artist by ID
    artist = None
    for a in artists_data.get('artists', []):
        if a.get('id') == artist_id:
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Get artist's shows
    artist_shows = [s for s in shows_data.get('shows', []) if s.get('host_id') == artist_id or s.get('host') == artist.get('name')]
    
    return jsonify(artist_shows)

@app.route('/api/daily-playlist')
def api_daily_playlist():
    """Generate seeded daily playlist"""
    music_data = load_json_data('music.json', {'tracks': []})
    
    # Get today's seed
    today_str = datetime.now().strftime('%Y%m%d')
    seed = int(today_str)
    random.seed(seed)
    
    tracks = music_data.get('tracks', [])
    if not tracks:
        return jsonify({'playlist': [], 'message': 'No tracks available'})
    
    # Create playlist aiming for ~1 hour
    shuffled_tracks = random.sample(tracks, min(len(tracks), 20))
    playlist = []
    total_duration = 0
    
    for track in shuffled_tracks:
        duration = track.get('duration_seconds', 180)
        if total_duration < 3600 or len(playlist) == 0:
            playlist.append(track)
            total_duration += duration
        else:
            break
    
    return jsonify({
        'playlist': playlist,
        'total_duration': total_duration,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'seed': seed
    })

# Removed duplicate search route - using comprehensive_search instead

# Legacy playlist endpoints - redirect to new enhanced system
@app.route('/api/user/playlists', methods=['GET', 'POST'])
@login_required
def user_playlists():
    """Legacy playlist endpoint - redirects to new system"""
    return manage_playlists()

@app.route('/api/user/playlists/<playlist_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_playlist_legacy(playlist_id):
    """Legacy playlist management - redirects to new system"""
    return manage_playlist(playlist_id)

@app.route('/api/user/playlists/<playlist_id>/items', methods=['POST', 'DELETE'])
@login_required
def manage_playlist_items(playlist_id):
    """Legacy playlist items - redirects to new system"""
    if request.method == 'POST':
        return add_to_playlist(playlist_id)
    else:
        return remove_from_playlist(playlist_id)

# Removed: /api/user/playlists/<playlist_id>/reorder - always returned error, feature not supported


# Removed: /api/user/likes - use bookmarks instead (not part of MVP)
# Removed: /api/user/history - use blueprints/activity.py instead  
# Removed: /api/user/recommendations - not part of MVP

# Auth routes moved to blueprints/api/auth.py (database-based, Flask sessions)

@app.route('/api/user/profile')
@login_required
def user_profile():
    """Get user profile"""
    return jsonify(session.get('user_data', {}).get('profile', {}))

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """Update user profile - uses database"""
    from db import get_session
    from models import User
    data = request.json
    
    with get_session() as db_session:
        user = db_session.get(User, current_user.id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        if 'preferences' in data:
            user.preferences = {**user.preferences, **data['preferences']}
        
        db_session.commit()
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name,
                'avatar_url': user.avatar_url
            }
        })

@app.route('/api/user/stats')
@login_required
def get_user_stats():
    """Get user statistics - uses database"""
    from db import get_session
    from models import User, Playlist, Bookmark, PlayHistory
    from sqlalchemy import func
    
    with get_session() as db_session:
        user = db_session.get(User, current_user.id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        stats = {
            'playlists_count': db_session.query(func.count(Playlist.id)).filter(Playlist.user_id == user.id).scalar() or 0,
            'bookmarks_count': db_session.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user.id).scalar() or 0,
            'play_history_count': db_session.query(func.count(PlayHistory.id)).filter(PlayHistory.user_id == user.id).scalar() or 0,
        }
        return jsonify(stats)

# Note: Saves/bookmarks are handled by blueprints/bookmarks.py
# These legacy routes are removed - use /api/bookmarks instead

# Note: Likes/recently-played features removed - not part of MVP
# Use bookmarks and play history instead

# Note: Playlists are handled by blueprints/playlists.py
# These legacy routes are removed - use /api/playlists instead

@app.route('/api/guest-data', methods=['GET'])
def get_guest_data():
    """Get current guest data for migration"""
    if 'username' in session:
        return jsonify({'error': 'User is logged in'}), 400
    
    guest_data = {
        'saves': session.get('guest_saves', []),
        'playlists': session.get('guest_playlists', []),
        'likes': session.get('guest_likes', [])
    }
    
    return jsonify(guest_data)

# Removed: /api/user/favorites - was calling non-existent functions (like_content, get_liked_content)
# Use bookmarks API instead: /api/bookmarks

# Policy Routes
@app.route('/privacy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@app.route('/security')
def security_policy():
    """Security Policy page"""
    return render_template('security.html')

@app.route('/terms')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms.html')

# Debug Routes
@app.route('/debug')
def debug_page():
    """Debug console page with DB health info"""
    # Default values
    db_ok = False
    db_error = None
    db_dsn_summary = None
    db_env_missing = False
    db_counts = {
        'users': 0,
        'playlists': 0,
        'bookmarks': 0,
        'play_history': 0,
        'feedback': 0,
    }

    try:
        # Lazy imports to avoid hard dependency for non-DB flows
        from db import get_session, current_db_dsn_summary
        from sqlalchemy import text

        with get_session() as session:
            # Basic liveness
            session.execute(text('SELECT 1'))
            db_ok = True
            db_dsn_summary = current_db_dsn_summary()

            # Counts per table
            for table, query in [
                ('users', 'SELECT COUNT(*) FROM users'),
                ('playlists', 'SELECT COUNT(*) FROM playlists'),
                ('bookmarks', 'SELECT COUNT(*) FROM bookmarks'),
                ('play_history', 'SELECT COUNT(*) FROM play_history'),
                ('feedback', 'SELECT COUNT(*) FROM feedback'),
            ]:
                try:
                    result = session.execute(text(query)).scalar() or 0
                    db_counts[table] = int(result)
                except Exception:
                    # Table might not exist yet
                    db_counts[table] = 0
    except Exception as e:
        db_error = str(e)
        # Identify missing env var to show Render mapping help
        if "DATABASE_URL is not set" in db_error:
            db_env_missing = True

    return render_template('debug.html', db_ok=db_ok, db_error=db_error, db_counts=db_counts, db_dsn_summary=db_dsn_summary, db_env_missing=db_env_missing)

@app.route('/debug_hero')
def debug_hero():
    """Debug hero carousel page"""
    return send_from_directory('.', 'debug_hero.html')

@app.route('/api/debug/logs')
def get_debug_logs():
    """Get debug logs"""
    # In a real app, you'd read from log files
    # For now, return some sample logs
    logs = [
        {
            'id': 1,
            'timestamp': '10:30:15',
            'level': 'info',
            'source': 'Server',
            'message': 'Server started successfully',
            'details': None
        },
        {
            'id': 2,
            'timestamp': '10:30:20',
            'level': 'error',
            'source': 'API',
            'message': 'Save operation failed',
            'details': 'Mock error for testing - This is not a real error'
        },
        {
            'id': 3,
            'timestamp': '10:30:25',
            'level': 'warning',
            'source': 'Database',
            'message': 'Session expired',
            'details': 'User session expired after 30 minutes of inactivity'
        }
    ]
    return jsonify({'logs': logs})

@app.route('/api/debug/users')
def get_debug_users():
    """Get user details for debug - uses database"""
    from db import get_session
    from models import User
    try:
        with get_session() as db_session:
            users = db_session.query(User).all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'email': user.email,
                    'display_name': user.display_name,
                    'created_at': user.created_at.isoformat() if user.created_at else '',
                    'last_active_at': user.last_active_at.isoformat() if user.last_active_at else '',
                    'is_admin': user.is_admin,
                    'disabled': user.disabled
                })
            
            # Sort by creation date (newest first)
            user_list.sort(key=lambda x: x['created_at'], reverse=True)
            
            return jsonify({
                'total_users': len(user_list),
                'users': user_list
            })
    except Exception as e:
        return jsonify({'users': [], 'error': str(e)})

@app.route('/api/debug/test-save', methods=['POST'])
def test_save():
    """Test save functionality"""
    try:
        data = request.json
        content_type = data.get('type', 'track')
        content_id = data.get('id', 'test_id')
        content_data = data.get('data', {})
        
        # Test the save functionality
        username = current_user.id if current_user.is_authenticated else None
        
        if not username:
            # Test guest save
            if 'guest_saves' not in session:
                session['guest_saves'] = []
            
            session['guest_saves'].append({
                'type': content_type,
                'id': content_id,
                'data': content_data,
                'saved_at': datetime.now().isoformat()
            })
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Guest save test successful',
                'guest': True
            })
        else:
            # Test user save - use bookmarks API instead
            from blueprints.bookmarks import bp as bookmarks_bp
            # Note: This test route is deprecated - use /api/bookmarks directly
            return jsonify({
                'success': True,
                'message': 'Use /api/bookmarks endpoint for saving content',
                'guest': False
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Save test failed with error'
        }), 500

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def find_available_port(start_port=5001, end_port=5020):
    """Find an available port between start_port and end_port"""
    import socket
    for port in range(start_port, end_port + 1):
        try:
            # Try to bind to the port on all interfaces (0.0.0.0) to match gunicorn behavior
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue
    return None

@app.route('/api/debug/sample-accounts')
def debug_sample_accounts():
    """Get sample accounts for testing"""
    sample_accounts = [
        {
            'username': 'musiclover',
            'password': 'music123',
            'display_name': 'Music Lover',
            'email': 'musiclover@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 45,
                'saved_shows': 12,
                'liked_content': 78,
                'playlists': 8
            }
        },
        {
            'username': 'indieexplorer',
            'password': 'indie123',
            'display_name': 'Indie Explorer',
            'email': 'indie@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 23,
                'saved_shows': 18,
                'liked_content': 56,
                'playlists': 5
            }
        },
        {
            'username': 'showbinger',
            'password': 'shows123',
            'display_name': 'Show Binger',
            'email': 'shows@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 12,
                'saved_shows': 35,
                'liked_content': 42,
                'playlists': 3
            }
        },
        {
            'username': 'newuser',
            'password': 'new123',
            'display_name': 'New User',
            'email': 'new@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 0,
                'saved_shows': 0,
                'liked_content': 0,
                'playlists': 0
            }
        }
    ]
    
    return jsonify({'accounts': sample_accounts})

@app.route('/api/debug/data/<data_type>')
def debug_data_viewer(data_type):
    """View application data for debugging"""
    if data_type == 'users':
        from db import get_session
        from models import User
        with get_session() as db_session:
            users = db_session.query(User).all()
            return jsonify([{
                'id': u.id,
                'email': u.email,
                'display_name': u.display_name,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in users])
    elif data_type == 'music':
        music_data = load_json_data('music.json', {'tracks': []})
        return jsonify(music_data)
    elif data_type == 'shows':
        shows_data = load_json_data('shows.json', {'shows': []})
        return jsonify(shows_data)
    elif data_type == 'artists':
        artists_data = load_json_data('artists.json', {'artists': []})
        return jsonify(artists_data)
    else:
        return jsonify({'error': 'Unknown data type'}), 400

@app.route('/api/debug/status')
def debug_system_status():
    """Get system status for debugging"""
    import os

    from db import get_session
    from models import User
    from sqlalchemy import func
    
    with get_session() as db_session:
        user_count = db_session.query(func.count(User.id)).scalar() or 0
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'app': {
            'users_count': user_count,
            'session_count': len(session),
            'cache_status': 'active'
        },
        'data_files': {
            'users_file': os.path.exists('data/users.json'),
            'music_file': os.path.exists('static/data/music.json'),
            'shows_file': os.path.exists('static/data/shows.json'),
            'artists_file': os.path.exists('static/data/artists.json')
        }
    }

    return jsonify(status)

@app.route('/search')
def search_page():
    """Search results page"""
    return render_template('search.html')

@app.route('/auth')
def auth_page():
    """Authentication page"""
    return render_template('auth.html')

@app.route('/account')
def account_page():
    """User account/profile page"""
    return render_template('account.html')

@app.route('/dashboard')
def dashboard_page():
    """Dashboard page with user collection and quests"""
    # Keep legacy dashboard sidebars/layout available on /dashboard only.
    return render_template('dashboard.html', show_dashboard_sidebars=True)

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.route('/sitemap')
def sitemap_page():
    """Sitemap and app structure documentation page"""
    response = make_response(render_template('sitemap.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/sitemap.xml')
def sitemap_xml():
    """XML sitemap for search engines"""
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots_txt():
    """Robots.txt for search engines"""
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@app.route('/cast')
def cast_page():
    """Casting instructions and sender setup page"""
    return render_template('cast.html')

@app.route('/admin')
@admin_required
def admin_page():
    """Admin page for user management"""
    
    return render_template('admin.html')

@app.route('/feedback')
def feedback_page():
    """Feedback form page"""
    return render_template('feedback.html')

@app.route('/contact')
def contact_page():
    """Contact form page"""
    return render_template('contact.html')

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Get all users for admin management - uses database"""
    from db import get_session
    from models import User
    with get_session() as db_session:
        users = db_session.query(User).all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name,
                'created_at': user.created_at.isoformat() if user.created_at else '',
                'last_active_at': user.last_active_at.isoformat() if user.last_active_at else '',
                'is_admin': user.is_admin,
                'disabled': user.disabled
            })
        return jsonify({'users': user_list})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user - uses database"""
    from db import get_session
    from models import User
    with get_session() as db_session:
        user = db_session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow admin to delete themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        db_session.delete(user)
        db_session.commit()
        return jsonify({'success': True, 'message': f'User {user.email} deleted'})

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def admin_reset_password(user_id):
    """Reset user password - uses database"""
    from db import get_session
    from models import User
    from extensions import bcrypt
    
    data = request.json
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'Password required'}), 400
    
    with get_session() as db_session:
        user = db_session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db_session.commit()
        return jsonify({'success': True, 'message': f'Password reset for {user.email}'})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.json
        feedback_data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'username': session.get('username', 'anonymous'),
            'feedback_type': data.get('type', 'general'),
            'rating': data.get('rating', 0),
            'ui_rating': data.get('ui_rating', 0),
            'performance_rating': data.get('performance_rating', 0),
            'content_rating': data.get('content_rating', 0),
            'subject': data.get('subject', ''),
            'message': data.get('message', ''),
            'suggestions': data.get('suggestions', ''),
            'bugs': data.get('bugs', ''),
            'feature_requests': data.get('feature_requests', ''),
            'contact_email': data.get('contact_email', ''),
            'anonymous': data.get('anonymous', False),
            'status': 'new'
        }
        
        # Load existing feedback
        feedback_file = 'data/feedback.json'
        try:
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
        except FileNotFoundError:
            feedback_list = []
        
        # Add new feedback
        feedback_list.append(feedback_data)
        
        # Save feedback
        os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.route('/api/feedback', methods=['GET'])
@admin_required
def get_feedback():
    """Get feedback (admin only)"""
    
    try:
        feedback_file = 'data/feedback.json'
        with open(feedback_file, 'r') as f:
            feedback_list = json.load(f)
        
        # Sort by timestamp (newest first)
        feedback_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'feedback': feedback_list})
        
    except FileNotFoundError:
        return jsonify({'feedback': []})
    except Exception as e:
        print(f"Error loading feedback: {e}")
        return jsonify({'error': 'Failed to load feedback'}), 500

@app.route('/api/feedback/<feedback_id>/status', methods=['PUT'])
@admin_required
def update_feedback_status():
    """Update feedback status (admin only)"""
    
    try:
        data = request.json
        feedback_id = request.view_args['feedback_id']
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status required'}), 400
        
        feedback_file = 'data/feedback.json'
        with open(feedback_file, 'r') as f:
            feedback_list = json.load(f)
        
        # Find and update feedback
        for feedback in feedback_list:
            if feedback['id'] == feedback_id:
                feedback['status'] = new_status
                feedback['updated_at'] = datetime.now().isoformat()
                break
        else:
            return jsonify({'error': 'Feedback not found'}), 404
        
        # Save updated feedback
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Status updated'})
        
    except Exception as e:
        print(f"Error updating feedback status: {e}")
        return jsonify({'error': 'Failed to update status'}), 500

# Removed duplicate search route - using comprehensive_search instead

# ========================================
# 🔍 COMPREHENSIVE SEARCH API
# ========================================

@app.route('/api/search', methods=['GET'])
def comprehensive_search():
    """Comprehensive search API with TF-IDF scoring and fuzzy matching"""
    try:
        from search_indexer import search_index
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100
        offset = int(request.args.get('offset', 0))
        kinds = request.args.get('kinds', '').split(',') if request.args.get('kinds') else None
        sort = request.args.get('sort', 'relevance')
        
        # Validate sort parameter
        if sort not in ['relevance', 'recent']:
            sort = 'relevance'
        
        # Perform search
        results = search_index.search(
            query=query,
            limit=limit,
            offset=offset,
            kinds=kinds,
            sort=sort
        )
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error in comprehensive search: {e}")
        return jsonify({'error': 'Search failed', 'results': [], 'total': 0}), 500

@app.route('/api/search/reindex', methods=['POST'])
def reindex_search():
    """Reindex the search data (admin endpoint)"""
    try:
        from search_indexer import search_index
        
        data_sources = {
            'music': 'static/data/music.json',
            'shows': 'static/data/shows.json',
            'artists': 'static/data/artists.json'
        }
        
        search_index.reindex(data_sources)
        
        return jsonify({
            'success': True,
            'message': f'Search index rebuilt with {search_index.total_docs} documents'
        })
        
    except Exception as e:
        print(f"Error reindexing search: {e}")
        return jsonify({'error': 'Reindex failed'}), 500

@app.route('/api/suggest', methods=['GET'])
def search_suggestions():
    """Typeahead suggestions for search header"""
    try:
        from search_indexer import search_index
        
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 8)), 20)  # Cap at 20
        
        if not query or len(query) < 2:
            return jsonify({
                'query': query,
                'items': []
            })
        
        suggestions = []
        query_lower = query.lower()
        
        # Get all documents for suggestion building
        all_docs = list(search_index.documents.values())
        
        # 1. Matching titles (prefix-boosted)
        title_matches = []
        for doc in all_docs:
            title = doc.get('title', '')
            if title.lower().startswith(query_lower):
                title_matches.append({
                    'label': f"{title} — {doc.get('fields', {}).get('artist', doc.get('fields', {}).get('host', ''))}",
                    'kind': doc.get('kind', ''),
                    'url': doc.get('url', '#'),
                    'score': 10.0  # High score for prefix matches
                })
            elif query_lower in title.lower():
                title_matches.append({
                    'label': f"{title} — {doc.get('fields', {}).get('artist', doc.get('fields', {}).get('host', ''))}",
                    'kind': doc.get('kind', ''),
                    'url': doc.get('url', '#'),
                    'score': 5.0  # Lower score for contains matches
                })
        
        # Sort by score and add to suggestions
        title_matches.sort(key=lambda x: x['score'], reverse=True)
        suggestions.extend(title_matches[:limit//2])
        
        # 2. Top tags/genres starting with query
        tag_matches = []
        seen_tags = set()
        
        for doc in all_docs:
            # Get tags
            tags = doc.get('tags', [])
            for tag in tags:
                if tag.lower().startswith(query_lower) and tag not in seen_tags:
                    tag_matches.append({
                        'label': f"#{tag}",
                        'kind': 'tag',
                        'url': f"/search?q=tag:{tag}",
                        'score': 8.0
                    })
                    seen_tags.add(tag)
            
            # Get genres
            genres = doc.get('genres', [])
            for genre in genres:
                if genre.lower().startswith(query_lower) and genre not in seen_tags:
                    tag_matches.append({
                        'label': f"#{genre}",
                        'kind': 'genre',
                        'url': f"/search?q=genre:{genre}",
                        'score': 7.0
                    })
                    seen_tags.add(genre)
        
        # Sort and add tag matches
        tag_matches.sort(key=lambda x: x['score'], reverse=True)
        suggestions.extend(tag_matches[:limit//4])
        
        # 3. Popular artists/shows where name starts with query
        artist_matches = []
        seen_artists = set()
        
        for doc in all_docs:
            artist_name = doc.get('fields', {}).get('artist', '') or doc.get('fields', {}).get('host', '')
            if artist_name and artist_name.lower().startswith(query_lower) and artist_name not in seen_artists:
                artist_matches.append({
                    'label': f"🎤 {artist_name}",
                    'kind': 'artist',
                    'url': doc.get('url', '#'),
                    'score': 6.0
                })
                seen_artists.add(artist_name)
        
        # Sort and add artist matches
        artist_matches.sort(key=lambda x: x['score'], reverse=True)
        suggestions.extend(artist_matches[:limit//4])
        
        # Sort all suggestions by score and limit
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        suggestions = suggestions[:limit]
        
        # Add some fun suggestions for empty or short queries
        if len(query) < 3:
            fun_suggestions = [
                {'label': '🔥 Trending Now', 'kind': 'trending', 'url': '/search?q=trending', 'score': 9.0},
                {'label': '🎵 New Releases', 'kind': 'new', 'url': '/search?q=recent', 'score': 8.0},
                {'label': '⭐ Staff Picks', 'kind': 'featured', 'url': '/search?q=featured', 'score': 7.0},
                {'label': '🎧 Discover', 'kind': 'discover', 'url': '/search?q=discover', 'score': 6.0}
            ]
            suggestions = fun_suggestions[:limit]
        
        return jsonify({
            'query': query,
            'items': suggestions
        })
        
    except Exception as e:
        print(f"Error in search suggestions: {e}")
        return jsonify({
            'query': query if 'query' in locals() else '',
            'items': []
        }), 500


@app.route('/api/search/trending', methods=['GET'])
def trending_content():
    """Get trending content for discovery"""
    try:
        from search_indexer import search_index
        
        # Get recent content (simplified - using added_date if available)
        recent_docs = []
        for doc in search_index.documents.values():
            if doc.get('added_date'):
                recent_docs.append(doc)
        
        # Sort by date (most recent first)
        recent_docs.sort(key=lambda x: x.get('added_date', ''), reverse=True)
        
        # Take top 8
        trending = recent_docs[:8]
        
        # Format for frontend
        results = []
        for doc in trending:
            result = {
                'id': doc['id'],
                'kind': doc['kind'],
                'title': doc['title'],
                'url': doc['url'],
                'summary': doc['summary'],
                'tags': doc['tags'],
                'genres': doc['genres']
            }
            
            # Add type-specific fields
            if doc['kind'] == 'music':
                result['artist'] = doc['fields'].get('artist', '')
                result['album'] = doc['fields'].get('album', '')
            elif doc['kind'] == 'show':
                result['host'] = doc['fields'].get('host', '')
            elif doc['kind'] == 'artist':
                result['name'] = doc['fields'].get('name', '')
            
            results.append(result)
        
        return jsonify({
            'trending': results,
            'count': len(results)
        })
        
    except Exception as e:
        print(f"Error in trending content: {e}")
        return jsonify({'error': 'Trending failed'}), 500

# Allow `python -m app` locally if needed
if __name__ == "__main__":
    import os, socket, subprocess, shutil, sys, platform

    def _is_port_free(p: int) -> bool:
        """Check if port is free on all interfaces (0.0.0.0) to match gunicorn binding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", p))
            return True
        except OSError:
            return False

    # 1) Ensure DB migrations are applied (best-effort for local dev)
    try:
        alembic_bin = shutil.which("alembic")
        if alembic_bin:
            print("⚙️  Applying migrations (alembic upgrade heads)…")
            env = os.environ.copy()
            # Ensure PYTHONPATH includes project root so alembic/env.py can import models
            project_root = os.path.dirname(os.path.abspath(__file__))
            env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH','')}" if env.get('PYTHONPATH') else project_root
            # Provide a sane default DATABASE_URL for local runs
            env.setdefault("DATABASE_URL", "sqlite:///local.db")
            subprocess.run([alembic_bin, "upgrade", "heads"], check=True, env=env)
        else:
            print("⚠️  Alembic not found in PATH; skipping automatic migrations.")
    except Exception as e:
        print(f"⚠️  Migrations step skipped: {e}")

    # 2) Pick a free port automatically if requested is busy
    requested = int(os.getenv("PORT", "5000"))
    chosen = requested
    if not _is_port_free(requested):
        alt = find_available_port(5001, 5020)
        if alt:
            print(f"⚠️  Port {requested} busy — starting on {alt}")
            chosen = alt
        else:
            # Fallback: let OS pick an ephemeral port
            print(f"❌ Port {requested} busy and no alternates free in 5001-5020.")
            print("🔁 Falling back to PORT=0 (OS-assigned ephemeral port).")
            print("💡 Set explicit PORT env var if you prefer a fixed port, e.g. PORT=5050 python app.py")
            chosen = 0

    # 3) Local run strategy:
    # - Default to Flask dev server (more stable locally, esp. on macOS where fork() + Objective-C can crash).
    # - Allow opting into gunicorn via AHOY_USE_GUNICORN=1 for parity testing.
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    want_gunicorn = str(os.getenv("AHOY_USE_GUNICORN", "")).lower() in ("1", "true", "yes", "on")

    gunicorn_bin = shutil.which("gunicorn") if (not is_windows) else None
    if gunicorn_bin and want_gunicorn and (not is_macos):
        print(f"🚀 Starting gunicorn on port {chosen}…")
        os.execv(gunicorn_bin, ["gunicorn", "app:app", "--workers", "2", "--threads", "4", "--timeout", "120", "-b", f"0.0.0.0:{chosen}"])
    else:
        if gunicorn_bin and is_macos and not want_gunicorn:
            print("🧯 macOS detected: skipping gunicorn by default to avoid fork()/objc crashes.")
            print("   Set AHOY_USE_GUNICORN=1 if you want to run gunicorn locally anyway.")
        if is_windows:
            print(f"🚀 Starting Flask dev server on http://127.0.0.1:{chosen} (Windows detected)")
        else:
            print(f"🚀 Starting Flask dev server on http://127.0.0.1:{chosen}")
        app.run(port=chosen, use_reloader=False)

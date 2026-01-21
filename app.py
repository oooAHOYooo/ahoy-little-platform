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
from typing import Optional
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
        # Avoid Unicode symbols here (Windows console can be cp1252).
        print(f"Search index initialized with {search_index.total_docs} documents")
        
    except Exception as e:
        # Avoid Unicode symbols here (Windows console can be cp1252).
        print(f"Error initializing search index: {e}")

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


def _admin_session_required(fn):
    """Admin guard for browser/session-based admin routes (Flask-Login)."""
    from functools import wraps
    from flask import request as _request, jsonify as _jsonify, redirect as _redirect, url_for as _url_for, flash as _flash

    @wraps(fn)
    def wrapper(*args, **kwargs):
        wants_html = 'text/html' in (_request.headers.get('Accept') or '')
        if not getattr(current_user, "is_authenticated", False):
            if wants_html:
                _flash("Please log in as admin", "warning")
                return _redirect(_url_for('auth_page'))
            return _jsonify({"error": "forbidden"}), 403
        if not getattr(current_user, "is_admin", False):
            if wants_html:
                _flash("Admin access required", "danger")
                return _redirect(_url_for('home'))
            return _jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)

    return wrapper


def _bootstrap_admin_user_from_env():
    """
    Create/update an admin user from env without committing secrets.

    Set:
      - AHOY_ADMIN_EMAIL
      - AHOY_ADMIN_PASSWORD
    """
    email = (os.getenv("AHOY_ADMIN_EMAIL") or "").strip().lower()
    password = os.getenv("AHOY_ADMIN_PASSWORD") or ""
    if not email or not password:
        return
    try:
        from db import get_session
        from models import User
        from utils.security import hash_password

        with get_session() as s:
            u = s.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    email=email,
                    password_hash=hash_password(password),
                    is_admin=True,
                    display_name=email.split("@")[0],
                )
                s.add(u)
            else:
                u.password_hash = hash_password(password)
                u.is_admin = True
                if not u.display_name:
                    u.display_name = email.split("@")[0]
            s.commit()
    except Exception:
        # Never crash app startup if bootstrap fails.
        return

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
        st = (app.config.get("SESSION_TYPE") or "").lower()
        if st == "redis":
            app.logger.info("Redis sessions enabled")
        elif st == "filesystem":
            app.logger.info("Filesystem sessions enabled")
        elif st:
            app.logger.info("%s sessions enabled", st)
    else:
        print("WARN: Flask noted Flask-Session not available; using client-side cookies only. Activate venv or install Flask-Session.")
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
        _bootstrap_admin_user_from_env()

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

    # Debug endpoints for payment and checkout systems
    @app.route('/ops/debug/payments', methods=['GET'])
    def debug_payments():
        """Debug endpoint for payment system status - use this to check Stripe/wallet configuration"""
        from flask_login import current_user
        from db import get_session
        from models import User, WalletTransaction, Purchase, Tip
        import stripe
        from datetime import datetime
        
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "stripe": {},
            "database": {},
            "user": {},
            "errors": []
        }
        
        # Check Stripe configuration
        try:
            stripe_key = app.config.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
            debug_info["stripe"]["configured"] = bool(stripe_key)
            debug_info["stripe"]["key_prefix"] = stripe_key[:7] + "..." if stripe_key else None
            debug_info["stripe"]["webhook_secret_set"] = bool(app.config.get("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET_TEST"))
            
            # Test Stripe API connection
            if stripe_key:
                try:
                    stripe.api_key = stripe_key
                    # Try to list customers (lightweight operation)
                    customers = stripe.Customer.list(limit=1)
                    debug_info["stripe"]["api_connection"] = "ok"
                    debug_info["stripe"]["api_version"] = stripe.api_version if hasattr(stripe, 'api_version') else "unknown"
                except Exception as e:
                    debug_info["stripe"]["api_connection"] = "error"
                    debug_info["stripe"]["api_error"] = str(e)
                    debug_info["errors"].append(f"Stripe API error: {e}")
            else:
                debug_info["stripe"]["api_connection"] = "not_configured"
                debug_info["errors"].append("Stripe secret key not configured")
        except Exception as e:
            debug_info["stripe"]["error"] = str(e)
            debug_info["errors"].append(f"Stripe check error: {e}")
        
        # Check database connectivity and wallet tables
        try:
            with get_session() as s:
                # Check if wallet_balance column exists
                from sqlalchemy import inspect
                inspector = inspect(s.bind)
                users_columns = [col['name'] for col in inspector.get_columns('users')]
                debug_info["database"]["wallet_balance_column"] = 'wallet_balance' in users_columns
                
                # Check if wallet_transactions table exists
                tables = inspector.get_table_names()
                debug_info["database"]["wallet_transactions_table"] = 'wallet_transactions' in tables
                
                # Get counts
                user_count = s.query(User).count()
                wallet_tx_count = s.query(WalletTransaction).count() if 'wallet_transactions' in tables else 0
                purchase_count = s.query(Purchase).count()
                tip_count = s.query(Tip).count()
                
                debug_info["database"]["counts"] = {
                    "users": user_count,
                    "wallet_transactions": wallet_tx_count,
                    "purchases": purchase_count,
                    "tips": tip_count
                }
                
                # Check current user's wallet if logged in
                if current_user.is_authenticated:
                    user = s.query(User).filter(User.id == current_user.id).first()
                    if user:
                        debug_info["user"]["logged_in"] = True
                        debug_info["user"]["user_id"] = user.id
                        debug_info["user"]["wallet_balance"] = float(user.wallet_balance or 0)
                        debug_info["user"]["stripe_customer_id"] = user.stripe_customer_id or None
                        
                        # Get recent wallet transactions
                        if 'wallet_transactions' in tables:
                            recent_tx = s.query(WalletTransaction).filter(
                                WalletTransaction.user_id == user.id
                            ).order_by(WalletTransaction.created_at.desc()).limit(5).all()
                            debug_info["user"]["recent_transactions"] = [
                                {
                                    "type": tx.type,
                                    "amount": float(tx.amount),
                                    "balance_after": float(tx.balance_after),
                                    "description": tx.description,
                                    "created_at": tx.created_at.isoformat()
                                } for tx in recent_tx
                            ]
                else:
                    debug_info["user"]["logged_in"] = False
        except Exception as e:
            debug_info["database"]["error"] = str(e)
            debug_info["errors"].append(f"Database error: {e}")
        
        # Overall status
        debug_info["status"] = "ok" if len(debug_info["errors"]) == 0 else "errors"
        
        return jsonify(debug_info), 200 if debug_info["status"] == "ok" else 500

    @app.route('/ops/debug/checkout', methods=['GET'])
    def debug_checkout():
        """Debug endpoint for checkout system - checks merch catalog"""
        from storage import read_json
        from datetime import datetime
        
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "merch_catalog": {},
            "errors": []
        }
        
        # Check merch catalog
        try:
            merch_catalog = read_json("data/merch.json", {"items": []})
            if isinstance(merch_catalog, dict):
                items = merch_catalog.get("items", [])
                debug_info["merch_catalog"]["exists"] = True
                debug_info["merch_catalog"]["item_count"] = len(items) if isinstance(items, list) else 0
                debug_info["merch_catalog"]["items"] = [
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "price_usd": item.get("price_usd"),
                        "available": item.get("available", True)
                    } for item in (items[:10] if isinstance(items, list) else [])  # First 10 items
                ]
            else:
                debug_info["merch_catalog"]["exists"] = False
                debug_info["errors"].append("Merch catalog is not a valid dictionary")
        except FileNotFoundError:
            debug_info["merch_catalog"]["exists"] = False
            debug_info["errors"].append("Merch catalog file not found: data/merch.json")
        except Exception as e:
            debug_info["merch_catalog"]["error"] = str(e)
            debug_info["errors"].append(f"Error reading merch catalog: {e}")
        
        debug_info["status"] = "ok" if len(debug_info["errors"]) == 0 else "errors"
        
        return jsonify(debug_info), 200 if debug_info["status"] == "ok" else 500

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
        print("Compression enabled")
    except ImportError:
        print("WARN: Flask-Compress not available, compression disabled")

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

    # For merch, ignore client-provided amount/title and look up from merch catalog.
    if kind == "merch" and item_id:
        try:
            from storage import read_json
            merch_catalog = read_json("data/merch.json", {"items": []}) or {}
            items = merch_catalog.get("items") if isinstance(merch_catalog, dict) else []
            found = None
            if isinstance(items, list):
                for it in items:
                    if isinstance(it, dict) and str(it.get("id") or "") == str(item_id):
                        found = it
                        break
            if found:
                # Respect item availability flags if present.
                if found.get("available") is False:
                    return render_template('checkout.html',
                                           error="This item is not available.",
                                           kind=kind,
                                           item_id=item_id,
                                           qty=qty,
                                           csrf_token=generate_csrf_token()), 400
                unit = Decimal(str(found.get("price_usd") or "0")).quantize(Decimal("0.01"))
                if unit <= 0:
                    return render_template('checkout.html',
                                           error="Invalid item price.",
                                           kind=kind,
                                           item_id=item_id,
                                           qty=qty,
                                           csrf_token=generate_csrf_token()), 400
                amount = str(unit)  # unit price
                title = str(found.get("name") or "Merch")[:120]
                total = (unit * Decimal(str(max(1, qty)))).quantize(Decimal("0.01"))
            else:
                # Item not found in catalog
                current_app.logger.warning(f"Merch item not found: {item_id}")
                return render_template('checkout.html',
                                       error=f"Merch item '{item_id}' not found in catalog.",
                                       kind=kind,
                                       item_id=item_id,
                                       qty=qty,
                                       csrf_token=generate_csrf_token()), 404
        except Exception as e:
            current_app.logger.error(f"Error loading merch catalog: {e}", exc_info=True)
            return render_template('checkout.html',
                                   error="Unable to load merch catalog. Please try again later.",
                                   kind=kind,
                                   item_id=item_id,
                                   qty=qty,
                                   csrf_token=generate_csrf_token()), 500

    # Get wallet balance if user is logged in
    wallet_balance = None
    try:
        from flask_login import current_user
        if current_user.is_authenticated:
            from db import get_session
            from models import User
            with get_session() as s:
                user = s.query(User).filter(User.id == current_user.id).first()
                if user:
                    wallet_balance = float(user.wallet_balance or 0)
    except Exception:
        pass

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
        wallet_balance=wallet_balance,
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
    use_wallet = form.get('use_wallet') == 'true'
    try:
        amount = float(form.get('amount') or '0')
    except Exception:
        amount = 0.0
    try:
        total = float(form.get('total') or form.get('computed_total') or amount)
    except Exception:
        total = amount

    # Harden merch checkout: price/title must come from server-side merch catalog.
    if kind == "merch":
        try:
            from storage import read_json
            merch_catalog = read_json("data/merch.json", {"items": []}) or {}
            items = merch_catalog.get("items") if isinstance(merch_catalog, dict) else []
            found = None
            if isinstance(items, list) and item_id:
                for it in items:
                    if isinstance(it, dict) and str(it.get("id") or "") == str(item_id):
                        found = it
                        break
            if not found:
                return render_template("checkout.html",
                                       error="Invalid merch item.",
                                       csrf_token=generate_csrf_token(),
                                       kind=kind,
                                       item_id=item_id or "",
                                       qty=max(1, qty)), 400
            if found.get("available") is False:
                return render_template("checkout.html",
                                       error="This item is not available.",
                                       csrf_token=generate_csrf_token(),
                                       kind=kind,
                                       item_id=item_id or "",
                                       qty=max(1, qty)), 400

            qty = int(max(1, qty))
            unit = float(found.get("price_usd") or 0)
            if unit <= 0:
                return render_template("checkout.html",
                                       error="Invalid item price.",
                                       csrf_token=generate_csrf_token(),
                                       kind=kind,
                                       item_id=item_id or "",
                                       qty=qty), 400
            amount = float(unit)              # unit price (authoritative)
            total = float(unit * qty)         # total (authoritative)
        except Exception:
            pass

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

    # Create a Stripe Checkout Session and redirect user to Stripe-hosted checkout
    try:
        import stripe
        from decimal import Decimal
        from blueprints.payments import calculate_boost_fees

        # Configure Stripe from config/env (prefer config)
        api_key = app.config.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
        stripe.api_key = api_key
        if not stripe.api_key:
            raise RuntimeError("Stripe not configured (missing STRIPE_SECRET_KEY)")

        # Compute authoritative totals for boost/tip (ignore client-provided totals)
        metadata = {
            "purchase_id": str(purchase_id),
            "type": str(kind),
            "user_id": str(user_id or ""),
            "artist_id": str(artist_id or ""),
            "item_id": str(item_id or ""),
            "qty": str(qty),
            "amount": str(amount),
            "total": str(total),
        }

        line_items = []
        if kind in ["boost", "tip"]:
            boost_amount_decimal = Decimal(str(amount or 0)).quantize(Decimal("0.01"))
            stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue = calculate_boost_fees(boost_amount_decimal)

            # Update Purchase.total to total_charge (authoritative)
            total = float(total_charge)
            with get_session() as s:
                p = s.query(Purchase).filter(Purchase.id == int(purchase_id)).first()
                if p:
                    p.total = total
                    s.commit()

            metadata.update({
                "boost_amount": str(boost_amount_decimal),
                "stripe_fee": str(stripe_fee),
                "platform_fee": str(platform_fee),
                "total_paid": str(total_charge),
                "artist_payout": str(artist_payout),
                "platform_revenue": str(platform_revenue),
            })

            line_items = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Boost Amount",
                            "description": "100% goes directly to the artist",
                        },
                        "unit_amount": int(boost_amount_decimal * 100),
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Stripe Processing Fee",
                            "description": "2.9% + $0.30",
                        },
                        "unit_amount": int(Decimal(str(stripe_fee)) * 100),
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Ahoy Indie Media Platform Fee",
                            "description": "7.5% platform fee",
                        },
                        "unit_amount": int(Decimal(str(platform_fee)) * 100),
                    },
                    "quantity": 1,
                },
            ]
        else:
            # One-time purchases (merch/theme/subscription MVP): treat as a simple one-time payment.
            unit_amount_cents = int(max(0, float(amount or 0)) * 100)
            if unit_amount_cents <= 0:
                raise ValueError("Invalid amount")
            # For merch, always derive title from the merch catalog item when possible.
            safe_title = (request.form.get("title") or "Ahoy Purchase").strip()[:120]
            if kind == "merch" and item_id:
                try:
                    from storage import read_json
                    merch_catalog = read_json("data/merch.json", {"items": []}) or {}
                    items = merch_catalog.get("items") if isinstance(merch_catalog, dict) else []
                    if isinstance(items, list):
                        for it in items:
                            if isinstance(it, dict) and str(it.get("id") or "") == str(item_id):
                                safe_title = str(it.get("name") or safe_title).strip()[:120]
                                break
                except Exception:
                    pass
            line_items = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": safe_title},
                        "unit_amount": unit_amount_cents,
                    },
                    "quantity": int(max(1, qty)),
                }
            ]

        # Handle wallet payment if requested
        if use_wallet:
            from flask_login import current_user
            if current_user.is_authenticated:
                try:
                    from blueprints.payments import deduct_wallet_balance
                    from decimal import Decimal
                    
                    # Calculate total charge
                    if kind in ["boost", "tip"]:
                        boost_amount_decimal = Decimal(str(amount or 0)).quantize(Decimal("0.01"))
                        _, _, total_charge, _, _ = calculate_boost_fees(boost_amount_decimal)
                    else:
                        # For merch, use the total from the purchase record
                        try:
                            total_charge = Decimal(str(total)) if total else Decimal("0.00")
                        except (ValueError, TypeError):
                            # Fallback: get total from purchase record
                            with get_session() as s:
                                from models import Purchase
                                p = s.query(Purchase).filter(Purchase.id == int(purchase_id)).first()
                                if p and p.total:
                                    total_charge = Decimal(str(p.total))
                                elif amount:
                                    total_charge = Decimal(str(amount))
                                else:
                                    current_app.logger.error(f"Wallet payment: Unable to determine total for purchase {purchase_id}, kind={kind}")
                                    # Get wallet balance for error page
                                    try:
                                        from models import User
                                        with get_session() as s2:
                                            user = s2.query(User).filter(User.id == current_user.id).first()
                                            wallet_balance = float(user.wallet_balance or 0) if user else 0.0
                                    except:
                                        wallet_balance = None
                                    return render_template("checkout.html",
                                                         error="Unable to determine purchase total. Please try again.",
                                                         csrf_token=generate_csrf_token(),
                                                         kind=kind,
                                                         artist_id=artist_id or "",
                                                         amount=amount,
                                                         item_id=item_id or "",
                                                         qty=qty,
                                                         wallet_balance=wallet_balance), 400
                    
                    if total_charge <= 0:
                        current_app.logger.error(f"Wallet payment: Invalid total_charge {total_charge} for purchase {purchase_id}")
                        try:
                            from models import User
                            with get_session() as s2:
                                user = s2.query(User).filter(User.id == current_user.id).first()
                                wallet_balance = float(user.wallet_balance or 0) if user else 0.0
                        except:
                            wallet_balance = None
                        return render_template("checkout.html",
                                             error="Invalid purchase amount",
                                             csrf_token=generate_csrf_token(),
                                             kind=kind,
                                             artist_id=artist_id or "",
                                             amount=amount,
                                             item_id=item_id or "",
                                             qty=qty,
                                             wallet_balance=wallet_balance), 400
                    
                    # Try to deduct from wallet
                    success, error, balance_after = deduct_wallet_balance(
                        current_user.id,
                        total_charge,
                        f"{kind.title()} payment",
                        str(purchase_id),
                        kind
                    )
                    
                    if success:
                        # Wallet payment successful - mark purchase as paid
                        with get_session() as s:
                            from models import Purchase
                            p = s.query(Purchase).filter(Purchase.id == int(purchase_id)).first()
                            if p:
                                p.status = "paid"
                                p.stripe_id = f"wallet_{purchase_id}"
                                s.commit()
                            else:
                                current_app.logger.error(f"Wallet payment: Purchase {purchase_id} not found after wallet deduction")
                                # Wallet was deducted but purchase not found - this is bad
                                # Try to refund wallet (manual process needed)
                                try:
                                    from models import User, WalletTransaction
                                    with get_session() as s2:
                                        user = s2.query(User).filter(User.id == current_user.id).first()
                                        if user:
                                            user.wallet_balance += total_charge
                                            refund_tx = WalletTransaction(
                                                user_id=current_user.id,
                                                type="refund",
                                                amount=total_charge,
                                                balance_before=float(balance_after),
                                                balance_after=float(balance_after) + float(total_charge),
                                                description=f"Refund: Purchase {purchase_id} not found",
                                                reference_id=str(purchase_id),
                                                reference_type="purchase",
                                                created_at=datetime.utcnow(),
                                            )
                                            s2.add(refund_tx)
                                            s2.commit()
                                except Exception as refund_err:
                                    current_app.logger.error(f"Failed to refund wallet: {refund_err}")
                                
                                try:
                                    from models import User
                                    with get_session() as s2:
                                        user = s2.query(User).filter(User.id == current_user.id).first()
                                        wallet_balance = float(user.wallet_balance or 0) if user else 0.0
                                except:
                                    wallet_balance = None
                                return render_template("checkout.html",
                                                     error="Purchase record not found. Wallet has been refunded. Please try again.",
                                                     csrf_token=generate_csrf_token(),
                                                     kind=kind,
                                                     artist_id=artist_id or "",
                                                     amount=amount,
                                                     item_id=item_id or "",
                                                     qty=qty,
                                                     wallet_balance=wallet_balance), 500
                    else:
                        # Wallet payment failed - fall through to Stripe
                        current_app.logger.warning(f"Wallet payment failed for user {current_user.id}: {error}")
                        try:
                            from models import User
                            with get_session() as s2:
                                user = s2.query(User).filter(User.id == current_user.id).first()
                                wallet_balance = float(user.wallet_balance or 0) if user else 0.0
                        except:
                            wallet_balance = None
                        return render_template("checkout.html",
                                             error=error or "Insufficient wallet balance",
                                             csrf_token=generate_csrf_token(),
                                             kind=kind,
                                             artist_id=artist_id or "",
                                             amount=amount,
                                             item_id=item_id or "",
                                             qty=qty,
                                             wallet_balance=wallet_balance), 400
                except Exception as e:
                    current_app.logger.error(f"Wallet payment error for user {current_user.id if current_user.is_authenticated else 'anonymous'}: {e}", exc_info=True)
                    try:
                        from models import User
                        with get_session() as s2:
                            user = s2.query(User).filter(User.id == current_user.id).first()
                            wallet_balance = float(user.wallet_balance or 0) if user else 0.0
                    except:
                        wallet_balance = None
                    return render_template("checkout.html",
                                         error=f"Wallet payment error: {str(e)}",
                                         csrf_token=generate_csrf_token(),
                                         kind=kind,
                                         artist_id=artist_id or "",
                                         amount=amount,
                                         item_id=item_id or "",
                                         qty=qty,
                                         wallet_balance=wallet_balance), 500

        success_url = url_for("checkout_success", pid=purchase_id, _external=True)
        cancel_url = url_for("checkout_page", type=kind, artist_id=artist_id or "", amount=amount, item_id=item_id or "", qty=qty, title=request.form.get("title") or "", _external=True)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

        # Persist Stripe session id
        with get_session() as s:
            p = s.query(Purchase).filter(Purchase.id == int(purchase_id)).first()
            if p:
                p.stripe_id = checkout_session.id
                s.commit()

        return redirect(checkout_session.url)
    except Exception as e:
        # Fall back to success page with an error; keep purchase recorded for diagnostics
        return render_template("checkout.html",
                               error=f"Checkout setup failed. {str(e)}",
                               csrf_token=generate_csrf_token(),
                               kind=kind,
                               artist_id=artist_id or "",
                               amount=amount,
                               item_id=item_id or "",
                               qty=qty), 500

# Exempt checkout_process and wallet funding from Flask-WTF CSRF after route is registered
_csrf_ext = app.extensions.get('csrf')
if _csrf_ext is not None:
    _csrf_ext.exempt(checkout_process)
    # Exempt wallet funding endpoint (JSON API)
    try:
        from blueprints.payments import fund_wallet
        _csrf_ext.exempt(fund_wallet)
    except Exception as e:
        # Log but don't fail - endpoint will still work, just with CSRF check
        print(f"Warning: Could not exempt wallet funding from CSRF: {e}")


@app.route('/success')
def checkout_success():
    pid = request.args.get('pid')
    artist_id = None
    amount = None
    status = None
    try:
        if pid:
            from db import get_session
            from models import Purchase
            with get_session() as s:
                p = s.query(Purchase).filter(Purchase.id == int(pid)).first()
                if p:
                    artist_id = p.artist_id
                    amount = p.amount
                    status = p.status
                    # Best-effort verification: if we have a Stripe session id, check if paid and update.
                    if p.stripe_id and p.status != "paid":
                        try:
                            import stripe
                            api_key = app.config.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
                            stripe.api_key = api_key
                            if stripe.api_key:
                                sess = stripe.checkout.Session.retrieve(p.stripe_id)
                                if getattr(sess, "payment_status", None) == "paid":
                                    p.status = "paid"
                                    status = "paid"
                                    s.commit()
                        except Exception:
                            pass
    except Exception:
        artist_id = None
        amount = None
        status = None
    return render_template('success.html', pid=pid, artist_id=artist_id, amount=amount, status=status)


# Debug routes removed - debug functionality available via /debug endpoint

try:
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)
    # Configure compression to work with all content types
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript', 'image/svg+xml'
    ]
    app.config['COMPRESS_LEVEL'] = 6  # Good balance of speed vs compression
    app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress files > 500 bytes
    print("Compression enabled")
except ImportError:
    print("WARN: Flask-Compress not available, compression disabled")

# Cache configuration
CACHE_TIMEOUT = 600  # 10 minutes (increased for better performance)

# In-memory cache for JSON data files (prevents repeated disk I/O)
_json_data_cache = {}
_json_file_mtimes = {}

# Removed: USERS_FILE, ACTIVITY_FILE, load_users(), save_users() - using database now

def load_json_data(filename, default=None, cache_duration=600):
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


def _etag_for_static_json(filename: str) -> Optional[str]:
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
    try:
        response = make_response(render_template('live_tv.html'))
        response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
        return response
    except Exception as e:
        import logging
        logging.error(f'Error rendering live_tv.html: {e}', exc_info=True)
        # Return a simple error page
        return f'<h1>Error loading Live TV</h1><p>An error occurred: {str(e)}</p>', 500

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
    from utils.observability import get_release
    merch_catalog = read_json('data/merch.json', {"items": []})
    response = make_response(render_template('merch.html', merch=merch_catalog, release=get_release()))
    # Merch changes frequently; avoid serving stale HTML that can "stick" in app/webview caches.
    response.headers['Cache-Control'] = 'no-store'
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
    # Use cached data (cache_duration=600 to match other endpoints - data is already cached)
    music_data = load_json_data('music.json', {'tracks': []}, cache_duration=600)
    shows_data = load_json_data('shows.json', {'shows': []}, cache_duration=600)
    
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
    return _cached_json_response("music.json", {"tracks": []}, max_age_seconds=600)

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
    return _cached_json_response("shows.json", {"shows": []}, max_age_seconds=600)

@app.route('/api/live-tv/channels')
@limiter.exempt
def api_live_tv_channels():
    """Return four Live TV channels built from available media content."""
    try:
        shows_data = load_json_data('shows.json', {'shows': []})
        # Note: Response caching added below after processing

        def normalize_show(item):
            # Map show to a unified structure
            # Ensure id is always present, generate one if missing
            show_id = item.get('id')
            if not show_id:
                # Generate a temporary ID if missing
                show_id = str(uuid.uuid4())
            
            # Ensure tags is a list of strings
            tags = item.get('tags') or []
            if not isinstance(tags, list):
                tags = []
            # Filter out non-string tags and convert to strings
            tags = [str(t) for t in tags if t is not None]
            
            return {
                'id': show_id,
                'title': item.get('title') or 'Untitled',
                'type': 'show',  # treated as video for player behavior
                'video_url': item.get('video_url') or item.get('mp4_link') or item.get('trailer_url'),
                'thumbnail': item.get('thumbnail'),
                'duration_seconds': item.get('duration_seconds') or 0,
                'description': item.get('description') or '',
                'category': (item.get('category') or '').lower(),
                'tags': tags,
            }

        shows = [normalize_show(s) for s in shows_data.get('shows', []) if s.get('video_url') or s.get('mp4_link') or s.get('trailer_url')]

        # Channel categorization
        # Helper to safely join tags
        def safe_join_tags(tags):
            if not tags or not isinstance(tags, list):
                return ''
            return ' '.join(str(t) for t in tags if t is not None)
        
        music_videos = [s for s in shows if (s.get('category') == 'music video' or 'music-video' in s.get('tags', []) or 'musicvideos' in safe_join_tags(s.get('tags', [])))]
        films = [s for s in shows if (s.get('category') == 'short film' or s.get('category') == 'film' or 'short-film' in s.get('tags', []))]
        live_shows = [s for s in shows if (s.get('category') == 'broadcast' or 'live' in safe_join_tags(s.get('tags', [])) or 'episode' in s.get('category', ''))]

        # Misc: everything not already in the other channels (video only)
        # Use .get() to safely access id, filter out None values
        included_ids = {s.get('id') for s in music_videos + films + live_shows if s.get('id')}
        misc_videos = [s for s in shows if s.get('id') and s.get('id') not in included_ids]
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
    except Exception as e:
        # Log the error for debugging
        import logging
        logging.error(f'Error in api_live_tv_channels: {e}', exc_info=True)
        # Return empty channels instead of crashing (return 200 to avoid showing as internal server error)
        response = jsonify({
            'channels': [
                {'id': 'misc', 'name': 'Misc', 'items': []},
                {'id': 'music-videos', 'name': 'Music Videos', 'items': []},
                {'id': 'films', 'name': 'Films', 'items': []},
                {'id': 'live-shows', 'name': 'Live Shows', 'items': []},
            ],
            'error': 'Failed to load channels'
        })
        response.headers['Cache-Control'] = 'no-cache'
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
    return _cached_json_response("artists.json", {"artists": []}, max_age_seconds=600)

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

@app.route('/api/whats-new')
@limiter.exempt
def api_whats_new():
    """Get 'What's New at Ahoy' updates - returns 4 most recent for home page"""
    try:
        data = load_json_data("whats_new.json", {"updates": {}})
        
        # Ensure we have the updates structure (not the whole file)
        if not isinstance(data, dict) or "updates" not in data:
            # If data is malformed, return empty
            return jsonify({"updates": []})
        
        # Extract all items from monthly structure and flatten for backward compatibility
        all_items = []
        updates = data.get("updates", {})
        
        # Handle case where updates might be a list (backward compatibility)
        if isinstance(updates, list):
            all_items = updates
        elif isinstance(updates, dict):
            for year, months in updates.items():
                if not isinstance(months, dict):
                    continue
                for month, sections in months.items():
                    if not isinstance(sections, dict):
                        continue
                    for section_name, section_data in sections.items():
                        if isinstance(section_data, dict) and "items" in section_data:
                            for item in section_data.get("items", []):
                                if isinstance(item, dict):
                                    item_copy = item.copy()
                                    item_copy["year"] = year
                                    item_copy["month"] = month
                                    item_copy["section"] = section_name
                                    all_items.append(item_copy)
        
        # Sort by date (newest first)
        all_items.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Return 4 most recent for home page
        response = jsonify({"updates": all_items[:4]})
        response.headers['Cache-Control'] = 'public, max-age=300'
        return response
    except Exception as e:
        import logging
        logging.error(f'Error in api_whats_new: {e}', exc_info=True)
        # Return empty updates on error
        return jsonify({"updates": []})

@app.route('/whats-new')
def whats_new_archive():
    """Archive page listing all available months"""
    try:
        data = load_json_data("whats_new.json", {"updates": {}})
        updates = data.get("updates", {})
        
        if not isinstance(updates, dict):
            updates = {}
        
        # Build list of available months
        months_list = []
        for year, months in sorted(updates.items(), reverse=True):
            if not isinstance(months, dict):
                continue
            for month, sections in sorted(months.items(), reverse=True):
                if not isinstance(sections, dict):
                    continue
                # Count total items across all sections
                total_items = 0
                for section_data in sections.values():
                    if isinstance(section_data, dict) and "items" in section_data:
                        total_items += len(section_data.get("items", []))
                
                if total_items > 0:  # Only show months with content
                    months_list.append({
                        "year": year,
                        "month": month,
                        "month_name": _get_month_name(month),
                        "total_items": total_items
                    })
        
        return render_template('whats_new_archive.html', months=months_list)
    except Exception as e:
        import logging
        logging.error(f'Error in whats_new_archive: {e}', exc_info=True)
        return render_template('whats_new_archive.html', months=[]), 500

@app.route('/whats-new/<year>/<month>')
def whats_new_month(year, month):
    """Monthly overview page with all 6 sections"""
    try:
        import logging
        # Ensure year is a string (Flask passes it as string, but be explicit)
        year_str = str(year)
        month_lower = month.lower()
        
        data = load_json_data("whats_new.json", {"updates": {}})
        updates = data.get("updates", {})
        
        if not isinstance(updates, dict):
            logging.warning(f'whats_new_month: updates is not a dict, got {type(updates)}')
            return render_template('404.html'), 404
        
        # Check if year exists in updates
        if year_str not in updates:
            available_years = list(updates.keys())
            logging.warning(f'whats_new_month: year {year_str} not found. Available years: {available_years}')
            return render_template('404.html'), 404
        
        year_data = updates.get(year_str, {})
        if not isinstance(year_data, dict):
            logging.warning(f'whats_new_month: year_data for {year_str} is not a dict, got {type(year_data)}')
            return render_template('404.html'), 404
        
        month_data = year_data.get(month_lower, {})
        
        if not month_data:
            # Try to find month with different case
            for m, sections in year_data.items():
                if isinstance(sections, dict) and m.lower() == month_lower:
                    month_data = sections
                    break
        
        if not month_data or not isinstance(month_data, dict):
            available_months = list(year_data.keys())
            logging.warning(f'whats_new_month: month {month_lower} not found for year {year_str}. Available months: {available_months}')
            return render_template('404.html'), 404
        
        # Get all sections (with empty arrays if section doesn't exist)
        sections = {
            "music": month_data.get("music", {"title": "Music Updates", "items": []}) if isinstance(month_data.get("music"), dict) else {"title": "Music Updates", "items": []},
            "videos": month_data.get("videos", {"title": "Video Updates", "items": []}) if isinstance(month_data.get("videos"), dict) else {"title": "Video Updates", "items": []},
            "artists": month_data.get("artists", {"title": "Artist Updates", "items": []}) if isinstance(month_data.get("artists"), dict) else {"title": "Artist Updates", "items": []},
            "platform": month_data.get("platform", {"title": "Platform Updates", "items": []}) if isinstance(month_data.get("platform"), dict) else {"title": "Platform Updates", "items": []},
            "merch": month_data.get("merch", {"title": "Merch Updates", "items": []}) if isinstance(month_data.get("merch"), dict) else {"title": "Merch Updates", "items": []},
            "events": month_data.get("events", {"title": "Events Updates", "items": []}) if isinstance(month_data.get("events"), dict) else {"title": "Events Updates", "items": []}
        }
        
        month_name = _get_month_name(month_lower)
        
        return render_template('whats_new_month.html', 
                             year=year_str, 
                             month=month_lower, 
                             month_name=month_name,
                             sections=sections)
    except Exception as e:
        import logging
        logging.error(f'Error in whats_new_month: {e}', exc_info=True)
        return render_template('404.html'), 500

@app.route('/whats-new/<year>/<month>/<section>')
def whats_new_section(year, month, section):
    """Individual section detail page"""
    try:
        import logging
        # Ensure year is a string (Flask passes it as string, but be explicit)
        year_str = str(year)
        month_lower = month.lower()
        section_lower = section.lower()
        
        valid_sections = ["music", "videos", "artists", "platform", "merch", "events"]
        if section_lower not in valid_sections:
            logging.warning(f'whats_new_section: invalid section {section_lower}')
            return render_template('404.html'), 404
        
        data = load_json_data("whats_new.json", {"updates": {}})
        updates = data.get("updates", {})
        
        if not isinstance(updates, dict):
            logging.warning(f'whats_new_section: updates is not a dict, got {type(updates)}')
            return render_template('404.html'), 404
        
        # Check if year exists in updates
        if year_str not in updates:
            available_years = list(updates.keys())
            logging.warning(f'whats_new_section: year {year_str} not found. Available years: {available_years}')
            return render_template('404.html'), 404
        
        year_data = updates.get(year_str, {})
        if not isinstance(year_data, dict):
            logging.warning(f'whats_new_section: year_data for {year_str} is not a dict, got {type(year_data)}')
            return render_template('404.html'), 404
        
        month_data = year_data.get(month_lower, {})
        
        if not month_data or not isinstance(month_data, dict):
            # Try to find month with different case
            for m, sections in year_data.items():
                if isinstance(sections, dict) and m.lower() == month_lower:
                    month_data = sections
                    break
        
        if not month_data or not isinstance(month_data, dict):
            available_months = list(year_data.keys())
            logging.warning(f'whats_new_section: month {month_lower} not found for year {year_str}. Available months: {available_months}')
            return render_template('404.html'), 404
        
        section_data = month_data.get(section_lower, {})
        if not isinstance(section_data, dict):
            section_data = {"title": f"{section.capitalize()} Updates", "items": []}
        
        month_name = _get_month_name(month_lower)
        
        return render_template('whats_new_section.html',
                             year=year_str,
                             month=month_lower,
                             month_name=month_name,
                             section=section_lower,
                             section_title=section_data.get("title", f"{section.capitalize()} Updates"),
                             items=section_data.get("items", []))
    except Exception as e:
        import logging
        logging.error(f'Error in whats_new_section: {e}', exc_info=True)
        return render_template('404.html'), 500

def _get_month_name(month_abbr):
    """Convert month abbreviation to full name"""
    months = {
        "jan": "January", "feb": "February", "mar": "March", "apr": "April",
        "may": "May", "jun": "June", "jul": "July", "aug": "August",
        "sep": "September", "oct": "October", "nov": "November", "dec": "December"
    }
    return months.get(month_abbr.lower(), month_abbr.capitalize())

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
    # Source-of-truth is the DB user row (session['user_data'] may be absent).
    return jsonify({
        "id": current_user.id,
        "email": getattr(current_user, "email", None),
        "username": getattr(current_user, "username", None),
        "display_name": getattr(current_user, "display_name", None),
        "avatar_url": getattr(current_user, "avatar_url", None),
    })

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
                'username': getattr(user, "username", None),
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

@app.route('/auth/forgot')
def forgot_password_page():
    """Forgot password page (requests reset link)."""
    return render_template('forgot_password.html')

@app.route('/auth/reset')
def reset_password_page():
    """Reset password page (consumes token)."""
    return render_template('reset_password.html')

@app.route('/account')
def account_page():
    """User account/profile page"""
    from flask_login import current_user
    from db import get_session
    from models import Bookmark, Playlist, PlayHistory, Purchase
    from sqlalchemy import func

    if not current_user.is_authenticated:
        return render_template('account.html', stats={}, recent_orders=[])

    with get_session() as s:
        from models import User
        user_id = current_user.id
        user = s.query(User).filter(User.id == user_id).first()
        wallet_balance = float(user.wallet_balance or 0) if user else 0.0
        
        stats = {
            "bookmarks": int(s.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user_id).scalar() or 0),
            "plays": int(s.query(func.count(PlayHistory.id)).filter(PlayHistory.user_id == user_id).scalar() or 0),
            "merch_orders": 0,
        }
        recent_orders = []
        
        # Handle purchases table - it may not exist if migration hasn't run
        try:
            from sqlalchemy import inspect
            insp = inspect(s.bind)
            tables = insp.get_table_names()
            if 'purchases' in tables:
                stats["merch_orders"] = int(
                    s.query(func.count(Purchase.id)).filter(Purchase.user_id == user_id, Purchase.type == "merch").scalar()
                    or 0
                )
                recent = (
                    s.query(Purchase)
                    .filter(Purchase.user_id == user_id, Purchase.type == "merch")
                    .order_by(Purchase.created_at.desc())
                    .limit(10)
                    .all()
                )
                recent_orders = [
                    {
                        "id": p.id,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                        "status": p.status,
                        "item_id": p.item_id,
                        "qty": p.qty,
                        "total": p.total,
                        "stripe_id": p.stripe_id,
                    }
                    for p in recent
                ]
        except Exception as e:
            # If purchases table doesn't exist or query fails, just use defaults
            current_app.logger.warning(f"Could not query purchases table: {e}")
            pass

    return render_template('account.html', stats=stats, recent_orders=recent_orders, wallet_balance=wallet_balance)

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

@app.route('/admin/artist-earnings')
@login_required
@_admin_session_required
def admin_artist_earnings():
    """Admin page to view artist earnings (payout buckets)"""
    return render_template('admin/artist_earnings.html')

@app.route('/admin')
@login_required
@_admin_session_required
def admin_page():
    """Admin page (read-only stats)"""
    return render_template('admin.html')

@app.route('/feedback')
def feedback_page():
    """Feedback form page"""
    return render_template('feedback.html')

@app.route('/contact')
def contact_page():
    """Contact form page"""
    return render_template('contact.html')

@app.route('/api/admin/stats', methods=['GET'])
@login_required
@_admin_session_required
def admin_stats():
    """Read-only admin stats (users + merch orders + analytics)."""
    from db import get_session
    from models import (
        User, Purchase, PlayHistory, ListeningSession, ListeningTotal,
        Bookmark, UserArtistFollow, Tip
    )
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    active_since = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(days=1)

    with get_session() as s:
        # User stats
        total_users = int(s.query(func.count(User.id)).scalar() or 0)
        active_users = int(
            s.query(func.count(User.id))
            .filter(User.last_active_at.isnot(None))
            .filter(User.last_active_at >= active_since)
            .scalar()
            or 0
        )
        new_users_7d = int(
            s.query(func.count(User.id))
            .filter(User.created_at >= week_ago)
            .scalar() or 0
        )
        new_users_24h = int(
            s.query(func.count(User.id))
            .filter(User.created_at >= day_ago)
            .scalar() or 0
        )

        # Order stats
        total_orders = int(s.query(func.count(Purchase.id)).filter(Purchase.type == "merch").scalar() or 0)
        pending_orders = int(
            s.query(func.count(Purchase.id)).filter(Purchase.type == "merch", Purchase.status == "pending").scalar() or 0
        )
        paid_orders = int(
            s.query(func.count(Purchase.id)).filter(Purchase.type == "merch", Purchase.status == "paid").scalar() or 0
        )
        fulfilled_orders = int(
            s.query(func.count(Purchase.id)).filter(Purchase.type == "merch", Purchase.status == "fulfilled").scalar() or 0
        )

        # Play statistics
        total_plays = int(s.query(func.count(PlayHistory.id)).scalar() or 0)
        plays_7d = int(
            s.query(func.count(PlayHistory.id))
            .filter(PlayHistory.played_at >= week_ago)
            .scalar() or 0
        )
        plays_24h = int(
            s.query(func.count(PlayHistory.id))
            .filter(PlayHistory.played_at >= day_ago)
            .scalar() or 0
        )
        unique_tracks_played = int(
            s.query(func.count(func.distinct(PlayHistory.media_id)))
            .filter(PlayHistory.media_type == "track")
            .scalar() or 0
        )

        # Listening time statistics
        total_listening_seconds = int(
            s.query(func.sum(ListeningTotal.total_seconds)).scalar() or 0
        )
        total_listening_hours = round(total_listening_seconds / 3600, 1)
        
        # Listening sessions
        total_sessions = int(s.query(func.count(ListeningSession.id)).scalar() or 0)
        sessions_7d = int(
            s.query(func.count(ListeningSession.id))
            .filter(ListeningSession.started_at >= week_ago)
            .scalar() or 0
        )
        radio_sessions = int(
            s.query(func.count(ListeningSession.id))
            .filter(ListeningSession.source == "radio")
            .scalar() or 0
        )
        manual_sessions = int(
            s.query(func.count(ListeningSession.id))
            .filter(ListeningSession.source == "manual")
            .scalar() or 0
        )

        # Engagement stats
        total_bookmarks = int(s.query(func.count(Bookmark.id)).scalar() or 0)
        total_follows = int(s.query(func.count(UserArtistFollow.id)).scalar() or 0)
        total_tips = int(s.query(func.count(Tip.id)).scalar() or 0)
        total_tip_amount = float(
            s.query(func.sum(Tip.amount)).scalar() or 0
        )

    return jsonify({
        "users": {
            "total": total_users,
            "active_30d": active_users,
            "new_7d": new_users_7d,
            "new_24h": new_users_24h,
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "paid": paid_orders,
            "fulfilled": fulfilled_orders,
        },
        "plays": {
            "total": total_plays,
            "last_7d": plays_7d,
            "last_24h": plays_24h,
            "unique_tracks": unique_tracks_played,
        },
        "listening": {
            "total_hours": total_listening_hours,
            "total_seconds": total_listening_seconds,
            "total_sessions": total_sessions,
            "sessions_7d": sessions_7d,
            "radio_sessions": radio_sessions,
            "manual_sessions": manual_sessions,
        },
        "engagement": {
            "bookmarks": total_bookmarks,
            "follows": total_follows,
            "tips": total_tips,
            "tip_amount": round(total_tip_amount, 2),
        },
    })


@app.route('/api/admin/analytics', methods=['GET'])
@login_required
@_admin_session_required
def admin_analytics():
    """Detailed analytics for admin dashboard."""
    from db import get_session
    from models import (
        User, PlayHistory, ListeningSession, Bookmark,
        UserArtistFollow, Tip
    )
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    with get_session() as s:
        # Most active users (by play count)
        top_users_by_plays = s.query(
            User.id,
            User.username,
            User.email,
            func.count(PlayHistory.id).label('play_count')
        ).join(
            PlayHistory, User.id == PlayHistory.user_id
        ).group_by(
            User.id, User.username, User.email
        ).order_by(
            func.count(PlayHistory.id).desc()
        ).limit(10).all()

        # Most played tracks
        top_tracks = s.query(
            PlayHistory.media_id,
            func.count(PlayHistory.id).label('play_count')
        ).filter(
            PlayHistory.media_type == "track"
        ).group_by(
            PlayHistory.media_id
        ).order_by(
            func.count(PlayHistory.id).desc()
        ).limit(20).all()

        # Plays over time (last 7 days)
        daily_plays = []
        for i in range(7):
            day_start = (now - timedelta(days=6-i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = int(
                s.query(func.count(PlayHistory.id))
                .filter(PlayHistory.played_at >= day_start)
                .filter(PlayHistory.played_at < day_end)
                .scalar() or 0
            )
            daily_plays.append({
                "date": day_start.isoformat(),
                "count": count
            })

        # Listening time by source
        radio_time = int(
            s.query(func.sum(ListeningSession.seconds))
            .filter(ListeningSession.source == "radio")
            .scalar() or 0
        )
        manual_time = int(
            s.query(func.sum(ListeningSession.seconds))
            .filter(ListeningSession.source == "manual")
            .scalar() or 0
        )

        # User engagement breakdown
        users_with_plays = int(
            s.query(func.count(func.distinct(PlayHistory.user_id))).scalar() or 0
        )
        users_with_bookmarks = int(
            s.query(func.count(func.distinct(Bookmark.user_id))).scalar() or 0
        )
        users_with_follows = int(
            s.query(func.count(func.distinct(UserArtistFollow.user_id))).scalar() or 0
        )
        users_with_tips = int(
            s.query(func.count(func.distinct(Tip.user_id))).scalar() or 0
        )

        # Recent activity (last 24h)
        recent_plays_24h = int(
            s.query(func.count(PlayHistory.id))
            .filter(PlayHistory.played_at >= (now - timedelta(days=1)))
            .scalar() or 0
        )
        recent_bookmarks_24h = int(
            s.query(func.count(Bookmark.id))
            .filter(Bookmark.created_at >= (now - timedelta(days=1)))
            .scalar() or 0
        )
        recent_follows_24h = int(
            s.query(func.count(UserArtistFollow.id))
            .filter(UserArtistFollow.created_at >= (now - timedelta(days=1)))
            .scalar() or 0
        )

    return jsonify({
        "top_users": [
            {
                "id": u.id,
                "username": u.username or u.email,
                "email": u.email,
                "play_count": u.play_count
            }
            for u in top_users_by_plays
        ],
        "top_tracks": [
            {
                "media_id": t.media_id,
                "play_count": t.play_count
            }
            for t in top_tracks
        ],
        "daily_plays": daily_plays,
        "listening_by_source": {
            "radio_hours": round(radio_time / 3600, 1),
            "manual_hours": round(manual_time / 3600, 1),
            "radio_seconds": radio_time,
            "manual_seconds": manual_time,
        },
        "user_engagement": {
            "users_with_plays": users_with_plays,
            "users_with_bookmarks": users_with_bookmarks,
            "users_with_follows": users_with_follows,
            "users_with_tips": users_with_tips,
        },
        "recent_24h": {
            "plays": recent_plays_24h,
            "bookmarks": recent_bookmarks_24h,
            "follows": recent_follows_24h,
        },
    })


@app.route('/api/admin/users', methods=['GET'])
@login_required
@_admin_session_required
def admin_users():
    """Get list of users for admin dashboard."""
    from db import get_session
    from models import User
    from sqlalchemy import func

    limit = 100
    try:
        limit = int(request.args.get("limit") or "100")
        limit = max(1, min(500, limit))
    except Exception:
        limit = 100

    with get_session() as s:
        rows = (
            s.query(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .all()
        )
        users = [{
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "display_name": u.display_name,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_active_at": u.last_active_at.isoformat() if u.last_active_at else None,
            "is_admin": u.is_admin,
            "disabled": u.disabled,
        } for u in rows]

        # Get play counts for each user
        play_counts = {}
        if users:
            user_ids = [u["id"] for u in users]
            from models import PlayHistory
            counts = (
                s.query(
                    PlayHistory.user_id,
                    func.count(PlayHistory.id).label('count')
                )
                .filter(PlayHistory.user_id.in_(user_ids))
                .group_by(PlayHistory.user_id)
                .all()
            )
            play_counts = {user_id: count for user_id, count in counts}

        # Add play counts to users
        for user in users:
            user["play_count"] = play_counts.get(user["id"], 0)

    return jsonify({"users": users})


@app.route('/api/admin/orders', methods=['GET'])
@login_required
@_admin_session_required
def admin_orders():
    """Read-only list of merch orders."""
    from db import get_session
    from models import Purchase

    limit = 200
    try:
        limit = int(request.args.get("limit") or "200")
        limit = max(1, min(500, limit))
    except Exception:
        limit = 200

    with get_session() as s:
        rows = (
            s.query(Purchase)
            .filter(Purchase.type == "merch")
            .order_by(Purchase.created_at.desc())
            .limit(limit)
            .all()
        )
        orders = [{
            "id": p.id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "status": p.status,
            "item_id": p.item_id,
            "qty": p.qty,
            "amount": p.amount,
            "total": p.total,
            "stripe_id": p.stripe_id,
        } for p in rows]
    return jsonify({"orders": orders})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@_admin_session_required
def admin_delete_user(user_id):
    return jsonify({"error": "read_only_admin"}), 403

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@_admin_session_required
def admin_reset_password(user_id):
    return jsonify({"error": "read_only_admin"}), 403

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
            print("Applying migrations (alembic upgrade heads)...")
            env = os.environ.copy()
            # Ensure PYTHONPATH includes project root so alembic/env.py can import models
            project_root = os.path.dirname(os.path.abspath(__file__))
            env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH','')}" if env.get('PYTHONPATH') else project_root
            # Provide a sane default DATABASE_URL for local runs
            env.setdefault("DATABASE_URL", "sqlite:///local.db")
            subprocess.run([alembic_bin, "upgrade", "heads"], check=True, env=env)
        else:
            print("WARN: Alembic not found in PATH; skipping automatic migrations.")
    except Exception as e:
        print(f"WARN: Migrations step skipped: {e}")

    # 2) Pick a free port automatically if requested is busy
    requested = int(os.getenv("PORT", "5000"))
    chosen = requested
    if not _is_port_free(requested):
        alt = find_available_port(5001, 5020)
        if alt:
            print(f"WARN: Port {requested} busy — starting on {alt}")
            chosen = alt
        else:
            # Fallback: let OS pick an ephemeral port
            print(f"ERROR: Port {requested} busy and no alternates free in 5001-5020.")
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
        print(f"Starting gunicorn on port {chosen}...")
        os.execv(gunicorn_bin, ["gunicorn", "app:app", "--workers", "2", "--threads", "4", "--timeout", "120", "-b", f"0.0.0.0:{chosen}"])
    else:
        if gunicorn_bin and is_macos and not want_gunicorn:
            print("🧯 macOS detected: skipping gunicorn by default to avoid fork()/objc crashes.")
            print("   Set AHOY_USE_GUNICORN=1 if you want to run gunicorn locally anyway.")
        if is_windows:
            print(f"Starting Flask dev server on http://127.0.0.1:{chosen} (Windows detected)")
        else:
            print(f"Starting Flask dev server on http://127.0.0.1:{chosen}")
        app.run(port=chosen, use_reloader=False)

#!/usr/bin/env python3
"""
CDN utility for Ahoy Indie Media

Provides CDN URL generation for static assets with:
- Optional CDN URL prefix via environment variable
- Cache busting via version query parameter
- Fallback to Flask's url_for when CDN not configured
"""

import os
import hashlib
from flask import url_for, current_app
from functools import lru_cache

# CDN configuration
CDN_URL = os.getenv('CDN_URL', '').rstrip('/')  # e.g., https://cdn.ahoyindie.com
STATIC_VERSION = os.getenv('STATIC_VERSION', 'v1')  # For cache busting


def get_cdn_url():
    """Get the configured CDN URL or empty string if not set."""
    return CDN_URL


def is_cdn_enabled():
    """Check if CDN is configured."""
    return bool(CDN_URL)


@lru_cache(maxsize=1000)
def get_file_hash(filepath: str) -> str:
    """
    Get a short hash of file contents for cache busting.
    Uses first 8 chars of MD5 hash.
    Cached for performance.
    """
    try:
        import os
        full_path = os.path.join(current_app.static_folder, filepath)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:8]
    except Exception:
        pass
    return STATIC_VERSION


def static_url(filename: str, use_hash: bool = False, _external: bool = False) -> str:
    """
    Generate a URL for a static file, using CDN if configured.

    Args:
        filename: Path to static file relative to /static/
        use_hash: If True, append file content hash for cache busting
        _external: If True and CDN not set, generate absolute URL

    Returns:
        URL string for the static file

    Examples:
        static_url('css/main.css')
        # Without CDN: /static/css/main.css?v=v1
        # With CDN: https://cdn.ahoyindie.com/static/css/main.css?v=v1

        static_url('js/app.js', use_hash=True)
        # With hash: /static/js/app.js?v=a1b2c3d4
    """
    # Determine cache bust parameter
    if use_hash:
        try:
            version = get_file_hash(filename)
        except Exception:
            version = STATIC_VERSION
    else:
        version = STATIC_VERSION

    if CDN_URL:
        # Use CDN URL
        url = f"{CDN_URL}/static/{filename}"
        if version:
            url = f"{url}?v={version}"
        return url
    else:
        # Use Flask's url_for
        base_url = url_for('static', filename=filename, _external=_external)
        if version:
            separator = '&' if '?' in base_url else '?'
            base_url = f"{base_url}{separator}v={version}"
        return base_url


def cdn_context_processor():
    """
    Flask context processor to add CDN functions to templates.

    Usage in templates:
        {{ static_url('css/main.css') }}
        {{ cdn_enabled }}
    """
    return {
        'static_url': static_url,
        'cdn_enabled': is_cdn_enabled(),
        'cdn_url': get_cdn_url(),
    }


def init_cdn(app):
    """
    Initialize CDN support for a Flask app.

    Registers:
    - Context processor for template access
    - Jinja global function
    """
    app.context_processor(cdn_context_processor)
    app.jinja_env.globals['static_url'] = static_url

    # Log CDN configuration
    import structlog
    logger = structlog.get_logger()
    if CDN_URL:
        logger.info("CDN configured", cdn_url=CDN_URL, version=STATIC_VERSION)
    else:
        logger.info("CDN not configured, using local static files", version=STATIC_VERSION)

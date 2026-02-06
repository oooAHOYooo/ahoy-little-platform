#!/usr/bin/env python3
"""
Observability utilities for Ahoy Indie Media
Handles Sentry initialization and release management
"""

import os
import subprocess
import sys


def _is_safe_release(s):
    """Reject local file paths or long strings that shouldn't be shown as BUILD."""
    if not s or not isinstance(s, str):
        return False
    s = s.strip()
    if len(s) > 24:
        return False
    bad = ("/var/", "/Users/", "TemporaryItems", "Screenshot", ".png", ".jpg", "\\")
    return not any(b in s for b in bad)


def get_release():
    """Get release version from git commit or env var. Never returns a file path."""
    # Try APP_RELEASE env var first
    release = os.getenv("APP_RELEASE")
    if release and _is_safe_release(release):
        return release

    # Try GIT_COMMIT or RENDER_GIT_COMMIT (Render sets one of these)
    for env_name in ("GIT_COMMIT", "RENDER_GIT_COMMIT"):
        git_commit = os.getenv(env_name)
        if git_commit and _is_safe_release(git_commit):
            return git_commit[:12] if len(git_commit) > 12 else git_commit

    # Try to get git commit hash
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        out = (result.stdout or "").strip()
        if out and _is_safe_release(out):
            return out
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


def init_sentry(app):
    """Initialize Sentry error tracking if DSN is provided"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        app.logger.info("Sentry DSN not provided, skipping Sentry initialization")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment=os.getenv("FLASK_ENV", "production"),
            release=get_release()
        )
        
        app.logger.info(f"Sentry initialized with release {get_release()}")
        return True
        
    except ImportError:
        app.logger.warning("Sentry SDK not installed, skipping Sentry initialization")
        return False
    except Exception as e:
        app.logger.error(f"Failed to initialize Sentry: {e}")
        return False

#!/usr/bin/env python3
"""
Observability utilities for Ahoy Indie Media
Handles Sentry initialization and release management
"""

import os
import subprocess
import sys


def get_release():
    """Get release version from git commit or env var"""
    # Try APP_RELEASE env var first
    release = os.getenv("APP_RELEASE")
    if release:
        return release
    
    # Try GIT_COMMIT env var
    git_commit = os.getenv("GIT_COMMIT")
    if git_commit:
        return git_commit
    
    # Try to get git commit hash
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
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

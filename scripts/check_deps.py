#!/usr/bin/env python3
"""
Dependency health check script for Ahoy Indie Media
Checks that all production dependencies can be imported and reports versions
"""

import json
import sys
from pkg_resources import get_distribution

def check_dependency(name, import_name, version_attr=None):
    """Check if a dependency can be imported and get its version"""
    try:
        module = __import__(import_name)
        if version_attr:
            version = getattr(module, version_attr, "unknown")
        else:
            try:
                version = get_distribution(name).version
            except:
                version = getattr(module, '__version__', "unknown")
        
        return {
            "library": name,
            "version": str(version),
            "ok": True
        }
    except ImportError as e:
        return {
            "library": name,
            "version": None,
            "ok": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "library": name,
            "version": None,
            "ok": False,
            "error": f"Unexpected error: {str(e)}"
        }

def main():
    """Check all production dependencies"""
    dependencies = [
        ("flask", "flask"),
        ("gunicorn", "gunicorn.app.base"),
        ("bcrypt", "bcrypt"),
        ("flask-limiter", "flask_limiter"),
        ("limits", "limits"),
        ("flask-wtf", "flask_wtf"),
        ("email-validator", "email_validator"),
        ("sentry-sdk", "sentry_sdk"),
        ("psycopg", "psycopg"),
        ("python-json-logger", "pythonjsonlogger"),
        ("structlog", "structlog"),
    ]
    
    results = []
    failed_count = 0
    
    for name, import_name in dependencies:
        result = check_dependency(name, import_name)
        results.append(result)
        if not result["ok"]:
            failed_count += 1
        print(json.dumps(result))
    
    # Final status
    status = "ok" if failed_count == 0 else "error"
    final_result = {
        "status": status,
        "failed": failed_count
    }
    print(json.dumps(final_result))
    
    # Exit with error code if any dependencies failed
    if failed_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

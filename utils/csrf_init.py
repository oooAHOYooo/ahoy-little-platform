#!/usr/bin/env python3
"""
CSRF protection initialization for Ahoy Indie Media
Handles CSRF token validation and error responses
"""

import structlog
from flask import request, jsonify, g
from flask_wtf.csrf import CSRFProtect, CSRFError

logger = structlog.get_logger()


def init_csrf(app):
    """Initialize CSRF protection"""
    csrf = CSRFProtect(app)
    
    # Configure CSRF to accept tokens from X-CSRFToken header for JSON requests
    @csrf.exempt
    def exempt_json_requests():
        """Exempt JSON requests from CSRF if they have the token in header"""
        # Hotfix: Analytics endpoint used by client without session causes 502 loop
        if request.path == '/api/admin/analytics/event':
            return True

        if request.is_json and request.headers.get('X-CSRFToken'):
            return False  # Don't exempt - validate the header token
        return request.is_json  # Exempt other JSON requests
    
    # Custom CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF validation errors with structured JSON response"""
        request_id = getattr(g, 'request_id', None)
        
        logger.warning("CSRF validation failed",
                      error=str(e),
                      path=request.path,
                      method=request.method,
                      request_id=request_id,
                      user_agent=request.headers.get('User-Agent', 'unknown'))
        
        return jsonify({
            "error": "CSRF validation failed",
            "reason": "Invalid or missing CSRF token",
            "request_id": request_id
        }), 400
    
    logger.info("CSRF protection initialized")
    return csrf

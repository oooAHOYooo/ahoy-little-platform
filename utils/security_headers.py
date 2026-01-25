#!/usr/bin/env python3
"""
Security headers middleware for Ahoy Indie Media
Handles security headers and CSP reporting
"""

import os
import json
import structlog
from flask import Blueprint, request, jsonify

logger = structlog.get_logger()


def attach_security_headers(app):
    """Attach security headers middleware to Flask app"""

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Basic security headers (always set)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Check if this is a static asset request
        is_static = request.path.startswith('/static/')

        # Add cache headers for static assets (CDN-optimized)
        if response.content_type:
            # Static assets: long cache with immutable (1 year)
            if response.content_type.startswith('text/css'):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                response.headers['Expires'] = 'Thu, 31 Dec 2026 23:59:59 GMT'
                if is_static:
                    response.headers['Vary'] = 'Accept-Encoding'
            elif response.content_type.startswith('application/javascript') or response.content_type.startswith('text/javascript'):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                response.headers['Expires'] = 'Thu, 31 Dec 2026 23:59:59 GMT'
                if is_static:
                    response.headers['Vary'] = 'Accept-Encoding'
            elif response.content_type.startswith('image/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                response.headers['Expires'] = 'Thu, 31 Dec 2026 23:59:59 GMT'
            elif response.content_type.startswith('font/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                response.headers['Expires'] = 'Thu, 31 Dec 2026 23:59:59 GMT'
                # CORS headers for fonts
                response.headers['Access-Control-Allow-Origin'] = '*'
            elif response.content_type.startswith('application/json') and is_static:
                # JSON data files can be cached but with shorter TTL
                response.headers['Cache-Control'] = 'public, max-age=3600'
                response.headers['Vary'] = 'Accept-Encoding'

        # Production-only headers
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "media-src 'self' https:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; "
                "font-src 'self' data:; "
                "connect-src 'self' https:;"
            )
            response.headers['Content-Security-Policy'] = csp

        return response


def create_csp_report_blueprint():
    """Create CSP report endpoint blueprint"""
    bp = Blueprint('csp_report', __name__, url_prefix='')
    
    @bp.route('/csp-report', methods=['POST'])
    def csp_report():
        """Handle CSP violation reports"""
        try:
            content_type = request.content_type or ''
            
            if 'application/csp-report' in content_type or 'application/json' in content_type:
                report_data = request.get_json(silent=True) or {}
                
                # Redact URLs for privacy
                if 'csp-report' in report_data:
                    csp_report = report_data['csp-report']
                    if 'document-uri' in csp_report:
                        csp_report['document-uri'] = '[REDACTED]'
                    if 'blocked-uri' in csp_report:
                        csp_report['blocked-uri'] = '[REDACTED]'
                
                logger.warning("CSP violation report", 
                             report=report_data,
                             user_agent=request.headers.get('User-Agent', 'unknown'),
                             remote_addr=request.remote_addr)
                
                return '', 204
            else:
                logger.warning("Invalid CSP report content type", 
                             content_type=content_type)
                return '', 400
                
        except Exception as e:
            logger.error("Failed to process CSP report", error=str(e))
            return '', 500
    
    return bp

#!/usr/bin/env python3
"""
Structured logging initialization for Ahoy Indie Media
Handles JSON logging in production and console logging in development
"""

import os
import logging
import uuid
import time
from contextvars import ContextVar
from flask import g, request, current_app

import structlog
from structlog.stdlib import LoggerFactory

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


def init_logging():
    """Initialize structured logging based on environment"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    flask_env = os.getenv("FLASK_ENV", "development")
    
    # Configure structlog
    if flask_env == "production":
        # JSON logging for production
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # Console logging for development
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Configure Python logging
    logging.basicConfig(
        format="%(message)s",
        stream=os.sys.stdout,
        level=getattr(logging, log_level),
    )
    
    logger = structlog.get_logger()
    logger.info("Logging initialized", 
                mode="json" if flask_env == "production" else "console",
                level=log_level)
    
    return logger


def get_request_id():
    """Get current request ID from context"""
    return request_id_var.get()


def set_request_id(request_id: str):
    """Set request ID in context"""
    request_id_var.set(request_id)


def init_request_logging(app):
    """Initialize request logging middleware"""
    logger = structlog.get_logger()
    
    @app.before_request
    def before_request():
        # Generate or get request ID
        request_id_header = os.getenv("REQUEST_ID_HEADER", "X-Request-ID")
        request_id = request.headers.get(request_id_header) or str(uuid.uuid4())
        
        # Store in Flask g and context var
        g.request_id = request_id
        g.request_start_time = time.perf_counter()
        set_request_id(request_id)
        
        # Add to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
    
    @app.after_request
    def after_request(response):
        try:
            # Skip logging static files in development to reduce noise
            flask_env = os.getenv("FLASK_ENV", "development")
            if flask_env != "production" and request.path.startswith("/static/"):
                return response
            
            # Calculate duration
            duration_ms = None
            if hasattr(g, 'request_start_time'):
                duration_ms = round((time.perf_counter() - g.request_start_time) * 1000, 2)
            
            # Get user ID if authenticated
            user_id = None
            if hasattr(g, 'user') and g.user:
                user_id = getattr(g.user, 'id', None)
            elif hasattr(request, 'session') and request.session.get('username'):
                user_id = request.session.get('username')
            
            # Log request
            logger.info("request",
                       method=request.method,
                       path=request.path,
                       status=response.status_code,
                       duration_ms=duration_ms,
                       remote_ip=request.remote_addr,
                       request_id=g.get('request_id'),
                       user_id=user_id,
                       route_name=request.endpoint)
            
        except Exception as e:
            logger.error("Failed to log request", error=str(e))
        finally:
            return response

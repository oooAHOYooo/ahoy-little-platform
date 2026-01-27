"""
Shared API helper functions for blueprints.

Common utilities for request parsing, validation, and response formatting.
"""
from flask import request, jsonify


# Valid media types across the platform
ALLOWED_MEDIA_TYPES = {"music", "show", "artist", "clip"}


def parse_pagination(default_per_page: int = 50, max_per_page: int = 100):
    """
    Parse pagination parameters from request args.

    Args:
        default_per_page: Default items per page if not specified
        max_per_page: Maximum allowed items per page

    Returns:
        tuple: (page, per_page, offset)
    """
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (ValueError, TypeError):
        page = 1

    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (ValueError, TypeError):
        per_page = default_per_page

    per_page = max(1, min(per_page, max_per_page))
    offset = (page - 1) * per_page

    return page, per_page, offset


def validate_media_type(media_type: str) -> bool:
    """Check if a media type is valid."""
    return media_type in ALLOWED_MEDIA_TYPES


def error_response(error_code: str, status: int = 400, message: str = None):
    """
    Create a standardized error response.

    Args:
        error_code: Short error identifier (e.g., "not_found", "forbidden")
        status: HTTP status code
        message: Optional human-readable message

    Returns:
        tuple: (response, status_code)
    """
    response = {"error": error_code}
    if message:
        response["message"] = message
    return jsonify(response), status


def success_response(data: dict = None, status: int = 200):
    """
    Create a standardized success response.

    Args:
        data: Response data dict
        status: HTTP status code

    Returns:
        tuple: (response, status_code)
    """
    response = {"success": True}
    if data:
        response.update(data)
    return jsonify(response), status

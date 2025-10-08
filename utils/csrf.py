import os
import secrets
from functools import wraps
from flask import session, request, abort


CSRF_SESSION_KEY = "csrf_token"


def generate_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf() -> bool:
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    token = session.get(CSRF_SESSION_KEY)
    return bool(token and sent and secrets.compare_digest(str(token), str(sent)))


def csrf_protect(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if not validate_csrf():
                abort(400)
        return fn(*args, **kwargs)
    return wrapper



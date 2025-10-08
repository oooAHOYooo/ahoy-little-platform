import os
import datetime as dt
from functools import wraps

import jwt
from flask import request, jsonify, g, redirect, url_for, flash, current_app, make_response


JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
ACCESS_TTL_MIN = 15
REFRESH_TTL_DAYS = 30


def create_access_token(user_id: int, email: str) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_id: int, email: str) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(days=REFRESH_TTL_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing_bearer_token"}), 401
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return jsonify({"error": "invalid_token_type"}), 401
            # Make user info available to handlers
            g.jwt = payload
        except Exception as e:
            return jsonify({"error": "invalid_token", "detail": str(e)}), 401
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """Require admin; respects JSON vs HTML requests.

    - Requires a valid access token (jwt_required behavior)
    - Loads real user from DB and checks is_admin
    - For HTML (Accept: text/html), redirect to /auth with flash
    - For JSON, return 403
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # First enforce JWT
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            # no token
            wants_html = 'text/html' in (request.headers.get('Accept') or '')
            if wants_html:
                flash("Please log in as admin", "warning")
                return redirect(url_for('auth_page'))
            return jsonify({"error": "forbidden"}), 403
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return jsonify({"error": "forbidden"}), 403
            user_id = int(payload.get("sub"))
        except Exception:
            wants_html = 'text/html' in (request.headers.get('Accept') or '')
            if wants_html:
                flash("Session expired. Please log in.", "warning")
                return redirect(url_for('auth_page'))
            return jsonify({"error": "forbidden"}), 403

        # Load real user and verify admin
        try:
            from db import get_session
            from models import User
            with get_session() as session:
                real_user = session.get(User, user_id)
                if not real_user or not real_user.is_admin:
                    wants_html = 'text/html' in (request.headers.get('Accept') or '')
                    if wants_html:
                        flash("Admin access required", "danger")
                        return redirect(url_for('auth_page'))
                    return jsonify({"error": "forbidden"}), 403
                # store real user for downstream use
                g.real_user = real_user
        except Exception:
            return jsonify({"error": "forbidden"}), 403

        return fn(*args, **kwargs)

    return wrapper


# Impersonation helpers
def _sign_value(value: str) -> str:
    secret = JWT_SECRET  # reuse same secret for simplicity
    import hmac, hashlib
    sig = hmac.new(secret.encode("utf-8"), msg=value.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    return f"{value}.{sig}"


def _verify_signed_value(signed: str) -> str | None:
    parts = signed.split(".")
    if len(parts) < 2:
        return None
    value = ".".join(parts[:-1])
    sig = parts[-1]
    import hmac, hashlib
    expected = hmac.new(JWT_SECRET.encode("utf-8"), msg=value.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected):
        return value
    return None


def set_impersonate(user_id: int):
    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie("impersonate_as", _sign_value(str(user_id)), httponly=True, samesite="Lax")
    return resp


def clear_impersonate():
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie("impersonate_as")
    return resp


def get_effective_user(real_user, request):
    """Return impersonated user for UI if real_user is admin and cookie valid, else real_user.
    Note: admin_required should always check real_user, not the effective one.
    """
    if not real_user or not getattr(real_user, "is_admin", False):
        return real_user
    signed = request.cookies.get("impersonate_as")
    if not signed:
        return real_user
    user_id_str = _verify_signed_value(signed)
    if not user_id_str:
        return real_user
    try:
        from db import get_session
        from models import User
        with get_session() as session:
            imp = session.get(User, int(user_id_str))
            return imp or real_user
    except Exception:
        return real_user



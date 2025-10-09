import os
from typing import Optional
import datetime as dt
from functools import wraps

# Optional PyJWT import with fallback
try:
    import jwt as _pyjwt  # type: ignore
    _HAS_PYJWT = True
except Exception:  # ImportError or runtime issues
    _pyjwt = None
    _HAS_PYJWT = False

from flask import request, jsonify, g, redirect, url_for, flash, current_app, make_response


JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
ACCESS_TTL_MIN = 15
REFRESH_TTL_DAYS = 30


# Lightweight JWT-compatible fallback (HS256 only)
def _b64url_encode(raw: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    import base64
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def _jwt_fallback_encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    import json, hmac, hashlib
    header = {"alg": algorithm, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _jwt_fallback_decode(token: str, secret: str, algorithms: list[str] | tuple[str, ...] = ("HS256",)) -> dict:
    import json, hmac, hashlib, time
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise ValueError("Invalid token format")
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64url_decode(payload_b64))
    # Basic exp check (seconds since epoch)
    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and time.time() > float(exp):
        raise ValueError("Token expired")
    return payload


def create_access_token(user_id: int, email: str) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
    }
    if _HAS_PYJWT:
        return _pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)  # type: ignore
    return _jwt_fallback_encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_id: int, email: str) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(days=REFRESH_TTL_DAYS)).timestamp()),
    }
    if _HAS_PYJWT:
        return _pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)  # type: ignore
    return _jwt_fallback_encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    if _HAS_PYJWT:
        return _pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])  # type: ignore
    return _jwt_fallback_decode(token, JWT_SECRET, algorithms=[JWT_ALG])


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


def _verify_signed_value(signed: str) -> Optional[str]:
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



from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from db import get_session
from models import User
from utils.security import hash_password, verify_password
from extensions import limiter, rate_limit_auth, login_manager
from services.emailer import send_email, can_send_email


bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")

_USERNAME_MIN = 3
_USERNAME_MAX = 24
_USERNAME_ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789_")
_USERNAME_RESERVED = {
    "admin", "root", "support", "help", "about", "terms", "privacy",
    "settings", "account", "auth", "login", "logout", "register", "me",
    "api", "static", "assets",
}


def _normalize_username(raw: str) -> str:
    s = (raw or "").strip().lower()
    # Replace common separators with underscore, then strip invalid chars.
    s = s.replace(" ", "_").replace("-", "_").replace(".", "_")
    s = "".join(ch for ch in s if ch in _USERNAME_ALLOWED)
    # Collapse multiple underscores
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def _username_is_valid(u: str) -> bool:
    if not u:
        return False
    if len(u) < _USERNAME_MIN or len(u) > _USERNAME_MAX:
        return False
    if u in _USERNAME_RESERVED:
        return False
    return all(ch in _USERNAME_ALLOWED for ch in u)


def _derive_username_from_email(email: str) -> str:
    local = (email or "").split("@")[0]
    u = _normalize_username(local)
    return u[:_USERNAME_MAX]


def _suggest_usernames(base: str):
    base = _normalize_username(base)
    base = base[:_USERNAME_MAX]
    if not base:
        base = "user"
    # Keep suggestions short and tap-friendly on mobile.
    return [
        base,
        (base[: max(0, _USERNAME_MAX - 2)] + "01")[:_USERNAME_MAX],
        (base[: max(0, _USERNAME_MAX - 5)] + "_music")[:_USERNAME_MAX],
    ]


def _reset_serializer():
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="ahoy-password-reset")


def _reset_token_for_user(user: User) -> str:
    # Include a stable “version” derived from password_hash so tokens are invalidated on password change.
    pwv = (user.password_hash or "")[:20]
    return _reset_serializer().dumps({"uid": int(user.id), "v": pwv})


def _verify_reset_token(token: str, max_age_seconds: int = 3600):
    data = _reset_serializer().loads(token, max_age=max_age_seconds)
    uid = int(data.get("uid"))
    v = str(data.get("v") or "")
    return uid, v


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    with get_session() as db_session:
        user = db_session.get(User, int(user_id))
        return user


@bp.post("/register")
@limiter.limit(rate_limit_auth)
def register():
    """Register new user with Flask sessions"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    username_raw = (data.get("username") or "").strip()
    username = _normalize_username(username_raw) if username_raw else _derive_username_from_email(email)
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400
    if not username:
        username = "user"
    if not _username_is_valid(username):
        return jsonify({
            "error": "invalid_username",
            "message": f"Username must be {_USERNAME_MIN}-{_USERNAME_MAX} chars, using letters/numbers/underscore.",
            "suggestions": _suggest_usernames(username or email.split("@")[0])
        }), 400

    pw_hash = hash_password(password)

    try:
        with get_session() as db_session:
            # Ensure uniqueness (case-insensitive) with a small suffix loop.
            base = username
            if base in _USERNAME_RESERVED or not _username_is_valid(base):
                base = _derive_username_from_email(email) or "user"
                base = base[:_USERNAME_MAX]

            candidate = base
            n = 0
            while True:
                exists = db_session.query(User.id).filter(func.lower(User.username) == candidate.lower()).first()
                if not exists:
                    break
                n += 1
                suffix = str(n)
                candidate = (base[: max(0, _USERNAME_MAX - len(suffix))] + suffix)[:_USERNAME_MAX]
                if n > 999:
                    return jsonify({"error": "username_unavailable"}), 409

            user = User(
                email=email,
                password_hash=pw_hash,
                username=candidate,
                display_name=(data.get("display_name") or "").strip() or candidate
            )
            db_session.add(user)
            db_session.flush()  # get user.id

            # Log user in with Flask-Login
            login_user(user, remember=True)

            # Optional welcome email (non-blocking)
            try:
                if can_send_email() and user.email:
                    send_email(
                        user.email,
                        subject="Welcome to Ahoy ✨",
                        text=(
                            "You just claimed your Ahoy account — welcome!\n\n"
                            f"Your username: @{user.username}\n\n"
                            "Tip: Save tracks, build playlists, and make your profile yours.\n"
                        ),
                    )
            except Exception:
                pass

            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name,
                    "avatar_url": user.avatar_url
                }
            }), 201
    except IntegrityError:
        # Could be email or username uniqueness
        return jsonify({"error": "account_already_exists"}), 409
    except Exception as e:
        return jsonify({"error": "registration_failed", "detail": str(e)}), 500


@bp.post("/password-reset/request")
@limiter.limit("5/minute")
def password_reset_request():
    """Request a password reset email.

    Security:
    - Always returns success to avoid user enumeration.
    - Rate limited.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    # Always respond success (do not leak whether the email exists).
    ok_resp = jsonify({"success": True, "message": "If that email exists, we sent a reset link."})
    if not email or "@" not in email:
        return ok_resp, 200

    if not can_send_email():
        # Still return success; operator can enable RESEND_API_KEY/SMTP later.
        return ok_resp, 200

    try:
        with get_session() as db_session:
            user = db_session.query(User).filter(User.email == email).first()
            if not user:
                return ok_resp, 200

            token = _reset_token_for_user(user)
            # Prefer an explicit BASE_URL in production (prevents host-header shenanigans).
            import os
            base = (os.getenv("BASE_URL") or "").rstrip("/")
            if not base:
                # Render/Gunicorn behind proxy: these headers are set by the platform.
                if request.headers.get("X-Forwarded-Proto") and request.headers.get("X-Forwarded-Host"):
                    base = f"{request.headers.get('X-Forwarded-Proto')}://{request.headers.get('X-Forwarded-Host')}"
                else:
                    base = request.url_root.rstrip("/")
            reset_link = f"{base}/auth/reset?token={token}"

            subject = "Reset your Ahoy password"
            text = (
                "We got a request to reset your Ahoy password.\n\n"
                f"Reset it here (link expires in 1 hour):\n{reset_link}\n\n"
                "If you didn’t request this, you can ignore this email."
            )
            send_email(user.email, subject=subject, text=text)
    except Exception:
        # Never leak details; keep response stable.
        pass

    return ok_resp, 200


@bp.post("/password-reset/confirm")
@limiter.limit("10/minute")
def password_reset_confirm():
    """Confirm password reset with token + new password."""
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("password") or ""
    if not token or len(new_password) < 8:
        return jsonify({"error": "invalid_request"}), 400

    try:
        uid, v = _verify_reset_token(token, max_age_seconds=3600)
    except SignatureExpired:
        return jsonify({"error": "token_expired"}), 400
    except BadSignature:
        return jsonify({"error": "invalid_token"}), 400
    except Exception:
        return jsonify({"error": "invalid_token"}), 400

    with get_session() as db_session:
        user = db_session.get(User, uid)
        if not user:
            return jsonify({"error": "invalid_token"}), 400
        pwv = (user.password_hash or "")[:20]
        if pwv != v:
            # Password already changed (or token invalidated)
            return jsonify({"error": "invalid_token"}), 400

        user.password_hash = hash_password(new_password)
        db_session.commit()

    return jsonify({"success": True})


@bp.post("/login")
@limiter.limit(rate_limit_auth)
def login():
    """Login with Flask sessions"""
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or data.get("email") or data.get("username") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "identifier_and_password_required"}), 400

    with get_session() as db_session:
        ident_l = identifier.strip().lower()
        if "@" in ident_l:
            user = db_session.query(User).filter(User.email == ident_l).first()
        else:
            uname = _normalize_username(ident_l)
            # Prefer username match; if user hasn't been backfilled yet, fall back to email-local-part match.
            user = db_session.query(User).filter(func.lower(User.username) == uname).first()
            if not user:
                user = db_session.query(User).filter(User.email.like(f"{uname}@%")).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        # Log user in with Flask-Login
        login_user(user, remember=True)

        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }
        })


@bp.post("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({"success": True})


@bp.get("/me")
@login_required
def me():
    """Get current user info"""
    return jsonify({
        "user": {
            "id": current_user.id,
            "username": getattr(current_user, "username", None),
            "email": current_user.email,
            "display_name": current_user.display_name,
            "avatar_url": getattr(current_user, "avatar_url", None)
        }
    })


@bp.get("/username-available")
@limiter.limit(rate_limit_auth)
def username_available():
    """Lightweight username availability check for the UI."""
    username = _normalize_username(request.args.get("username", ""))
    if not _username_is_valid(username):
        return jsonify({
            "available": False,
            "username": username,
            "error": "invalid_username",
            "suggestions": _suggest_usernames(username),
        }), 200
    with get_session() as db_session:
        exists = db_session.query(User.id).filter(func.lower(User.username) == username.lower()).first()
        return jsonify({
            "available": not bool(exists),
            "username": username,
            "suggestions": _suggest_usernames(username),
        }), 200


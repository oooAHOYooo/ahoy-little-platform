from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError

from db import get_session
from models import User
from utils.auth import create_access_token, create_refresh_token, jwt_required, decode_token
from utils.security import hash_password, verify_password
from extensions import limiter, rate_limit_auth


bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
@limiter.limit(rate_limit_auth)
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    pw_hash = hash_password(password)

    try:
        with get_session() as session:
            user = User(email=email, password_hash=pw_hash)
            session.add(user)
            session.flush()  # get user.id
            access = create_access_token(user.id, user.email)
            refresh = create_refresh_token(user.id, user.email)
            return jsonify({
                "user": {"id": user.id, "email": user.email},
                "access_token": access,
                "refresh_token": refresh,
            }), 201
    except IntegrityError:
        return jsonify({"error": "email_already_registered"}), 409


@bp.post("/login")
@limiter.limit(rate_limit_auth)
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    with get_session() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        access = create_access_token(user.id, user.email)
        refresh = create_refresh_token(user.id, user.email)
        return jsonify({
            "user": {"id": user.id, "email": user.email},
            "access_token": access,
            "refresh_token": refresh,
        })


@bp.get("/me")
@jwt_required
def me():
    # g.jwt is set by jwt_required
    return jsonify({
        "user": {"id": int(g.jwt.get("sub")), "email": g.jwt.get("email")}
    })


@bp.post("/refresh")
def refresh():
    data = request.get_json(silent=True) or {}
    token = (data.get("refresh_token") or "").strip()
    if not token:
        return jsonify({"error": "refresh_token_required"}), 400
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return jsonify({"error": "invalid_token_type"}), 401
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        # Issue new access token
        new_access = create_access_token(user_id, email)
        return jsonify({"access_token": new_access})
    except Exception as e:
        return jsonify({"error": "invalid_token", "detail": str(e)}), 401



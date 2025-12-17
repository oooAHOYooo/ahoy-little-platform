from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from db import get_session
from models import User
from utils.security import hash_password, verify_password
from extensions import limiter, rate_limit_auth, login_manager


bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")


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
    username = (data.get("username") or email.split("@")[0]).strip()
    password = data.get("password") or ""
    
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    pw_hash = hash_password(password)

    try:
        with get_session() as db_session:
            user = User(
                email=email,
                password_hash=pw_hash,
                display_name=username
            )
            db_session.add(user)
            db_session.flush()  # get user.id
            
            # Log user in with Flask-Login
            login_user(user, remember=True)
            
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name
                }
            }), 201
    except IntegrityError:
        return jsonify({"error": "email_already_registered"}), 409
    except Exception as e:
        return jsonify({"error": "registration_failed", "detail": str(e)}), 500


@bp.post("/login")
@limiter.limit(rate_limit_auth)
def login():
    """Login with Flask sessions"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    with get_session() as db_session:
        user = db_session.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        # Log user in with Flask-Login
        login_user(user, remember=True)
        
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name
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
            "email": current_user.email,
            "display_name": current_user.display_name
        }
    })



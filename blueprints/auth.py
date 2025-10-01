from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, UserMixin
from werkzeug.exceptions import BadRequest
import json, os
from extensions import bcrypt, login_manager

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
USERS_PATH = os.path.join("data", "users_auth.json")

class User(UserMixin):
    def __init__(self, username, pw_hash):
        self.id = username
        self.pw_hash = pw_hash

def _load_users():
    if not os.path.exists(USERS_PATH):
        return {}
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def _save_users(users):
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

@login_manager.user_loader
def load_user(user_id):
    users = _load_users()
    rec = users.get(user_id)
    return User(user_id, rec["pw_hash"]) if rec else None

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        raise BadRequest("username and password required")
    users = _load_users()
    if username in users:
        return jsonify({"error": "username_taken"}), 409
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    users[username] = {"pw_hash": pw_hash}
    _save_users(users)
    
    # Also create user in user_manager for playlist functionality
    try:
        from user_manager import user_manager
        # Check if user already exists in user_manager
        existing_user = user_manager.get_user(username)
        if not existing_user:
            user_manager.create_user(username, f"{username}@example.com", password)
    except Exception as e:
        # Don't fail registration if user_manager fails
        print(f"Warning: Failed to create user in user_manager: {e}")
    
    return jsonify({"ok": True})

@bp.get("/login")
def login_page():
    """Handle GET requests to login page (redirects from login_required)"""
    return jsonify({"error": "login_required", "message": "Please log in to access this resource"}), 401

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    users = _load_users()
    rec = users.get(username)
    if not rec or not bcrypt.check_password_hash(rec["pw_hash"], password):
        return jsonify({"error": "invalid_credentials"}), 401
    login_user(User(username, rec["pw_hash"]), remember=True)
    return jsonify({"ok": True, "user": {"username": username}})

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})
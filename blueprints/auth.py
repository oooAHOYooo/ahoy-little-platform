from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.exceptions import BadRequest
import json, os
from extensions import bcrypt, login_manager, limiter
from utils.security import hash_password, verify_password
from utils.email_auth import send_verification_email, send_reset_email, verify_token

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
    pw_hash = hash_password(password)
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
    if not rec or not verify_password(password, rec["pw_hash"]):
        return jsonify({"error": "invalid_credentials"}), 401
    login_user(User(username, rec["pw_hash"]), remember=True)
    return jsonify({"ok": True, "user": {"username": username}})

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})

# Email verification routes
@bp.post("/request-verify")
@limiter.limit("3 per minute")
def request_verification():
    """Send email verification"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get user email (assuming it's stored in user data)
    users = _load_users()
    user_data = users.get(current_user.id, {})
    user_email = user_data.get('email', f"{current_user.id}@example.com")
    
    if send_verification_email(user_email, current_user.id):
        return jsonify({"message": "Verification email sent"})
    else:
        return jsonify({"error": "Failed to send verification email"}), 500

@bp.get("/verify")
def verify_email():
    """Verify email with token"""
    token = request.args.get('token')
    if not token:
        return render_template('auth.html', error="Invalid verification link")
    
    payload = verify_token(token, 'verification')
    if not payload:
        return render_template('auth.html', error="Invalid or expired verification link")
    
    # Mark user as verified (you'd update your user model here)
    users = _load_users()
    if payload['user_id'] in users:
        users[payload['user_id']]['verified'] = True
        _save_users(users)
        return render_template('auth.html', message="Email verified successfully!")
    
    return render_template('auth.html', error="User not found")

@bp.post("/forgot")
@limiter.limit("3 per minute")
def forgot_password():
    """Send password reset email"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    users = _load_users()
    if username not in users:
        # Don't reveal if user exists
        return jsonify({"message": "If the account exists, a reset email has been sent"})
    
    user_email = users[username].get('email', f"{username}@example.com")
    
    if send_reset_email(user_email, username):
        return jsonify({"message": "If the account exists, a reset email has been sent"})
    else:
        return jsonify({"error": "Failed to send reset email"}), 500

@bp.get("/reset")
def reset_password_form():
    """Show password reset form"""
    token = request.args.get('token')
    if not token:
        return render_template('auth.html', error="Invalid reset link")
    
    payload = verify_token(token, 'reset')
    if not payload:
        return render_template('auth.html', error="Invalid or expired reset link")
    
    return render_template('auth.html', reset_token=token)

@bp.post("/reset")
@limiter.limit("3 per minute")
def reset_password():
    """Reset password with token"""
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    new_password = data.get('password', '').strip()
    
    if not token or not new_password:
        return jsonify({"error": "Token and password required"}), 400
    
    payload = verify_token(token, 'reset')
    if not payload:
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    username = payload['user_id']
    users = _load_users()
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Update password
    users[username]['pw_hash'] = hash_password(new_password)
    _save_users(users)
    
    return jsonify({"message": "Password reset successfully"})
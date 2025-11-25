import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

bcrypt = Bcrypt()
login_manager = LoginManager()

# Initialize limiter with environment-driven defaults
rate_limit_default = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")
rate_limit_auth = os.getenv("RATE_LIMIT_AUTH", "10 per minute")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[rate_limit_default]
)

def init_cors(app):
    # Default allowed origins for Ahoy Indie Media
    default_allowed = [
        "https://app.ahoy.ooo",
        "https://api.ahoy.ooo",
        "http://localhost:5173",
        "http://localhost:5000",
    ]
    # Merge with any origins provided via env/config
    extra = app.config.get("CORS_ORIGINS") or []
    # Deduplicate while preserving order
    allowed_origins = list(dict.fromkeys(default_allowed + extra))

    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["Content-Type"],
        max_age=86400,  # help browsers cache preflight
    )
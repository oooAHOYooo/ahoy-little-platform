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
    if app.config.get("CORS_ORIGINS"):
        CORS(app, resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "supports_credentials": True,
            }
        })
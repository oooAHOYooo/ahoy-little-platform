import os

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-not-secret")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_TYPE = "filesystem"
    REMEMBER_COOKIE_HTTPONLY = True
    JSON_SORT_KEYS = False
    RATELIMIT_DEFAULT = "200/hour"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else []

class ProdConfig(BaseConfig):
    RATELIMIT_DEFAULT = "600/hour"

class DevConfig(BaseConfig):
    pass

def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return ProdConfig if env == "production" else DevConfig
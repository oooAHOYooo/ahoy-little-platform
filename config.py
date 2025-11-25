import os

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-not-secret")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Only use secure cookies in production (HTTPS required)
    # In development (HTTP), secure cookies won't work
    SESSION_COOKIE_SECURE = os.environ.get("AHOY_ENV", "sandbox").lower() == "production"
    REMEMBER_COOKIE_SECURE = os.environ.get("AHOY_ENV", "sandbox").lower() == "production"
    SESSION_TYPE = "filesystem"
    REMEMBER_COOKIE_HTTPONLY = True
    JSON_SORT_KEYS = False
    RATELIMIT_DEFAULT = "200/hour"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else []
    # Square defaults (overridden in env-specific configs)
    SQUARE_ENV = os.environ.get("AHOY_ENV", "sandbox").lower()
    SQUARE_APPLICATION_ID = os.environ.get("SQUARE_APPLICATION_ID_SANDBOX", "")
    SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN_SANDBOX", "")

class ProductionConfig(BaseConfig):
    RATELIMIT_DEFAULT = "600/hour"
    SQUARE_ENV = "production"
    SQUARE_APPLICATION_ID = os.environ.get("SQUARE_APPLICATION_ID_PRODUCTION", "")
    SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN_PRODUCTION", "")
    SQUARE_LOCATION_ID = os.environ.get("SQUARE_LOCATION_ID_PRODUCTION", "")

class SandboxConfig(BaseConfig):
    SQUARE_ENV = "sandbox"
    SQUARE_APPLICATION_ID = os.environ.get("SQUARE_APPLICATION_ID_SANDBOX", "")
    SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN_SANDBOX", "")
    SQUARE_LOCATION_ID = os.environ.get("SQUARE_LOCATION_ID_SANDBOX", "")

def get_config():
    # AHOY_ENV determines payment environment targeting
    env = os.environ.get("AHOY_ENV", "sandbox").lower()
    if env == "production":
        return ProductionConfig
    return SandboxConfig
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
    # Stripe configuration (test vs live based on AHOY_ENV)
    # If AHOY_ENV == "development" (or "sandbox"), use *_TEST keys. Otherwise use live keys.
    _AHOY_ENV = os.environ.get("AHOY_ENV", "development").lower()
    _USE_TEST_KEYS = _AHOY_ENV in ("development", "sandbox")
    STRIPE_PUBLISHABLE_KEY = os.environ.get(
        "STRIPE_PUBLISHABLE_KEY_TEST" if _USE_TEST_KEYS else "STRIPE_PUBLISHABLE_KEY",
        ""
    )
    STRIPE_SECRET_KEY = os.environ.get(
        "STRIPE_SECRET_KEY_TEST" if _USE_TEST_KEYS else "STRIPE_SECRET_KEY",
        ""
    )
    STRIPE_WEBHOOK_SECRET = os.environ.get(
        "STRIPE_WEBHOOK_SECRET_TEST" if _USE_TEST_KEYS else "STRIPE_WEBHOOK_SECRET",
        ""
    )

class ProductionConfig(BaseConfig):
    RATELIMIT_DEFAULT = "600/hour"
    pass

class SandboxConfig(BaseConfig):
    pass

def get_config():
    # AHOY_ENV determines payment environment targeting
    env = os.environ.get("AHOY_ENV", "sandbox").lower()
    if env == "production":
        return ProductionConfig
    return SandboxConfig
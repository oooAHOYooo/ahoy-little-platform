import logging
import os
from typing import Optional
from urllib.parse import urljoin

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

log = logging.getLogger(__name__)


def _norm_env(value: Optional[str]) -> str:
    v = (value or "").strip().lower()
    # Back-compat: older docs used "sandbox" to mean non-production.
    if v in ("", "sandbox", "dev"):
        return "development"
    return v


def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    if v in ("1", "true", "t", "yes", "y", "on"):
        return True
    if v in ("0", "false", "f", "no", "n", "off"):
        return False
    return default


def get_base_url() -> str:
    """Best-effort public origin for link generation.

    Rules:
    - If BASE_URL is set, use it.
    - Else if AHOY_ENV != production, default to http://localhost:5000
    - Else (production): warn and infer from request context when available.
    """
    base = (os.getenv("BASE_URL") or "").strip().rstrip("/")
    if base:
        return base

    env = _norm_env(os.getenv("AHOY_ENV"))
    if env != "production":
        return "http://localhost:5000"

    # Production without BASE_URL: only infer if we're in a request context.
    try:
        from flask import has_request_context, request  # type: ignore
    except Exception:
        has_request_context = None  # type: ignore
        request = None  # type: ignore

    if has_request_context and has_request_context() and request is not None:
        proto = request.headers.get("X-Forwarded-Proto")
        host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host")
        if proto and host:
            inferred = f"{proto}://{host}".rstrip("/")
        else:
            inferred = request.url_root.rstrip("/")
        log.warning("BASE_URL not set in production; inferring public origin as %s", inferred)
        return inferred

    log.warning("BASE_URL not set in production and no request context is available; links may be relative.")
    return ""


def public_url(path: str) -> str:
    """Join BASE_URL + path into a public absolute URL (best-effort)."""
    path = (path or "").strip()
    if not path:
        return get_base_url() or ""
    if path.startswith("http://") or path.startswith("https://"):
        return path

    base = get_base_url()
    if not base:
        # Last-resort: keep relative if we can't compute a base.
        return path if path.startswith("/") else f"/{path}"
    # urljoin handles querystrings and avoids double slashes.
    return urljoin(f"{base}/", path.lstrip("/"))

class BaseConfig:
    # SECRET_KEY is REQUIRED in production - fail fast if missing
    AHOY_ENV = _norm_env(os.environ.get("AHOY_ENV"))
    if AHOY_ENV == "production":
        SECRET_KEY = os.environ.get("SECRET_KEY")
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is REQUIRED in production!")
    else:
        SECRET_KEY = os.environ.get("SECRET_KEY", "dev-not-secret-change-in-production")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    # Only use secure cookies in production (HTTPS required)
    # In development (HTTP), secure cookies won't work
    SESSION_COOKIE_SECURE = _parse_bool(
        os.environ.get("SESSION_COOKIE_SECURE"),
        default=(AHOY_ENV == "production"),
    )
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    # URL helpers (used for password reset email links, etc.)
    BASE_URL = os.environ.get("BASE_URL") or ""

    # Server-side sessions: Redis/Valkey if REDIS_URL is present; filesystem otherwise.
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "ahoy:sess:"
    _redis_url = (os.environ.get("REDIS_URL") or "").strip()
    if _redis_url:
        SESSION_TYPE = "redis"
        if redis is None:
            raise RuntimeError("REDIS_URL is set but the 'redis' package is not installed.")
        SESSION_REDIS = redis.from_url(_redis_url)
    else:
        SESSION_TYPE = "filesystem"  # Great for local dev; not for multi-instance prod
    REMEMBER_COOKIE_HTTPONLY = True
    JSON_SORT_KEYS = False
    # Static file caching (1 year for immutable assets)
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year in seconds
    RATELIMIT_DEFAULT = "200/hour"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else []
    # Stripe configuration (test vs live based on AHOY_ENV)
    # If AHOY_ENV == "development" (or "sandbox"), use *_TEST keys. Otherwise use live keys.
    _AHOY_ENV = _norm_env(os.environ.get("AHOY_ENV"))
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
    env = _norm_env(os.environ.get("AHOY_ENV"))
    if env == "production":
        return ProductionConfig
    return SandboxConfig
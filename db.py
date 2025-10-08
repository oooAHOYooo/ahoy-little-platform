import os
import logging
from contextlib import contextmanager
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import make_url


def _require_database_url() -> str:
    """Get DB URL, falling back to local SQLite for dev if not set.

    Order of precedence:
    - DATABASE_URL (production/Render)
    - LOCAL_DATABASE_URL (optional override for local dev)
    - sqlite:///local.db (default local file)
    """
    value = os.getenv("DATABASE_URL")
    if value:
        return value
    value = os.getenv("LOCAL_DATABASE_URL")
    if value:
        return value
    # Default local fallback
    return "sqlite:///local.db"


def _ensure_ssl_for_remote(url: str) -> str:
    parsed = urlsplit(url)
    # Skip SSL tweaks for SQLite/local file URLs
    if (parsed.scheme or "").startswith("sqlite"):
        return url
    host = (parsed.hostname or "").lower()
    is_local = host in {"localhost", "127.0.0.1", "::1"}
    if is_local:
        return url

    query_pairs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query_pairs:
        query_pairs["sslmode"] = "require"
        new_query = urlencode(query_pairs)
        parsed = parsed._replace(query=new_query)
        return urlunsplit(parsed)
    return url


def current_db_dsn_summary() -> str:
    """Return a masked DSN like 'postgresql+psycopg://<user>@<host>/<db>?sslmode=require'."""
    try:
        effective_url = _ensure_ssl_for_remote(_require_database_url())
        url = make_url(effective_url)
        driver = url.drivername or ""
        host = url.host or ""
        database = url.database or ""

        # Only include explicitly safe query keys
        safe_keys = {"sslmode"}
        safe_query_items = [(k, v) for k, v in (url.query or {}).items() if k in safe_keys]
        query_suffix = ""
        if safe_query_items:
            query_suffix = "?" + urlencode(safe_query_items)

        return f"{driver}://<user>@{host}/{database}{query_suffix}"
    except Exception:
        return "<db url unavailable>"


# Build effective DATABASE_URL (fail fast and enforce SSL for remote hosts)
RAW_DATABASE_URL = _require_database_url()
EFFECTIVE_DATABASE_URL = _ensure_ssl_for_remote(RAW_DATABASE_URL)

# Log a masked version for visibility
logger = logging.getLogger(__name__)
logger.info("Using database", extra={"dsn": current_db_dsn_summary()})

# Create SQLAlchemy engine with pool_pre_ping for resiliency
engine = create_engine(
    EFFECTIVE_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Thread-safe scoped session factory
SessionFactory = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations.

    Usage:
        with get_session() as session:
            session.query(...)
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()



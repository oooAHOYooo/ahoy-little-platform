import os
from typing import Optional

try:
    # Delay import until used to avoid hard dependency at import time
    from square.client import Client  # type: ignore
except Exception:
    Client = None  # type: ignore

def get_square_client(app=None):
    """
    Return a configured Square Client using environment derived from AHOY_ENV.
    - AHOY_ENV=sandbox -> Square sandbox
    - AHOY_ENV=production -> Square production
    Reads credentials from Flask config if available, else from environment variables.
    """
    if Client is None:
        # Import lazily to give a clearer error if the SDK isn't installed
        try:
            from square.client import Client as _Client  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Square Python SDK is not installed. Install with: pip install squareup"
            ) from exc
        global Client  # type: ignore
        Client = _Client  # type: ignore

    # Prefer Flask app config if available
    cfg = None
    if app is not None:
        cfg = getattr(app, "config", None)
    else:
        try:
            from flask import current_app  # type: ignore
            cfg = current_app.config
        except Exception:
            cfg = None

    square_env = None
    access_token = None

    if cfg:
        square_env = (cfg.get("SQUARE_ENV") or os.getenv("AHOY_ENV", "sandbox")).lower()
        access_token = cfg.get("SQUARE_ACCESS_TOKEN")
    else:
        square_env = os.getenv("AHOY_ENV", "sandbox").lower()
        if square_env == "production":
            access_token = os.getenv("SQUARE_ACCESS_TOKEN_PRODUCTION")
        else:
            access_token = os.getenv("SQUARE_ACCESS_TOKEN_SANDBOX")

    if not access_token:
        raise RuntimeError("Square access token not configured for current environment")

    if square_env not in ("sandbox", "production"):
        square_env = "sandbox"

    client = Client(
        access_token=access_token,
        environment=square_env,  # 'sandbox' or 'production'
    )
    return client



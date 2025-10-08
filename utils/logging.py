import logging
import json
import sys
import time
import uuid
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Include optional structured fields when present
        for key in ("path", "method", "status", "duration_ms", "trace_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def setup_json_logging() -> None:
    # Configure root logger to emit JSON to stdout
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    # Clear existing handlers to avoid duplicate logs
    logger.handlers = [handler]


def init_request_logging(app) -> None:
    from flask import g, request

    @app.before_request
    def _start_timer():
        g.__log_start = time.perf_counter()
        # Use incoming trace header or generate one
        g.__trace_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex

    @app.after_request
    def _log_request(response):
        try:
            start = getattr(g, "__log_start", None)
            duration_ms = None
            if start is not None:
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
            extra = {
                "path": request.path,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "trace_id": getattr(g, "__trace_id", None),
            }
            app.logger.info("request", extra=extra)
        finally:
            return response



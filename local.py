#!/usr/bin/env python3
"""
Local development server launcher with automatic browser opening.
Similar to app.py but opens browser automatically.
"""

import os
import socket
import subprocess
import shutil
import sys
import webbrowser
import time
import threading

# Import app module functions
import app as app_module
from app import create_app

def _is_port_free(p: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", p))
        return True
    except OSError:
        return False

def _wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be ready by checking if we can connect"""
    import urllib.request
    import urllib.error
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False

def open_browser_after_delay(url: str, delay: float = 2.0):
    """Open browser after a short delay to let server start"""
    def _open():
        time.sleep(delay)
        print(f"🌐 Opening browser at {url}")
        webbrowser.open(url)
    
    threading.Thread(target=_open, daemon=True).start()

if __name__ == "__main__":
    # 1) Ensure DB migrations are applied (best-effort for local dev)
    try:
        alembic_bin = shutil.which("alembic")
        if alembic_bin:
            print("⚙️  Applying migrations (alembic upgrade head)…")
            env = os.environ.copy()
            # Ensure PYTHONPATH includes project root so alembic/env.py can import models
            project_root = os.path.dirname(os.path.abspath(__file__))
            env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH','')}" if env.get('PYTHONPATH') else project_root
            # Provide a sane default DATABASE_URL for local runs
            env.setdefault("DATABASE_URL", "sqlite:///local.db")
            subprocess.run([alembic_bin, "upgrade", "head"], check=True, env=env)
        else:
            print("⚠️  Alembic not found in PATH; skipping automatic migrations.")
    except Exception as e:
        print(f"⚠️  Migrations step skipped: {e}")

    # 2) Pick a free port automatically if requested is busy
    requested = int(os.getenv("PORT", "5000"))
    chosen = requested
    if not _is_port_free(requested):
        alt = app_module.find_available_port(5001, 5010)
        if alt:
            print(f"⚠️  Port {requested} busy — starting on {alt}")
            chosen = alt
        else:
            print(f"⚠️  Port {requested} busy and no alternates free in 5001-5010. Trying {requested} anyway…")

    # 3) Create app instance
    app = create_app()
    
    # 4) Determine URL
    url = f"http://127.0.0.1:{chosen}"
    
    # 5) Schedule browser opening
    open_browser_after_delay(url, delay=2.0)

    # 6) Run with gunicorn if available for parity; else Flask dev server
    gunicorn_bin = shutil.which("gunicorn")
    if gunicorn_bin:
        print(f"🚀 Starting gunicorn on port {chosen}…")
        print(f"🌐 Browser will open at {url}")
        # Use the same interface as Render's script but single worker for local
        os.execv(gunicorn_bin, ["gunicorn", "app:app", "--workers", "2", "--threads", "4", "--timeout", "120", "-b", f"0.0.0.0:{chosen}"])
    else:
        print(f"🚀 Starting Flask dev server on {url}")
        print(f"🌐 Browser will open automatically...")
        app.run(port=chosen, host="127.0.0.1", use_reloader=False)


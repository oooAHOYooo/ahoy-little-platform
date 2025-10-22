#!/usr/bin/env python3
"""
Desktop launcher for Ahoy Indie Media
PyInstaller-friendly entrypoint with URL and port support
"""

import os
import sys
import argparse
import threading
import time
import socket
import webbrowser


def _wait_for_port(host: str, port: int, timeout_seconds: int = 30) -> bool:
    """Wait for a port to become available"""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def run_server(port: int):
    """Start Flask server in background thread"""
    # Ensure production-ish defaults for desktop
    os.environ.setdefault("FLASK_ENV", "production")
    os.environ.setdefault("PORT", str(port))

    # Import app only after env is set
    from app import app  # noqa: WPS433 (import inside function is intentional)

    app.run(host="127.0.0.1", port=port, use_reloader=False)


def main():
    """Main desktop application entrypoint"""
    parser = argparse.ArgumentParser(description="Ahoy Indie Media Desktop App")
    parser.add_argument(
        "--url", 
        help="Production URL to open (e.g., https://your-app.onrender.com)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=17600,
        help="Local port for Flask server (default: 17600)"
    )
    
    args = parser.parse_args()
    
    # Determine URL to use
    if args.url:
        # Use production URL
        url = args.url.rstrip('/')
        print(f"Opening production URL: {url}")
    else:
        # Start local Flask server
        port = args.port
        print(f"Starting local server on port {port}")
        
        # Start Flask server in background thread
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()
        
        # Wait for server to become ready
        if not _wait_for_port("127.0.0.1", port, timeout_seconds=30):
            print(f"Server failed to start on port {port}")
            sys.exit(1)
        
        url = f"http://127.0.0.1:{port}"
        print(f"Server ready at {url}")

    # Open desktop window using pywebview (soft dependency)
    try:
        import webview  # type: ignore
    except ImportError as e:
        print("pywebview is not installed. Run: pip install pywebview")
        print(f"Import error: {e}")
        print("Falling back to system browser...")
        webbrowser.open(url)
        return

    # Create and start webview window
    webview.create_window(
        title="Ahoy Indie Media",
        url=url,
        width=1200,
        height=800,
        min_size=(1200, 800),
        resizable=True,
        confirm_close=True,
    )
    webview.start()


if __name__ == "__main__":
    main()



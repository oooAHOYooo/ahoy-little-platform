import os
import threading
import time
import socket


def _wait_for_port(host: str, port: int, timeout_seconds: int = 30) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def run_server():
    # Ensure production-ish defaults for desktop
    os.environ.setdefault("FLASK_ENV", "production")
    os.environ.setdefault("PORT", "17600")

    # Import app only after env is set
    from app import app  # noqa: WPS433 (import inside function is intentional)

    port = int(os.getenv("PORT", "17600"))
    app.run(host="127.0.0.1", port=port, use_reloader=False)


def main():
    port = int(os.getenv("PORT", "17600"))

    # Start Flask server in background thread
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # Wait for server to become ready
    if not _wait_for_port("127.0.0.1", port, timeout_seconds=30):
        print(f"Server failed to start on port {port}")
        return

    # Open desktop window using pywebview (soft dependency)
    try:
        import webview  # type: ignore
    except Exception as e:  # pragma: no cover
        print("pywebview is not installed. Run: pip install pywebview")
        print(f"Import error: {e}")
        return

    webview.create_window(
        title="Ahoy Indie Media",
        url=f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        resizable=True,
        confirm_close=True,
    )
    webview.start()


if __name__ == "__main__":
    main()



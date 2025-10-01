# cli.py — simple runner for CI and local dev
import os
import argparse
from app import create_app  # make sure create_app() exists in app.py

def main():
    parser = argparse.ArgumentParser(description="Run Ahoy server")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    # CI tries port 5001; default to 5001 when CI or AHOY_TEST_MODE is set
    default_port = int(os.getenv("PORT", "5001" if (os.getenv("CI") or os.getenv("AHOY_TEST_MODE")) else "5000"))
    parser.add_argument("--port", type=int, default=default_port)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_app()
    # signal test mode to the app if needed
    if os.getenv("CI") or os.getenv("AHOY_TEST_MODE"):
        app.config["TESTING"] = True

    print(f"🚀 Ahoy server starting on http://{args.host}:{args.port} (testing={app.config.get('TESTING', False)})", flush=True)

    # IMPORTANT for CI: no reloader
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)

if __name__ == "__main__":
    main()

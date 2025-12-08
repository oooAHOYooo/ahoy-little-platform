#!/usr/bin/env python3
"""
Developer convenience launcher.

- Kills any previous dev server (python app.py, flask, or gunicorn app:app)
- Starts a fresh instance of app.py on PORT=5000 (or $PORT if set)
- Waits until the server is reachable
- Opens the default browser to the running app
"""
from __future__ import annotations

import os
import platform
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from contextlib import closing

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = int(os.environ.get("PORT", "5000"))


def _run(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=False, cwd=REPO_ROOT,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _is_port_open(port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def kill_previous(port: int) -> None:
    system = platform.system()
    patterns = [
        "python app.py",
        "python3 app.py",
        "flask run",
        "gunicorn app:app",
    ]
    if system in ("Darwin", "Linux"):
        for pat in patterns:
            _run(f"pkill -f {shlex.quote(pat)}")
        _run(f"lsof -ti tcp:{port} | xargs kill -9 2>/dev/null")
    elif system == "Windows":
        for pat in patterns:
            _run(
                'wmic process where "CommandLine like \'%{}%\'" call terminate'
                .format(pat.replace('"', ''))
            )
        _run(f"netstat -ano | findstr :{port} | for /f %a in ('more') do taskkill /PID %a /F")
    else:
        for pat in patterns:
            _run(f"pkill -f {shlex.quote(pat)}")

    # Allow the OS to free the port
    for _ in range(20):
        if not _is_port_open(port):
            break
        time.sleep(0.1)


def start_server(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["PORT"] = str(port)
    python_bin = sys.executable or "python3"
    cmd = [python_bin, "-u", "app.py"]
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def wait_for_http(port: int, timeout_s: float = 12.0) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        if _is_port_open(port):
            return
        time.sleep(0.2)


def maybe_parse_port_from_output(line: str) -> int | None:
    m = re.search(r":(\d{2,5})", line)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def main() -> int:
    # Do NOT kill anything; just emulate `python app.py` and open a browser.
    port = DEFAULT_PORT
    print("🚀 Starting app.py (no process killing)…")
    proc = start_server(port)

    # Track port in case app picks an alternate
    chosen_port = port
    t0 = time.time()
    while time.time() - t0 < 4.0:
        try:
            line = proc.stdout.readline()
        except Exception:
            break
        if not line:
            break
        sys.stdout.write(line)
        sys.stdout.flush()
        detected = maybe_parse_port_from_output(line)
        if detected:
            chosen_port = detected
            break

    wait_for_http(chosen_port)

    url = f"http://127.0.0.1:{chosen_port}"
    print(f"🌐 Opening {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Visit: {url}")

    # Stream logs to current terminal until Ctrl+C
    try:
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n🛑 Stopping dev server…")
        if proc.poll() is None:
            if platform.system() == "Windows":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



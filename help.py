#!/usr/bin/env python3
"""
Ahoy dev helper: start dev server, check status, track todos from TODOS.md.

Usage:
  python help.py              # show help and quick status
  python help.py start        # start dev server (runs dev.py)
  python help.py status       # check server, git, and env
  python help.py todos        # list todos from TODOS.md
  python help.py todos add "thing to do"
  python help.py todos done 1 # mark item 1 done (updates TODOS.md)
"""
from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
TODOS_FILE = PROJECT_ROOT / "TODOS.md"
PORT_RANGE = (5000, 5020)  # 5000 + 5001..5020


def _probe(port: int, path: str = "/healthz", timeout: float = 1.0) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def find_server_port() -> int | None:
    """Return first port in range that responds to /healthz, or None."""
    for port in range(PORT_RANGE[0], PORT_RANGE[1] + 1):
        if _probe(port):
            return port
    return None


def cmd_start(_args: argparse.Namespace) -> int:
    """Start the dev server (runs dev.py)."""
    dev_py = PROJECT_ROOT / "dev.py"
    if not dev_py.exists():
        print("dev.py not found", file=sys.stderr)
        return 1
    os.chdir(PROJECT_ROOT)
    # Replace current process so Ctrl+C etc. work
    os.execv(sys.executable, [sys.executable, str(dev_py)])
    return 0  # unreachable


def cmd_status(_args: argparse.Namespace) -> int:
    """Check dev server, git status, and env."""
    port = find_server_port()
    if port is not None:
        print(f"Server: running at http://127.0.0.1:{port}")
        if _probe(port, "/readyz"):
            print("Ready: DB connectivity OK (/readyz)")
        else:
            print("Ready: /readyz failed (DB or app issue)")
    else:
        print("Server: not running (ports 5000–5020)")
        print("  Start with: python help.py start  or  python dev.py")

    # Git
    git_dir = PROJECT_ROOT / ".git"
    if git_dir.exists():
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            print("Git: uncommitted changes")
            for line in r.stdout.strip().splitlines()[:8]:
                print(f"  {line}")
            if r.stdout.count("\n") >= 8:
                print("  ...")
        else:
            print("Git: clean (or no changes)")
    else:
        print("Git: no repo")

    # Env
    if os.getenv("DATABASE_URL"):
        print("Env: DATABASE_URL set")
    else:
        print("Env: DATABASE_URL not set (defaults may apply)")
    return 0


def _read_todos() -> list[tuple[bool, str]]:
    """Parse TODOS.md into list of (done, text)."""
    if not TODOS_FILE.exists():
        return []
    text = TODOS_FILE.read_text(encoding="utf-8")
    out: list[tuple[bool, str]] = []
    for line in text.splitlines():
        m = re.match(r"^(\s*[-*]\s+)\[([ xX])\]\s+(.*)$", line)
        if m:
            out.append((m.group(2).lower() == "x", m.group(3).strip()))
    return out


def _write_todos(items: list[tuple[bool, str]]) -> None:
    """Write TODOS.md from list of (done, text). Preserve header if present."""
    lines: list[str] = []
    if TODOS_FILE.exists():
        intro = []
        for line in TODOS_FILE.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\s*[-*]\s+\[[ xX]\]", line):
                break
            intro.append(line)
        if intro:
            lines.extend(intro)
            if intro[-1].strip() and not intro[-1].endswith("\n"):
                lines.append("")
    for done, text in items:
        lines.append(f"- [{'x' if done else ' '}] {text}")
    TODOS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_todos(args: argparse.Namespace) -> int:
    """List, add, or mark todos."""
    items = _read_todos()

    if args.todo_action == "list" or args.todo_action is None:
        if not items:
            if not TODOS_FILE.exists():
                print("No TODOS.md yet. Create it or run: python help.py todos add \"Your first task\"")
            else:
                print("No checklist items in TODOS.md (use '- [ ] task' format).")
            return 0
        for i, (done, text) in enumerate(items, 1):
            mark = "[x]" if done else "[ ]"
            print(f"  {i}. {mark} {text}")
        return 0

    if args.todo_action == "add":
        text = " ".join(getattr(args, "extra", None) or []).strip()
        if not text:
            print("Usage: python help.py todos add \"task description\"", file=sys.stderr)
            return 1
        items.append((False, text))
        _write_todos(items)
        print(f"Added: {text}")
        return 0

    if args.todo_action == "done":
        extra = getattr(args, "extra", None) or []
        try:
            idx = int(extra[0]) if extra else 0
        except (ValueError, IndexError):
            print("Usage: python help.py todos done <number>", file=sys.stderr)
            return 1
        if idx < 1 or idx > len(items):
            print(f"Invalid index. Use 1–{len(items)}", file=sys.stderr)
            return 1
        items[idx - 1] = (True, items[idx - 1][1])
        _write_todos(items)
        print(f"Marked done: {items[idx - 1][1]}")
        return 0

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ahoy dev helper: start dev, status, todos from TODOS.md",
        epilog="Examples: help.py start | help.py status | help.py todos | help.py todos add \"fix login\" | help.py todos done 1",
    )
    sub = parser.add_subparsers(dest="cmd", help="Command")

    sub.add_parser("start", help="Start dev server (runs dev.py)")

    sub.add_parser("status", help="Check server, git, env")

    t = sub.add_parser("todos", help="List/add/done todos from TODOS.md")
    t.add_argument("todo_action", nargs="?", choices=["list", "add", "done"], default="list")
    t.add_argument("extra", nargs="*", help="For 'add': task text (one or more words). For 'done': item number.")

    args = parser.parse_args()

    if args.cmd is None:
        # No subcommand: show short help and status
        parser.print_help()
        print()
        return cmd_status(args)

    if args.cmd == "start":
        return cmd_start(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "todos":
        return cmd_todos(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

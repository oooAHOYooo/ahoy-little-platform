import argparse

from db import get_session
from models import User


def set_admin(email: str, value: bool) -> int:
    with get_session() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            return 1
        user.is_admin = bool(value)
        print(f"Set is_admin={user.is_admin} for {email} (id={user.id})")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Ahoy admin tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("set-admin", help="toggle admin flag for user")
    p.add_argument("--email", required=True)
    switch = p.add_mutually_exclusive_group(required=True)
    switch.add_argument("--on", action="store_true")
    switch.add_argument("--off", action="store_true")

    args = parser.parse_args()
    if args.cmd == "set-admin":
        return set_admin(args.email, args.on)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



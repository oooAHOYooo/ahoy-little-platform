#!/usr/bin/env python3
"""
Reset all users and create a single test account: alexadmin / alexadmin.

Use for local/dev to start with a clean slate and a known login.
WARNING: Deletes all users and their related data (playlists, bookmarks, etc.).

Usage:
  python scripts/reset_users_and_create_test.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import User
from utils.security import hash_password


TEST_USERNAME = "alexadmin"
TEST_EMAIL = "alexadmin@test.ahoy.ooo"
TEST_PASSWORD = "alexadmin"
TEST_DISPLAY_NAME = "Alex Admin"


def main():
    print("Resetting users and creating test account...")
    with get_session() as session:
        deleted = session.query(User).delete()
        session.commit()
        print(f"Deleted {deleted} user(s).")

        user = User(
            email=TEST_EMAIL,
            username=TEST_USERNAME,
            password_hash=hash_password(TEST_PASSWORD),
            display_name=TEST_DISPLAY_NAME,
        )
        session.add(user)
        session.commit()
        print(f"Created test user: {TEST_USERNAME} (id={user.id})")

    print()
    print("Test login credentials:")
    print(f"  Username or email: {TEST_USERNAME}")
    print(f"  Password:           {TEST_PASSWORD}")
    print()
    print("In the login form you can enter 'alexadmin' in the email field and password 'alexadmin'.")


if __name__ == "__main__":
    main()

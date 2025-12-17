#!/usr/bin/env python3
"""
Create sample user accounts for testing - uses database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import User
from extensions import bcrypt

def create_sample_accounts():
    """Create sample user accounts"""
    
    # Sample accounts data
    sample_accounts = [
        {
            'email': 'musiclover@ahoy.com',
            'password': 'music123',
            'display_name': 'Music Lover',
        },
        {
            'email': 'indie@ahoy.com',
            'password': 'indie123',
            'display_name': 'Indie Explorer',
        },
        {
            'email': 'shows@ahoy.com',
            'password': 'shows123',
            'display_name': 'Show Binger',
        },
        {
            'email': 'new@ahoy.com',
            'password': 'new123',
            'display_name': 'New User',
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for account in sample_accounts:
        try:
            with get_session() as db_session:
                # Check if user already exists
                existing_user = db_session.query(User).filter(User.email == account['email']).first()
                if existing_user:
                    print(f"⚠️  User '{account['email']}' already exists")
                    existing_count += 1
                    continue
                
                # Create the user
                user = User(
                    email=account['email'],
                    password_hash=bcrypt.generate_password_hash(account['password']).decode('utf-8'),
                    display_name=account['display_name']
                )
                db_session.add(user)
                db_session.commit()
                
                print(f"✅ Created user: {account['display_name']} ({account['email']})")
                created_count += 1
                
        except Exception as e:
            print(f"❌ Error creating user '{account['email']}': {e}")
    
    with get_session() as db_session:
        total_users = db_session.query(User).count()
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count} accounts")
    print(f"   Already existed: {existing_count} accounts")
    print(f"   Total users: {total_users}")

if __name__ == '__main__':
    create_sample_accounts()

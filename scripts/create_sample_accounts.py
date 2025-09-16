#!/usr/bin/env python3
"""
Create sample user accounts for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_manager import user_manager

def create_sample_accounts():
    """Create sample user accounts"""
    
    # Sample accounts data
    sample_accounts = [
        {
            'username': 'musiclover',
            'password': 'music123',
            'email': 'musiclover@ahoy.com',
            'display_name': 'Music Lover',
            'bio': 'Passionate about discovering new indie music and supporting emerging artists.'
        },
        {
            'username': 'indieexplorer',
            'password': 'indie123',
            'email': 'indie@ahoy.com',
            'display_name': 'Indie Explorer',
            'bio': 'Always on the hunt for the next great indie discovery.'
        },
        {
            'username': 'showbinger',
            'password': 'shows123',
            'email': 'shows@ahoy.com',
            'display_name': 'Show Binger',
            'bio': 'Love watching live performances and indie shows.'
        },
        {
            'username': 'newuser',
            'password': 'new123',
            'email': 'new@ahoy.com',
            'display_name': 'New User',
            'bio': 'Just getting started with Ahoy Indie Media.'
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for account in sample_accounts:
        try:
            # Check if user already exists
            existing_user = user_manager.get_user(account['username'])
            if existing_user:
                print(f"⚠️  User '{account['username']}' already exists")
                existing_count += 1
                continue
            
            # Create the user
            user_data = user_manager.create_user(
                username=account['username'],
                password=account['password'],
                email=account['email'],
                display_name=account['display_name']
            )
            
            # Update bio
            user_manager.update_user_profile(account['username'], {
                'bio': account['bio']
            })
            
            print(f"✅ Created user: {account['display_name']} (@{account['username']})")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating user '{account['username']}': {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count} accounts")
    print(f"   Already existed: {existing_count} accounts")
    print(f"   Total users: {len(user_manager.users)}")

if __name__ == '__main__':
    create_sample_accounts()

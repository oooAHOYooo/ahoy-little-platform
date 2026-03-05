import os
from db import get_session
from models import User
from utils.security import hash_password

def set_alexmaster_password():
    with get_session() as s:
        # Check if user exists by username or email
        u = s.query(User).filter(User.username == 'alexMaster').first()
        if not u:
            u = s.query(User).filter(User.email == 'alexmaster@example.com').first()
            
        if u:
            u.username = 'alexMaster'
            u.password_hash = hash_password('trustdaL0RD!@#')
            u.is_admin = True
            print("Updated existing alexMaster user.")
        else:
            u = User(
                username='alexMaster',
                email='alexmaster@example.com', # Placeholder email
                password_hash=hash_password('trustdaL0RD!@#'),
                is_admin=True,
                display_name='Alex Master'
            )
            s.add(u)
            print("Created new alexMaster user.")
            
        s.commit()

if __name__ == "__main__":
    set_alexmaster_password()

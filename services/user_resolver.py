from typing import Optional

from flask import session
from flask_login import current_user

from db import get_session
from models import User


def resolve_db_user_id() -> Optional[int]:
    """Best-effort mapping of current session/login to DB user id.

    - If Flask-Login id is an int, use it
    - Else, try session['user_data']['profile']['email'] to find User by email
    """
    try:
        rid = current_user.get_id() if hasattr(current_user, "get_id") else None
        if rid is not None and str(rid).isdigit():
            return int(rid)
    except Exception:
        pass

    try:
        email = (session.get('user_data') or {}).get('profile', {}).get('email')
        if email:
            with get_session() as s:
                u = s.query(User).filter(User.email == email).first()
                if u:
                    return int(u.id)
    except Exception:
        pass
    return None



import datetime as dt
from storage import read_json, write_json

PRODUCTS = "data/products.json"
USERS = "data/users.json"

def _products():
    return read_json(PRODUCTS) or {}

def _users():
    data = read_json(USERS) or {"users": []}
    if "users" not in data: data["users"] = []
    return data

def get_user(username):
    data = _users()
    return next((u for u in data["users"] if u.get("username") == username), None)

def ensure_user(username):
    data = _users()
    u = get_user(username)
    if not u:
        u = {"username": username, "plan": "free", "themes": [], "created_at": dt.datetime.utcnow().isoformat() + "Z"}
        data["users"].append(u)
        write_json(USERS, data)
    return u

def get_limits(plan_name):
    p = _products()
    return (p.get("limits") or {}).get(plan_name or "free") or (p.get("limits") or {}).get("free")

def is_unlimited(val):
    return str(val).lower() == "unlimited"

def can_create_collection(username, current_count):
    user = ensure_user(username)
    limits = get_limits(user.get("plan"))
    cap = limits["max_collections"]
    return is_unlimited(cap) or current_count < int(cap)

def can_create_playlist(username, current_count):
    user = ensure_user(username)
    limits = get_limits(user.get("plan"))
    cap = limits["max_playlists"]
    return is_unlimited(cap) or current_count < int(cap)

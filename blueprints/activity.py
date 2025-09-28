from flask import Blueprint, request, jsonify, session
import os, time, uuid
from storage import read_json, write_json

bp = Blueprint("activity", __name__, url_prefix="/api/activity")

DATA_PATH = os.path.join("data", "user_activity.json")

def _user_bucket(store, username):
    return store.setdefault(username, {"likes": [], "bookmarks": [], "history": []})

@bp.get("/me")
def me_activity():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, username)
    return jsonify(bucket)

@bp.post("/like")
def like_toggle():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()  # track|show|artist
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, username)
    key = f"{kind}:{item_id}"
    if key in bucket["likes"]:
        bucket["likes"].remove(key)
        status = "unliked"
    else:
        bucket["likes"].append(key)
        status = "liked"
    write_json(DATA_PATH, store)
    return jsonify({"ok": True, "status": status, "id": item_id, "kind": kind})

@bp.post("/bookmark")
def bookmark_toggle():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, username)
    key = f"{kind}:{item_id}"
    if key in bucket["bookmarks"]:
        bucket["bookmarks"].remove(key)
        status = "removed"
    else:
        bucket["bookmarks"].append(key)
        status = "bookmarked"
    write_json(DATA_PATH, store)
    return jsonify({"ok": True, "status": status, "id": item_id, "kind": kind})

@bp.post("/played")
def mark_played():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, username)
    bucket["history"].append({
        "id": item_id,
        "kind": kind,
        "ts": int(time.time())
    })
    # keep last 500
    bucket["history"] = bucket["history"][-500:]
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})

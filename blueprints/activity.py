from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import os, time
from storage import read_json, write_json
from extensions import limiter

bp = Blueprint("activity", __name__, url_prefix="/api/activity")
DATA_PATH = os.path.join("data", "user_activity.json")

def _user_bucket(store, username):
    return store.setdefault(username, {"likes": [], "bookmarks": [], "history": []})

@bp.get("/me")
@login_required
def me_activity():
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, current_user.id)
    return jsonify(bucket)

@bp.post("/like")
@limiter.limit("60/minute")
@login_required
def like_toggle():
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, current_user.id)
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
@limiter.limit("60/minute")
@login_required
def bookmark_toggle():
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, current_user.id)
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
@limiter.limit("120/minute")
@login_required
def mark_played():
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, current_user.id)
    bucket["history"].append({"id": item_id, "kind": kind, "ts": int(time.time())})
    bucket["history"] = bucket["history"][-500:]
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})
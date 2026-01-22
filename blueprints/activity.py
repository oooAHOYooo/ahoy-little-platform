from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import os, time
from storage import read_json, write_json
from extensions import limiter
# Removed: gamify service (feature removed)
from services.user_resolver import resolve_db_user_id

bp = Blueprint("activity", __name__, url_prefix="/api/activity")
DATA_PATH = os.path.join("data", "user_activity.json")

def _user_bucket(store, username):
    # Migrate legacy shape that had "likes"
    bucket = store.setdefault(username, {"bookmarks": [], "history": []})
    if "likes" in bucket:
        # fold all likes into bookmarks (idempotent)
        for key in bucket.get("likes", []):
            if key not in bucket["bookmarks"]:
                bucket["bookmarks"].append(key)
        bucket.pop("likes", None)
    return bucket

@bp.get("/me")
@login_required
def me_activity():
    store = read_json(DATA_PATH, {})
    bucket = _user_bucket(store, current_user.id)
    # ensure migration saved
    write_json(DATA_PATH, store)
    return jsonify(bucket)

@bp.post("/bookmark")
@limiter.limit("60/minute")
def bookmark_toggle():
    """Legacy endpoint - redirects to /api/bookmarks for PostgreSQL storage"""
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    
    # Handle both old and new payload formats
    if not item_id and "item" in body:
        item = body.get("item", {})
        item_id = item.get("id", "").strip()
        kind = item.get("type", "track").strip()
    
    if not item_id:
        return jsonify({"error": "missing id"}), 400

    # Map old format to new format
    media_type_map = {
        "track": "music",
        "show": "show",
        "artist": "artist"
    }
    media_type = media_type_map.get(kind, "music")
    
    # For guests, just return success without persisting
    try:
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({"ok": True, "status": "bookmarked", "id": item_id, "kind": kind, "persisted": False})
    except:
        # No current_user available (guest)
        return jsonify({"ok": True, "status": "bookmarked", "id": item_id, "kind": kind, "persisted": False})

    # For logged-in users, use PostgreSQL via /api/bookmarks
    try:
        # Check if bookmark exists
        from db import get_session
        from models import Bookmark
        with get_session() as session:
            existing = (
                session.query(Bookmark)
                .filter(Bookmark.user_id == current_user.id, 
                       Bookmark.media_id == item_id, 
                       Bookmark.media_type == media_type)
                .first()
            )
            
            if existing:
                # Remove bookmark
                session.delete(existing)
                status = "removed"
            else:
                # Add bookmark
                b = Bookmark(user_id=current_user.id, media_id=item_id, media_type=media_type)
                session.add(b)
                status = "bookmarked"
        
        return jsonify({"ok": True, "status": status, "id": item_id, "kind": kind, "persisted": True})
    except Exception as e:
        # Fallback to legacy JSON storage if DB fails
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
        return jsonify({"ok": True, "status": status, "id": item_id, "kind": kind, "persisted": True})

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
    # Removed: gamify hook (feature removed)
    return jsonify({"ok": True})
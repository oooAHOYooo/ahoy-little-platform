from flask import Blueprint, request, jsonify
from uuid import uuid4
from datetime import datetime
from storage import read_json, write_json
from services.plan import can_create_playlist, ensure_user
from services.activity import track_activity

bp = Blueprint("playlists", __name__, url_prefix="/api/playlists")

PLAYLISTS_FILE = "data/playlists.json"
COLLECTIONS_FILE = "data/collections.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _ensure(path, key):
    data = read_json(path) or {key: []}
    if key not in data:
        data[key] = []
    return data

@bp.get("/")
def list_playlists():
    user = request.args.get("user")
    data = _ensure(PLAYLISTS_FILE, "playlists")
    pls = data["playlists"]
    if user:
        pls = [p for p in pls if p.get("owner") == user]
    return jsonify(pls)

@bp.post("/from-collection/<collection_id>")
def create_from_collection(collection_id):
    payload = request.get_json(silent=True) or {}
    owner = (payload.get("owner") or "").strip()
    name  = (payload.get("name")  or "").strip()
    if not owner:
        return jsonify({"error": "owner required"}), 400

    # Count existing playlists for owner
    data_existing = _ensure(PLAYLISTS_FILE, "playlists")
    owner_count = sum(1 for p in data_existing["playlists"] if p.get("owner") == owner)
    if not can_create_playlist(owner, owner_count):
        return jsonify({
            "error": "limit_reached",
            "message": "Free plan allows up to 3 Playlists. Upgrade to Ahoy Plus for unlimited.",
            "paywall": {"plan": "plus", "price_usd": 3.0}
        }), 402

    cols = _ensure(COLLECTIONS_FILE, "collections")["collections"]
    src = next((c for c in cols if c["id"] == collection_id), None)
    if not src:
        return jsonify({"error": "collection not found"}), 404

    data = _ensure(PLAYLISTS_FILE, "playlists")
    new_pl = {
        "id": uuid4().hex,
        "name": name or f'{src["name"]} — Playlist',
        "owner": owner,
        "source_collection": collection_id,
        "items": list(src.get("items", [])),  # shallow clone preserves order
        "is_public": bool(payload.get("is_public", False)),
        "cover_image": payload.get("cover_image") or src.get("cover_image"),
        "created_at": _now(),
        "updated_at": _now(),
    }
    data["playlists"].append(new_pl)
    write_json(PLAYLISTS_FILE, data)
    
    # Track activity
    streak = track_activity(owner, "playlist:create_from_collection")
    
    return jsonify({**new_pl, "streak": streak}), 201

@bp.patch("/<playlist_id>")
def update_playlist(playlist_id):
    payload = request.get_json(silent=True) or {}
    data = _ensure(PLAYLISTS_FILE, "playlists")
    for p in data["playlists"]:
        if p["id"] == playlist_id:
            if "name" in payload: p["name"] = (payload["name"] or "").strip() or p["name"]
            if "is_public" in payload: p["is_public"] = bool(payload["is_public"])
            if "cover_image" in payload: p["cover_image"] = payload["cover_image"]
            if "order" in payload and isinstance(payload["order"], list):
                id_to_item = {i["id"]: i for i in p["items"]}
                p["items"] = [id_to_item[i] for i in payload["order"] if i in id_to_item]
            p["updated_at"] = _now()
            write_json(PLAYLISTS_FILE, data)
            return jsonify(p)
    return jsonify({"error": "not found"}), 404

@bp.post("/<playlist_id>/items")
def add_item(playlist_id):
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("id")
    item_type = payload.get("type")  # 'track' | 'show' | 'episode' | 'clip' …
    if not item_id or not item_type:
        return jsonify({"error": "id and type required"}), 400

    data = _ensure(PLAYLISTS_FILE, "playlists")
    for p in data["playlists"]:
        if p["id"] == playlist_id:
            new_item = {"id": item_id, "type": item_type, "added_at": _now()}
            # no dupes; last write wins (moves to end)
            p["items"] = [i for i in p["items"] if i["id"] != item_id] + [new_item]
            p["updated_at"] = _now()
            write_json(PLAYLISTS_FILE, data)
            return jsonify(p)
    return jsonify({"error": "not found"}), 404

@bp.delete("/<playlist_id>/items/<item_id>")
def remove_item(playlist_id, item_id):
    data = _ensure(PLAYLISTS_FILE, "playlists")
    for p in data["playlists"]:
        if p["id"] == playlist_id:
            before = len(p["items"])
            p["items"] = [i for i in p["items"] if i["id"] != item_id]
            if len(p["items"]) != before:
                p["updated_at"] = _now()
                write_json(PLAYLISTS_FILE, data)
                return jsonify(p)
            return jsonify({"error": "item not in playlist"}), 404
    return jsonify({"error": "not found"}), 404
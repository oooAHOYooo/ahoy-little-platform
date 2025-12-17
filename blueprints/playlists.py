from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from uuid import uuid4
from datetime import datetime
from storage import read_json, write_json
from services.plan import can_create_playlist, ensure_user
from services.activity import track_activity

bp = Blueprint("playlists", __name__, url_prefix="/api/playlists")

PLAYLISTS_FILE = "data/playlists.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _ensure(path, key):
    data = read_json(path, {key: []})
    if key not in data:
        data[key] = []
    return data

@bp.route("/", methods=['GET', 'POST'])
def manage_playlists():
    """Get all playlists or create new playlist - works for both guests and users"""
    if request.method == 'GET':
        user = request.args.get("user")
        data = _ensure(PLAYLISTS_FILE, "playlists")
        pls = data["playlists"]
        if user:
            pls = [p for p in pls if p.get("owner") == user]
        return jsonify(pls)
    
    # POST - Create new playlist
    username = current_user.id if current_user.is_authenticated else None
    
    if username:
        # For logged-in users, use the user_manager system
        try:
            from user_manager import user_manager
            data = request.json
            name = data.get('name')
            description = data.get('description', '')
            color = data.get('color', '#6366f1')
            is_public = data.get('is_public', False)
            
            playlist_id = user_manager.create_playlist(username, name, description, color, is_public)
            
            if playlist_id:
                playlist = user_manager.get_playlist(username, playlist_id)
                return jsonify({'success': True, 'playlist': playlist, 'guest': False})
            else:
                return jsonify({'error': 'Failed to create playlist'}), 400
        except ImportError:
            # Fallback to file-based storage if user_manager not available
            pass
    
    # For guests or fallback, use file-based storage
    data = request.json
    playlist_id = str(__import__('uuid').uuid4())
    playlist = {
        'id': playlist_id,
        'name': data.get('name'),
        'description': data.get('description', ''),
        'color': data.get('color', '#6366f1'),
        'is_public': False,  # Guests can't create public playlists
        'created_at': _now(),
        'updated_at': _now(),
        'tracks': [],
        'shows': [],
        'artists': [],
        'total_items': 0,
        'cover_art': None,
        'tags': [],
        'is_guest': True,
        'items': []
    }
    
    file_data = _ensure(PLAYLISTS_FILE, "playlists")
    file_data["playlists"].append(playlist)
    write_json(PLAYLISTS_FILE, file_data)
    
    return jsonify({'success': True, 'playlist': playlist, 'guest': True})


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
    item_type = payload.get("type") or payload.get("kind")  # accept both
    if not item_id or not item_type:
        return jsonify({"error": "id and type required"}), 400

    username = current_user.id if current_user.is_authenticated else None
    
    if username:
        # For logged-in users, use the user_manager system (same as main app)
        try:
            from user_manager import user_manager
            playlist = user_manager.get_playlist(username, playlist_id)
            if not playlist:
                return jsonify({"error": "not found"}), 404
            
            # Add item to playlist
            success = user_manager.add_to_playlist(username, playlist_id, item_type, item_id, {})
            if success:
                updated_playlist = user_manager.get_playlist(username, playlist_id)
                return jsonify(updated_playlist), 200
            else:
                return jsonify({"error": "failed to add item"}), 400
        except ImportError:
            # Fallback to file-based storage if user_manager not available
            pass
    
    # For guests or fallback, use file-based storage
    data = _ensure(PLAYLISTS_FILE, "playlists")
    for p in data["playlists"]:
        if p["id"] == playlist_id:
            p.setdefault("items", [])
            # move-to-end if exists
            p["items"] = [i for i in p["items"] if i.get("id") != item_id] + [{
                "id": item_id, "type": item_type, "added_at": _now(), "data": {}
            }]
            p["updated_at"] = _now()
            # also keep totals in sync for tests that read them
            p["total_items"] = len(p["items"])
            write_json(PLAYLISTS_FILE, data)
            return jsonify(p), 200
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
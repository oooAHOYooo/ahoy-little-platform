from flask import Blueprint, request, jsonify, session
import os, uuid
from storage import read_json, write_json

bp = Blueprint("playlists", __name__, url_prefix="/api/playlists")
DATA_PATH = os.path.join("data", "playlists.json")

def _user_lists(store, username):
    return store.setdefault(username, {"lists": []})

def _find_list(user_data, pid):
    for p in user_data["lists"]:
        if p["id"] == pid:
            return p
    return None

@bp.get("")
def list_playlists():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    return jsonify(user_data["lists"])

@bp.post("")
def create_playlist():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    description = (body.get("description") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    pid = str(uuid.uuid4())[:8]
    user_data["lists"].append({"id": pid, "name": name, "description": description, "items": []})
    write_json(DATA_PATH, store)
    return jsonify({"ok": True, "id": pid})

@bp.put("/<pid>")
def rename_playlist(pid):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    description = (body.get("description") or "").strip()
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    pl = _find_list(user_data, pid)
    if not pl: return jsonify({"error": "not_found"}), 404
    if name: pl["name"] = name
    pl["description"] = description
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})

@bp.post("/<pid>/items")
def add_item(pid):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    pl = _find_list(user_data, pid)
    if not pl: return jsonify({"error": "not_found"}), 404
    key = f"{kind}:{item_id}"
    if key not in pl["items"]:
        pl["items"].append(key)
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})

@bp.delete("/<pid>/items")
def remove_item(pid):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    body = request.get_json(silent=True) or {}
    item_id = (body.get("id") or "").strip()
    kind = (body.get("kind") or "track").strip()
    if not item_id:
        return jsonify({"error": "missing id"}), 400
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    pl = _find_list(user_data, pid)
    if not pl: return jsonify({"error": "not_found"}), 404
    key = f"{kind}:{item_id}"
    pl["items"] = [k for k in pl["items"] if k != key]
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})

@bp.delete("/<pid>")
def delete_playlist(pid):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
        
    store = read_json(DATA_PATH, {})
    user_data = _user_lists(store, username)
    before = len(user_data["lists"])
    user_data["lists"] = [p for p in user_data["lists"] if p["id"] != pid]
    if len(user_data["lists"]) == before:
        return jsonify({"error": "not_found"}), 404
    write_json(DATA_PATH, store)
    return jsonify({"ok": True})

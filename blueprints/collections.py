from flask import Blueprint, request, jsonify
from storage import read_json, write_json
from datetime import datetime
import os

bp = Blueprint("collections", __name__, url_prefix="/api/collections")
COLLECTIONS_FILE = os.getenv("AHOY_COLLECTIONS_PATH", "data/collections.json")

def _now(): return datetime.utcnow().isoformat()

def _load():
    data = read_json(COLLECTIONS_FILE, {"collections": []})
    if "collections" not in data:
        data["collections"] = []
    return data

@bp.get("/")
def list_collections():
    user = request.args.get("user")
    data = _load()
    cols = data["collections"]
    if user:
        cols = [c for c in cols if c.get("owner") == user]
    return jsonify(cols), 200

@bp.post("/")
def create_collection():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    owner = (payload.get("owner") or "").strip()
    if not name or not owner:
        return jsonify({"error": "name and owner required"}), 400
    data = _load()
    newc = {
        "id": f"col-{len(data['collections'])+1}",
        "name": name,
        "owner": owner,
        "items": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    data["collections"].append(newc)
    write_json(COLLECTIONS_FILE, data)
    return jsonify(newc), 201

@bp.post("/<cid>/items")
def add_item(cid):
    payload = request.get_json(silent=True) or {}
    item_id = payload.get("id")
    item_type = payload.get("type") or payload.get("kind")  # accept both
    if not item_id or not item_type:
        return jsonify({"error": "id and type required"}), 400
    data = _load()
    for c in data["collections"]:
        if c["id"] == cid:
            # no dupes; move to end
            c["items"] = [i for i in c["items"] if i["id"] != item_id] + [{"id": item_id, "type": item_type, "added_at": _now()}]
            c["updated_at"] = _now()
            write_json(COLLECTIONS_FILE, data)
            return jsonify(c), 200
    return jsonify({"error": "not found"}), 404
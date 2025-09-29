# blueprints/bookmarks.py
from flask import Blueprint, request, jsonify, session, render_template
from pathlib import Path
import json, time

bp = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")
DATA_PATH = Path("data/bookmarks.json")

def _load():
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {"users": {}}

def _save(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _uid():
    username = session.get("username")
    if username:
        return f"user:{username}"
    return None

@bp.get("")
def list_bookmarks():
    uid = _uid()
    if not uid:
        return jsonify({"items": [], "persisted": False})
    data = _load()
    items = data["users"].get(uid, {}).get("items", {})
    return jsonify({"items": list(items.values()), "persisted": True})

@bp.post("")
def upsert_or_toggle():
    payload = request.get_json(force=True) or {}
    action = payload.get("action")
    item = payload.get("item") or {}
    key = item.get("key")
    if not key:
        return jsonify({"error": "missing key"}), 400

    uid = _uid()
    if not uid:
        # guest: client stores locally; server just acknowledges
        return jsonify({"items": [item], "persisted": False})

    data = _load()
    user = data["users"].setdefault(uid, {"items": {}})
    exists = key in user["items"]

    if action == "remove" or (action == "toggle" and exists):
        user["items"].pop(key, None)
    else:
        item.setdefault("added_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        user["items"][key] = item

    _save(data)
    return jsonify({"items": list(user["items"].values()), "persisted": True})

@bp.post("/merge")
def merge_from_client():
    uid = _uid()
    if not uid:
        return jsonify({"error": "not-logged-in"}), 401

    incoming = (request.get_json(force=True) or {}).get("items", [])
    data = _load()
    user = data["users"].setdefault(uid, {"items": {}})

    for it in incoming:
        k = it.get("key")
        if not k: 
            continue
        user["items"][k] = {**user["items"].get(k, {}), **it}

    _save(data)
    return jsonify({"items": list(user["items"].values()), "persisted": True})

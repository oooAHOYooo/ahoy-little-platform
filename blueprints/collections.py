from flask import Blueprint, request, jsonify, session
from uuid import uuid4
from datetime import datetime
import hashlib
from storage import read_json, write_json
from services.plan import can_create_collection, ensure_user
from services.activity import track_activity

bp = Blueprint("collections", __name__, url_prefix="/api/collections")

COLLECTIONS_FILE = "data/collections.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _ensure_store():
    data = read_json(COLLECTIONS_FILE) or {"collections": []}
    if "collections" not in data:
        data["collections"] = []
    return data

def auth_required(f):
    """Simple auth decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route("/", methods=['GET', 'POST'])
@auth_required
def collections():
    """Get all collections or create new collection"""
    username = session.get('username')
    
    if request.method == 'POST':
        data = request.get_json() or {}
        owner = username  # Use session username as owner
        
        # Enforce cap
        all_data = _ensure_store()
        owner_count = sum(1 for c in all_data["collections"] if c.get("owner") == owner)
        if not can_create_collection(owner, owner_count):
            return jsonify({
                "error": "limit_reached",
                "message": "Free plan allows up to 3 Collections. Upgrade to Ahoy Plus for unlimited.",
                "paywall": {"plan": "plus", "price_usd": 3.0}
            }), 402  # Payment Required
        
        # Create collection
        collection = {
            'id': uuid4().hex,
            'name': data.get('name'),
            'description': data.get('description', ''),
            'type': data.get('type', 'mixed'),  # mixed, music, shows, artists
            'owner': owner,
            'created_at': _now(),
            'updated_at': _now(),
            'items': [],
            'tags': data.get('tags', [])
        }
        
        all_data["collections"].append(collection)
        write_json(COLLECTIONS_FILE, all_data)
        
        # Track activity
        streak = track_activity(owner, "collection:create")
        
        return jsonify({'success': True, 'collection': collection, 'streak': streak})
    
    # GET - return user's collections
    all_data = _ensure_store()
    user_collections = [c for c in all_data["collections"] if c.get("owner") == username]
    return jsonify(user_collections)

@bp.route("/<collection_id>/items", methods=['POST'])
@auth_required
def add_item_to_collection(collection_id):
    """Add item to collection"""
    username = session.get('username')
    data = request.get_json() or {}
    
    all_data = _ensure_store()
    collection = next((c for c in all_data["collections"] if c["id"] == collection_id and c.get("owner") == username), None)
    
    if not collection:
        return jsonify({"error": "Collection not found"}), 404
    
    item = {
        "id": data.get("id"),
        "type": data.get("type"),
        "added_at": _now(),
        "data": data.get("data", {})
    }
    
    # Remove duplicates and add new item
    collection["items"] = [i for i in collection["items"] if i["id"] != item["id"]] + [item]
    collection["updated_at"] = _now()
    
    # Track activity
    streak = track_activity(username, "collection:add_item")
    
    write_json(COLLECTIONS_FILE, all_data)
    return jsonify({"success": True, "collection": collection, "streak": streak})

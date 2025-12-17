from flask import Blueprint, jsonify
from storage import read_json
from services.radio_sync import get_synced_radio_state
import os

bp = Blueprint("radio_sync", __name__, url_prefix="/api/radio")

def load_tracks():
    """Load tracks from static/data/music.json"""
    try:
        # Assuming app is running from root, path is static/data/music.json
        filepath = os.path.join('static', 'data', 'music.json')
        data = read_json(filepath, {'tracks': []})
        return data.get('tracks', [])
    except Exception:
        return []

@bp.route("/sync")
def sync_radio():
    """
    Returns the current global radio state.
    Use this to sync the frontend player.
    """
    tracks = load_tracks()
    state = get_synced_radio_state(tracks)
    
    if not state:
        return jsonify({"error": "No tracks available"}), 404
        
    return jsonify(state)


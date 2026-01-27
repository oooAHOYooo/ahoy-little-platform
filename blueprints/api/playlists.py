from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import asc, func

from db import get_session
from models import Playlist, PlaylistItem
from utils.api_helpers import ALLOWED_MEDIA_TYPES, parse_pagination


bp = Blueprint("api_playlists", __name__, url_prefix="/api/playlists")


def require_owner(playlist: Playlist, user_id: int):
    if not playlist:
        return None, (jsonify({"error": "not_found"}), 404)
    if playlist.user_id != user_id:
        return None, (jsonify({"error": "forbidden"}), 403)
    return playlist, None


@bp.post("")
def create_playlist():
    """Create playlist - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400

    user_id = current_user.id
    with get_session() as session:
        playlist = Playlist(user_id=user_id, name=name)
        session.add(playlist)
        session.flush()
        return jsonify({"id": playlist.id, "name": playlist.name}), 201


@bp.get("")
@login_required
def list_playlists():
    user_id = current_user.id
    page, per_page, offset = parse_pagination()
    with get_session() as session:
        total = session.query(func.count(Playlist.id)).filter(Playlist.user_id == user_id).scalar() or 0
        rows = (
            session.query(Playlist)
            .filter(Playlist.user_id == user_id)
            .order_by(asc(Playlist.created_at))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        items = [{"id": p.id, "name": p.name, "created_at": p.created_at.isoformat()} for p in rows]
        return jsonify({"items": items, "page": page, "per_page": per_page, "total": total})


@bp.get("/<int:playlist_id>")
def get_playlist(playlist_id: int):
    """Get playlist - public playlists visible to guests"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    
    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        return jsonify({
            "id": playlist.id,
            "name": playlist.name,
            "created_at": playlist.created_at.isoformat(),
            "updated_at": playlist.updated_at.isoformat() if playlist.updated_at else None,
        })


@bp.patch("/<int:playlist_id>")
def rename_playlist(playlist_id: int):
    """Rename playlist - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        playlist.name = name
        return jsonify({"id": playlist.id, "name": playlist.name})


@bp.delete("/<int:playlist_id>")
def delete_playlist(playlist_id: int):
    """Delete playlist - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        session.delete(playlist)
        return jsonify({"ok": True})


@bp.get("/<int:playlist_id>/items")
def list_items(playlist_id: int):
    """List playlist items - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    user_id = current_user.id
    page, per_page, offset = parse_pagination()
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        total = session.query(func.count(PlaylistItem.id)).filter(PlaylistItem.playlist_id == playlist_id).scalar() or 0
        rows = (
            session.query(PlaylistItem)
            .filter(PlaylistItem.playlist_id == playlist_id)
            .order_by(asc(PlaylistItem.position))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        items = [
            {
                "id": it.id,
                "media_id": it.media_id,
                "media_type": it.media_type,
                "position": it.position,
                "added_at": it.added_at.isoformat(),
            }
            for it in rows
        ]
        return jsonify({"items": items, "page": page, "per_page": per_page, "total": total})


@bp.post("/<int:playlist_id>/items")
def add_item(playlist_id: int):
    """Add item to playlist - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    data = request.get_json(silent=True) or {}
    media_id = (data.get("media_id") or "").strip()
    media_type = (data.get("media_type") or "").strip()
    position = data.get("position")
    if not media_id or media_type not in ALLOWED_MEDIA_TYPES:
        return jsonify({"error": "invalid_media"}), 400

    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err

        if position is None:
            # Append to end
            max_pos = session.query(func.max(PlaylistItem.position)).filter(PlaylistItem.playlist_id == playlist_id).scalar()
            position = (max_pos or 0) + 1
        else:
            try:
                position = int(position)
            except Exception:
                return jsonify({"error": "invalid_position"}), 400
            if position < 1:
                return jsonify({"error": "invalid_position"}), 400

        item = PlaylistItem(
            playlist_id=playlist_id,
            media_id=media_id,
            media_type=media_type,
            position=position,
        )
        session.add(item)
        session.flush()
        return jsonify({
            "id": item.id,
            "media_id": item.media_id,
            "media_type": item.media_type,
            "position": item.position,
        }), 201


@bp.patch("/<int:playlist_id>/items/<int:item_id>")
def reorder_item(playlist_id: int, item_id: int):
    """Reorder playlist item - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    data = request.get_json(silent=True) or {}
    position = data.get("position")
    if position is None:
        return jsonify({"error": "position_required"}), 400
    try:
        position = int(position)
    except Exception:
        return jsonify({"error": "invalid_position"}), 400
    if position < 1:
        return jsonify({"error": "invalid_position"}), 400

    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        item = session.get(PlaylistItem, item_id)
        if not item or item.playlist_id != playlist_id:
            return jsonify({"error": "not_found"}), 404
        item.position = position
        return jsonify({"id": item.id, "position": item.position})


@bp.delete("/<int:playlist_id>/items/<int:item_id>")
def remove_item(playlist_id: int, item_id: int):
    """Remove item from playlist - requires login"""
    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401
    user_id = current_user.id
    with get_session() as session:
        playlist = session.get(Playlist, playlist_id)
        playlist, err = require_owner(playlist, user_id)
        if err:
            return err
        item = session.get(PlaylistItem, item_id)
        if not item or item.playlist_id != playlist_id:
            return jsonify({"error": "not_found"}), 404
        session.delete(item)
        return jsonify({"ok": True})



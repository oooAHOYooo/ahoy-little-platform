from flask import Blueprint, request, jsonify, g
from sqlalchemy import desc, func

from db import get_session
from models import Bookmark
from utils.auth import jwt_required


bp = Blueprint("api_bookmarks", __name__, url_prefix="/api/bookmarks")

ALLOWED_MEDIA_TYPES = {"music", "show", "artist", "clip"}


def parse_pagination():
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 50))
    except Exception:
        per_page = 50
    per_page = max(1, min(per_page, 100))
    offset = (page - 1) * per_page
    return page, per_page, offset


@bp.get("")
@jwt_required
def list_bookmarks():
    user_id = int(g.jwt.get("sub"))
    page, per_page, offset = parse_pagination()
    with get_session() as session:
        total = session.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user_id).scalar() or 0
        rows = (
            session.query(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .order_by(desc(Bookmark.created_at))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        items = [
            {
                "id": b.id,
                "media_id": b.media_id,
                "media_type": b.media_type,
                "created_at": b.created_at.isoformat(),
            }
            for b in rows
        ]
        return jsonify({"items": items, "page": page, "per_page": per_page, "total": total})


@bp.post("")
@jwt_required
def add_bookmark():
    data = request.get_json(silent=True) or {}
    media_id = (data.get("media_id") or "").strip()
    media_type = (data.get("media_type") or "").strip()
    if not media_id or media_type not in ALLOWED_MEDIA_TYPES:
        return jsonify({"error": "invalid_media"}), 400
    user_id = int(g.jwt.get("sub"))
    with get_session() as session:
        # idempotent per user+media
        existing = (
            session.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.media_id == media_id, Bookmark.media_type == media_type)
            .first()
        )
        if existing:
            return jsonify({
                "id": existing.id,
                "media_id": existing.media_id,
                "media_type": existing.media_type,
                "created_at": existing.created_at.isoformat(),
            })
        b = Bookmark(user_id=user_id, media_id=media_id, media_type=media_type)
        session.add(b)
        session.flush()
        return jsonify({"id": b.id, "media_id": b.media_id, "media_type": b.media_type}), 201


@bp.delete("/<int:bookmark_id>")
@jwt_required
def remove_bookmark(bookmark_id: int):
    user_id = int(g.jwt.get("sub"))
    with get_session() as session:
        b = session.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user_id).first()
        if not b:
            return jsonify({"error": "not_found"}), 404
        session.delete(b)
        return jsonify({"ok": True})



from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import select, func

from db import get_session
from models import ArtistTip


bp = Blueprint("tips_api", __name__, url_prefix="/api")


def _require_int_user_id() -> int:
    raw = current_user.get_id()
    try:
        return int(raw)
    except Exception:
        return -1


@bp.get("/tips")
@login_required
def get_tips():
    """Get user's tipping history"""
    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    with get_session() as session:
        # Get all tips for user, ordered by most recent
        tips = session.execute(
            select(ArtistTip)
            .where(ArtistTip.user_id == user_id)
            .order_by(ArtistTip.created_at.desc())
            .limit(100)
        ).scalars().all()

        tips_list = [
            {
                "id": tip.id,
                "artist_name": tip.artist_name,
                "amount": tip.amount,
                "created_at": tip.created_at.isoformat(),
                "note": tip.note
            }
            for tip in tips
        ]

        return jsonify({"tips": tips_list})


@bp.post("/tips")
@login_required
def create_tip():
    """Create a new tip"""
    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    data = request.get_json(silent=True) or {}
    artist_name = (data.get("artist_name") or "").strip()
    amount = data.get("amount")

    if not artist_name:
        return jsonify({"error": "artist_name is required"}), 400

    if not amount or not isinstance(amount, int) or amount < 1:
        return jsonify({"error": "amount must be a positive integer (in cents)"}), 400

    note = (data.get("note") or "").strip()[:500]  # Limit to 500 chars

    with get_session() as session:
        tip = ArtistTip(
            user_id=user_id,
            artist_name=artist_name,
            amount=amount,
            note=note if note else None,
            created_at=datetime.utcnow()
        )
        session.add(tip)
        session.flush()

        return jsonify({
            "id": tip.id,
            "artist_name": tip.artist_name,
            "amount": tip.amount,
            "created_at": tip.created_at.isoformat(),
            "note": tip.note
        }), 201


@bp.get("/tips/history")
@login_required
def get_tipping_history():
    """Get user's tipping history (grouped by artist)"""
    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    with get_session() as session:
        # Get tips grouped by artist
        history = session.execute(
            select(
                ArtistTip.artist_name,
                func.sum(ArtistTip.amount).label("total_amount"),
                func.count(ArtistTip.id).label("tip_count"),
                func.max(ArtistTip.created_at).label("last_tip_date")
            )
            .where(ArtistTip.user_id == user_id)
            .group_by(ArtistTip.artist_name)
            .order_by(func.sum(ArtistTip.amount).desc())
        ).all()

        history_list = [
            {
                "artist_name": row.artist_name,
                "total_amount": row.total_amount,
                "tip_count": row.tip_count,
                "last_tip_date": row.last_tip_date.isoformat() if row.last_tip_date else None
            }
            for row in history
        ]

        total_all = sum(p["total_amount"] for p in history_list)

        return jsonify({
            "history": history_list,
            "total_all": total_all,
            "artist_count": len(history_list)
        })




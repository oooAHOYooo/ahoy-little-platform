from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from decimal import Decimal
from datetime import datetime, timedelta
from db import get_session
from models import UserArtistPosition, Tip
from services.user_resolver import resolve_db_user_id
import json
import os

bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


def load_json_data(filename, default=None):
    """Load JSON data from static/data directory"""
    try:
        filepath = os.path.join('static', 'data', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default or {}


def get_artist_name(artist_id):
    """Get artist name from artists.json by slug or id"""
    artists_data = load_json_data('artists.json', {'artists': []})
    for artist in artists_data.get('artists', []):
        if artist.get('slug') == artist_id or artist.get('id') == artist_id or artist.get('name') == artist_id:
            return artist.get('name', artist_id)
    return artist_id  # Fallback to ID if not found


@bp.route("")
# @login_required  # Disabled for development
def portfolio_page():
    """Portfolio page showing user's creative positions"""
    return render_template("portfolio.html")


@bp.route("/data")
# @login_required  # Disabled for development
def portfolio_data():
    """Get portfolio data for charts and tables"""
    user_id = resolve_db_user_id()
    if not user_id:
        # Return empty data for development (login disabled)
        return jsonify({
            "total_contributed": 0,
            "position_count": 0,
            "positions": [],
            "timeline": [],
            "pie_data": [],
            "top_artists": [],
        }), 200

    try:
        with get_session() as db_session:
            # Get all positions for user
            positions = db_session.query(UserArtistPosition).filter(
                UserArtistPosition.user_id == user_id
            ).order_by(UserArtistPosition.total_contributed.desc()).all()

            # Calculate totals
            total_contributed = sum(float(pos.total_contributed) for pos in positions)
            
            # Build positions data with artist names
            positions_data = []
            for pos in positions:
                artist_name = get_artist_name(pos.artist_id)
                weight = (float(pos.total_contributed) / total_contributed * 100) if total_contributed > 0 else 0
                positions_data.append({
                    "artist_id": pos.artist_id,
                    "artist_name": artist_name,
                    "total_contributed": float(pos.total_contributed),
                    "weight": round(weight, 2),
                    "last_boost": pos.boost_datetime.isoformat() if pos.boost_datetime else None,
                    "created_at": pos.created_at.isoformat(),
                })

            # Get timeline data (contributions over time)
            boosts = db_session.query(Tip).filter(
                Tip.user_id == user_id
            ).order_by(Tip.created_at.asc()).all()

            # Group by date
            timeline_data = {}
            for boost in boosts:
                date_key = boost.created_at.date().isoformat()
                if date_key not in timeline_data:
                    timeline_data[date_key] = 0
                timeline_data[date_key] += float(boost.boost_amount)

            # Convert to sorted list
            timeline_list = [
                {"date": date, "amount": amount}
                for date, amount in sorted(timeline_data.items())
            ]

            # Pie chart data (contributions by artist)
            pie_data = [
                {
                    "artist_id": pos.artist_id,
                    "artist_name": get_artist_name(pos.artist_id),
                    "amount": float(pos.total_contributed),
                }
                for pos in positions
            ]

            # Get top 3 artists for widget
            top_artists = positions_data[:3] if len(positions_data) >= 3 else positions_data

            return jsonify({
                "total_contributed": round(total_contributed, 2),
                "position_count": len(positions),
                "positions": positions_data,
                "timeline": timeline_list,
                "pie_data": pie_data,
                "top_artists": top_artists,
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/widget-data")
def portfolio_widget_data():
    """Get portfolio widget data (for navbar) - works without login for display"""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"total_invested": 0, "top_artists": []}), 200

    try:
        with get_session() as db_session:
            positions = db_session.query(UserArtistPosition).filter(
                UserArtistPosition.user_id == user_id
            ).order_by(UserArtistPosition.total_contributed.desc()).limit(3).all()

            total_contributed = sum(float(pos.total_contributed) for pos in positions)
            
            top_artists = [
                {
                    "artist_id": pos.artist_id,
                    "artist_name": get_artist_name(pos.artist_id),
                    "total_contributed": float(pos.total_contributed),
                }
                for pos in positions
            ]

            return jsonify({
                "total_invested": round(total_contributed, 2),
                "top_artists": top_artists,
            }), 200

    except Exception as e:
        return jsonify({"total_invested": 0, "top_artists": []}), 200


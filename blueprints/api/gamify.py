from datetime import date, datetime, timezone
import os
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import select

from db import get_session
from models import (
    User,
    Achievement,
    UserAchievement,
    ListeningTotal,
    QuestDef,
    UserQuest,
)
from services.gamify import on_event


def _utcnow():
    return datetime.now(timezone.utc)


bp = Blueprint("gamify_api", __name__, url_prefix="/api")


def _today_key() -> str:
    return date.today().strftime("%Y-%m-%d")


def _iso_week_key() -> str:
    iso_year, iso_week, _ = date.today().isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _require_int_user_id() -> int:
    raw = current_user.get_id()
    try:
        return int(raw)
    except Exception:
        # User id is not an integer; not supported for DB-backed gamification
        return -1


@bp.get("/me/gamification")
@login_required
def me_gamification():
    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    with get_session() as session:
        user = session.get(User, user_id)
        display_name = user.display_name if user and user.display_name else (user.email if user else "")
        avatar_url = user.avatar_url if user else None

        # badges (achievements joined)
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
        ua_rows = list(
            session.execute(
                select(UserAchievement, Achievement)
                .join(Achievement, Achievement.id == UserAchievement.achievement_id)
                .where(UserAchievement.user_id == user_id)
                .order_by(UserAchievement.unlocked_at.desc())
                .limit(limit)
            ).all()
        )
        badges = [
            {"key": ach.key, "title": ach.title, "icon": ach.icon, "tier": ach.tier}
            for (_ua, ach) in ua_rows
        ]

        # listening totals
        lt = session.get(ListeningTotal, user_id)
        listen = {"total_seconds": int(lt.total_seconds) if lt else 0}

        # quests today (and current week)
        day_key = _today_key()
        week_key = _iso_week_key()
        uq_rows = list(
            session.execute(
                select(UserQuest, QuestDef)
                .join(QuestDef, QuestDef.id == UserQuest.quest_id)
                .where((UserQuest.user_id == user_id) & (UserQuest.day_key.in_([day_key, week_key])))
            ).all()
        )
        quests_today = [
            {
                "key": qd.key,
                "title": qd.title,
                "description": qd.description,
                "kind": qd.kind,
                "progress_int": int(uq.progress_int or 0),
                "done": bool(uq.done),
                "xp": int(qd.xp or 0),
                "rule": qd.rule or {},
                "threshold": (qd.rule or {}).get("threshold", 1) if qd.rule else 1,
            }
            for (uq, qd) in uq_rows
        ]

        # recent achievements (small limit)
        recent_rows = ua_rows[:5]
        achievements_recent = [
            {"key": ach.key, "title": ach.title, "icon": ach.icon, "tier": ach.tier}
            for (_ua, ach) in recent_rows
        ]

        return jsonify({
            "display_name": display_name,
            "avatar_url": avatar_url,
            "badges": badges,
            "listen": listen,
            "quests_today": quests_today,
            "achievements_recent": achievements_recent,
        })


@bp.post("/debug/gamify")
@login_required
def debug_gamify():
    if os.getenv("AHOY_DEV_GAMIFY_DEBUG", "false").lower() != "true":
        return jsonify({"error": "forbidden"}), 403

    try:
        body: Dict[str, Any] = request.get_json(silent=True) or {}
    except Exception:
        return jsonify({"error": "invalid_json"}), 400

    event_kind = (body.get("event_kind") or "").strip()
    meta = body.get("meta") or {}
    allowed = {"play", "save", "queue", "playlist", "listen_time"}
    if event_kind not in allowed:
        return jsonify({"error": "invalid_event_kind", "allowed": sorted(list(allowed))}), 400

    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    summary = on_event(user_id, event_kind, meta)
    return jsonify(summary)


@bp.post("/gamify/redeem-code")
@login_required
def redeem_show_code():
    """Redeem a code from a live show to earn a merit badge"""
    user_id = _require_int_user_id()
    if user_id <= 0:
        return jsonify({"error": "unsupported_user_identity"}), 400

    try:
        body = request.get_json(silent=True) or {}
        code = (body.get("code") or "").strip().upper()
        
        if not code:
            return jsonify({"error": "code_required"}), 400

        # Simple mapping of codes to badge keys
        # In production, these would be stored in the database with show events
        code_to_badge = {
            "NEWHAVEN2024": {
                "key": "show_attended_newhaven",
                "title": "New Haven Attender",
                "description": "Attended a show in New Haven",
                "icon": "fas fa-map-marker-alt",
                "tier": "bronze"
            },
            "POETRY2024": {
                "key": "poetry_event",
                "title": "Poetry Enthusiast",
                "description": "Attended a poetry event",
                "icon": "fas fa-book",
                "tier": "bronze"
            },
            "INDIE2024": {
                "key": "indie_music_show",
                "title": "Indie Music Fan",
                "description": "Attended an indie music show",
                "icon": "fas fa-music",
                "tier": "silver"
            }
        }

        badge_def = code_to_badge.get(code)
        if not badge_def:
            return jsonify({"error": "invalid_code", "message": "This code is not recognized"}), 400

        with get_session() as session:
            # Check if achievement already exists
            ach = session.execute(
                select(Achievement).where(Achievement.key == badge_def["key"])
            ).scalar_one_or_none()

            # Create achievement if it doesn't exist
            if not ach:
                ach = Achievement(
                    key=badge_def["key"],
                    title=badge_def["title"],
                    description=badge_def["description"],
                    icon=badge_def["icon"],
                    tier=badge_def["tier"],
                    kind="show_code",
                    threshold_int=1,
                    active=True
                )
                session.add(ach)
                session.flush()

            # Check if user already has this achievement
            existing_ua = session.execute(
                select(UserAchievement).where(
                    (UserAchievement.user_id == user_id) &
                    (UserAchievement.achievement_id == ach.id)
                )
            ).scalar_one_or_none()

            if existing_ua:
                return jsonify({
                    "error": "already_redeemed",
                    "message": "You already redeemed this code!"
                }), 400

            # Grant the achievement
            ua = UserAchievement(
                user_id=user_id,
                achievement_id=ach.id,
                unlocked_at=_utcnow()
            )
            session.add(ua)

            # Trigger XP reward
            on_event(user_id, "show_code", {"code": code})

            return jsonify({
                "success": True,
                "message": "Code redeemed! You earned a badge!",
                "badge": {
                    "key": ach.key,
                    "title": ach.title,
                    "icon": ach.icon,
                    "tier": ach.tier
                }
            })

    except Exception as e:
        return jsonify({"error": "redemption_failed", "detail": str(e)}), 500



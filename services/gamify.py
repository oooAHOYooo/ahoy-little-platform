from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Dict, Any, List, Tuple

from sqlalchemy import select, func

from db import get_session
from models import (
    Achievement,
    UserAchievement,
    QuestDef,
    UserQuest,
    ListeningTotal,
)


def _utcnow():
    return datetime.now(timezone.utc)


def _today_key() -> str:
    return date.today().strftime("%Y-%m-%d")


def on_event(user_id: int, event_kind: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    meta = meta or {}
    # ensure_user_daily_quests(user_id, _today_key()) # Simplified: No quests
    achievements_unlocked = check_achievements(user_id)
    # quests_progressed, xp_earned = apply_quest_progress(user_id, event_kind, meta) # Simplified: No quests
    totals = _read_totals(user_id)
    return {
        "achievements_unlocked": achievements_unlocked,
        "quests_progressed": 0,
        "xp_earned": 0,
        "totals": totals,
    }


def _read_totals(user_id: int) -> Dict[str, Any]:
    # Currently only listening time tracked in DB; others can be extended later
    with get_session() as session:
        lt = session.get(ListeningTotal, user_id)
        return {"listen_time_seconds": int(lt.total_seconds) if lt else 0}


def check_achievements(user_id: int) -> List[str]:
    """Compare current totals vs Achievement thresholds and insert new UserAchievement rows.
    Returns a list of achievement keys unlocked this call.
    """
    unlocked: List[str] = []
    with get_session() as session:
        # Get all active achievements
        achs: List[Achievement] = list(session.execute(select(Achievement).where(Achievement.active == True)).scalars())

        # Preload user's existing achievements
        existing_ids = set(
            session.execute(select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)).scalars()
        )

        # Gather current counts - for now, only listen_time via ListeningTotal
        lt = session.get(ListeningTotal, user_id)
        current_listen_time = int(lt.total_seconds) if lt else 0

        for ach in achs:
            # Map kind -> current value
            if ach.kind == "listen_time":
                current_value = current_listen_time
            else:
                # For simplicity, treat others as 0 until counters are implemented
                current_value = 0

            threshold = ach.threshold_int or 0
            if current_value >= threshold and ach.id not in existing_ids:
                ua = UserAchievement(user_id=user_id, achievement_id=str(ach.id), unlocked_at=_utcnow())
                session.add(ua)
                unlocked.append(ach.key)
        # Session commit handled by get_session context manager
    return unlocked


def apply_quest_progress(user_id: int, event_kind: str, meta: Dict[str, Any]) -> Tuple[int, int]:
    """Deprecated: Quests simplified out."""
    return 0, 0


def ensure_user_daily_quests(user_id: int, day_key: str) -> None:
    """Deprecated: Quests simplified out."""
    passUpsert today's daily quests for a user from active QuestDefs.
    Also ensures the current weekly quests using ISO week key.
    """
    with get_session() as session:
        dailies: List[QuestDef] = list(
            session.execute(select(QuestDef).where((QuestDef.active == True) & (QuestDef.cadence == "daily"))).scalars()
        )
        for qd in dailies:
            _ensure_user_quest_row(session, user_id, str(qd.id), day_key)

        # Weekly
        week_key = _iso_week_key()
        weeklies: List[QuestDef] = list(
            session.execute(select(QuestDef).where((QuestDef.active == True) & (QuestDef.cadence == "weekly"))).scalars()
        )
        for qd in weeklies:
            _ensure_user_quest_row(session, user_id, str(qd.id), week_key)


def _iso_week_key() -> str:
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _ensure_user_quest_row(session, user_id: int, quest_id: str, day_key: str) -> None:
    uq = session.execute(
        select(UserQuest).where(
            (UserQuest.user_id == user_id) & (UserQuest.quest_id == quest_id) & (UserQuest.day_key == day_key)
        )
    ).scalar_one_or_none()
    if not uq:
        session.add(UserQuest(user_id=user_id, quest_id=quest_id, day_key=day_key, progress_int=0, done=False))

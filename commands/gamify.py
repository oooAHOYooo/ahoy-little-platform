import json
from datetime import datetime, timezone
from typing import Optional

import click
from sqlalchemy import select, func, text

from db import get_session
from models import (
    Achievement,
    User,
    QuestDef,
    ListeningTotal,
    PlayHistory,
)
from services.gamify import ensure_user_daily_quests


def _utcnow():
    return datetime.now(timezone.utc)


@click.group()
def gamify_cli():
    """Gamification utilities (seed, backfill, ensure)."""
    pass


@gamify_cli.command("seed-defs")
def seed_defs() -> None:
    """Upsert default achievements and daily quests. Idempotent."""
    defaults_ach = [
        {"key": "first_play", "title": "First Play", "tier": "bronze", "kind": "play", "threshold_int": 1},
        {"key": "first_save", "title": "First Save", "tier": "bronze", "kind": "save", "threshold_int": 1},
        {"key": "one_hour_listened", "title": "One Hour Listened", "tier": "bronze", "kind": "listen_time", "threshold_int": 3600},
    ]
    defaults_daily = [
        {"key": "daily_play_1", "title": "Daily Play", "xp": 10, "cadence": "daily", "kind": "play", "rule": {"threshold": 1}},
        {"key": "daily_listen_15m", "title": "Listen 15 Minutes", "xp": 25, "cadence": "daily", "kind": "listen_time", "rule": {"threshold": 900}},
    ]

    upserted_ach = 0
    upserted_q = 0
    with get_session() as session:
        for a in defaults_ach:
            rec = session.execute(select(Achievement).where(Achievement.key == a["key"])).scalar_one_or_none()
            if rec:
                rec.title = a["title"]
                rec.tier = a["tier"]
                rec.kind = a["kind"]
                rec.threshold_int = a["threshold_int"]
            else:
                session.add(Achievement(
                    key=a["key"], title=a["title"], tier=a["tier"], kind=a["kind"], threshold_int=a["threshold_int"], active=True, sort=0, created_at=_utcnow().replace(tzinfo=None)
                ))
                upserted_ach += 1

        for q in defaults_daily:
            rec = session.execute(select(QuestDef).where(QuestDef.key == q["key"])).scalar_one_or_none()
            if rec:
                rec.title = q["title"]
                rec.xp = q["xp"]
                rec.cadence = q["cadence"]
                rec.kind = q["kind"]
                rec.rule = q["rule"]
                rec.active = True
            else:
                session.add(QuestDef(
                    key=q["key"], title=q["title"], description=None, xp=q["xp"], cadence=q["cadence"], kind=q["kind"], rule=q["rule"], active=True, created_at=_utcnow().replace(tzinfo=None)
                ))
                upserted_q += 1

    click.echo(f"Seed complete: achievements new={upserted_ach}, quests new={upserted_q}")


@gamify_cli.command("backfill-totals")
def backfill_totals() -> None:
    """Backfill ListeningTotal per user from play_history. Safe to re-run."""
    with get_session() as session:
        rows = session.execute(
            select(PlayHistory.user_id, func.sum(func.nullif(PlayHistory.progress_seconds, 0)).label("sum_secs"), func.count().label("plays"))
            .group_by(PlayHistory.user_id)
        ).all()

        updated = 0
        for user_id, sum_secs, plays in rows:
            base = int(sum_secs or 0)
            if base <= 0:
                base = int(plays or 0) * 30
            total = session.get(ListeningTotal, user_id)
            if not total:
                total = ListeningTotal(user_id=user_id, total_seconds=0)
                session.add(total)
                session.flush()
            total.total_seconds = int(base)
            total.updated_at = _utcnow()
            updated += 1

    click.echo(f"Backfill complete: users_updated={updated}")


@gamify_cli.command("ensure-today")
@click.option("--user_id", "user_id_opt", type=int, required=False, help="Limit to a single user id")
def ensure_today(user_id_opt: Optional[int]) -> None:
    """Ensure today's and current week quests exist for users. Idempotent."""
    count = 0
    with get_session() as session:
        if user_id_opt:
            ids = [user_id_opt]
        else:
            ids = [id for (id,) in session.execute(select(User.id)).all()]
    for uid in ids:
        ensure_user_daily_quests(uid, datetime.now().strftime("%Y-%m-%d"))
        count += 1
    click.echo(f"Ensured quests for users={count}")



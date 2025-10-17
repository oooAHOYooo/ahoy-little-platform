from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update

from db import get_session
from models import ListeningSession, ListeningTotal


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def start_session(user_id: int, media_type: str, media_id: str, source: str = "manual") -> str:
    """Create a listening session and return its identifier."""
    started = _utcnow()
    with get_session() as session:
        rec = ListeningSession(
            user_id=user_id,
            media_type=media_type,
            media_id=media_id,
            started_at=started,
            source=source or "manual",
            created_at=started.replace(tzinfo=None),
        )
        session.add(rec)
        session.flush()
        return str(rec.id)


def end_session(session_id: str) -> Optional[int]:
    """End a session; compute seconds and increment totals atomically.

    Returns the number of seconds counted (0 if none or already finalized).
    """
    now = _utcnow()
    with get_session() as session:
        # Lock row for update if supported by dialect
        sess: Optional[ListeningSession] = session.get(ListeningSession, session_id)
        if not sess:
            return None
        if sess.ended_at is not None and sess.seconds and sess.seconds > 0:
            return 0

        sess.ended_at = now
        # Normalize timezone awareness for arithmetic across dialects
        def _aware(dt):
            if dt is None:
                return None
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        start = _aware(sess.started_at)
        end = _aware(sess.ended_at)
        delta = max(0, int((end - start).total_seconds())) if start and end else 0
        sess.seconds = max(sess.seconds or 0, delta)

        # Upsert into ListeningTotal
        total = session.get(ListeningTotal, sess.user_id)
        if not total:
            total = ListeningTotal(user_id=sess.user_id, total_seconds=0)
            session.add(total)
            session.flush()
        total.total_seconds = int(total.total_seconds or 0) + int(sess.seconds or 0)
        total.updated_at = now

        return int(sess.seconds or 0)



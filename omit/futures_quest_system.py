"""
ARCHIVED: Quest System Models and Functions
===========================================

This file contains the quest system code that was removed from the main codebase.
The quest system was simplified out in favor of a simpler achievements-only approach.

Date Archived: December 2024
Reason: Quest system was too complex for MVP, achievements-only approach is cleaner.

If you need to restore quest functionality:
1. Uncomment these models in models.py
2. Create Alembic migration for quest tables
3. Restore functions in services/gamify.py
4. Update on_event() to call quest functions
"""

# ============================================================================
# ARCHIVED MODELS (from models.py)
# ============================================================================

"""
class QuestDef(Base):
    __tablename__ = 'quest_defs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    xp = Column(Integer, nullable=False, default=10, server_default='10')
    cadence = Column(String(20), nullable=False)  # daily|weekly
    kind = Column(String(20), nullable=False)  # play|save|queue|playlist|streak|listen_time
    rule = Column(JSON, nullable=True)
    active = Column(Boolean, nullable=False, default=True, server_default='true', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserQuest(Base):
    __tablename__ = 'user_quests'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    quest_id = Column(String(36), ForeignKey('quest_defs.id', ondelete='CASCADE'), nullable=False, index=True)
    day_key = Column(String(20), nullable=False)  # YYYY-MM-DD or ISO week key
    progress_int = Column(Integer, nullable=False, default=0, server_default='0')
    done = Column(Boolean, nullable=False, default=False, server_default='false', index=True)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'quest_id', 'day_key', name='uq_user_quest_per_day'),
        Index('ix_user_quests_user_id_day_key', 'user_id', 'day_key'),
    )
"""

# ============================================================================
# ARCHIVED FUNCTIONS (from services/gamify.py)
# ============================================================================

"""
def apply_quest_progress(user_id: int, event_kind: str, meta: Dict[str, Any]) -> Tuple[int, int]:
    \"\"\"Apply quest progress based on event and return (quests_completed, xp_earned).\"\"\"
    # Implementation was removed - quest system simplified out
    return 0, 0


def ensure_user_daily_quests(user_id: int, day_key: str) -> None:
    \"\"\"Ensure user has daily quests initialized for the given day.\"\"\"
    # Implementation was removed - quest system simplified out
    pass
"""

# ============================================================================
# NOTES
# ============================================================================

"""
The quest system was designed to provide daily/weekly challenges for users.
However, it was determined that:
1. Achievements provide sufficient gamification
2. Quest system added unnecessary complexity
3. Database tables were never created/migrated
4. No frontend UI was built for quests

The UserArtistPosition model was also considered for removal but is kept
as it may be useful for future "boost" or "investment" features.
"""


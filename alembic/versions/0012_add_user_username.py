"""0012_add_user_username

Revision ID: 0012_add_user_username
Revises: 0011_user_artist_positions
Create Date: 2026-01-16

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0012_add_user_username"
down_revision = "0011_user_artist_positions"
branch_labels = None
depends_on = None


_ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789_")


def _normalize_username(raw: str) -> str:
    s = (raw or "").strip().lower()
    s = s.replace(" ", "_").replace("-", "_").replace(".", "_")
    s = "".join(ch for ch in s if ch in _ALLOWED)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")[:24]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    cols = [c["name"] for c in insp.get_columns("users")]
    if "username" not in cols:
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(sa.Column("username", sa.String(length=64), nullable=True))

    # Backfill before adding UNIQUE index.
    rows = list(bind.execute(sa.text("SELECT id, email FROM users")).fetchall())
    existing = set(
        (r[0] or "").strip().lower()
        for r in bind.execute(sa.text("SELECT username FROM users WHERE username IS NOT NULL AND username != ''")).fetchall()
    )
    for user_id, email in rows:
        current = bind.execute(
            sa.text("SELECT username FROM users WHERE id = :id"),
            {"id": user_id},
        ).scalar()
        if current and str(current).strip():
            existing.add(str(current).strip().lower())
            continue

        base = _normalize_username((email or "").split("@")[0]) or "user"
        candidate = base
        n = 0
        while candidate.lower() in existing:
            n += 1
            suffix = str(n)
            candidate = (base[: max(0, 24 - len(suffix))] + suffix)[:24]
            if n > 999:
                candidate = f"user{user_id}"
                break
        existing.add(candidate.lower())
        bind.execute(
            sa.text("UPDATE users SET username = :u WHERE id = :id"),
            {"u": candidate, "id": user_id},
        )

    # Add unique index if missing.
    indexes = [i["name"] for i in insp.get_indexes("users")]
    if "ix_users_username" not in indexes:
        with op.batch_alter_table("users") as batch_op:
            batch_op.create_index("ix_users_username", ["username"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = [i["name"] for i in insp.get_indexes("users")]
    with op.batch_alter_table("users") as batch_op:
        if "ix_users_username" in indexes:
            batch_op.drop_index("ix_users_username")
        batch_op.drop_column("username")


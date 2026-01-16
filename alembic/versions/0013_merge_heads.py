"""0013_merge_heads

Revision ID: 0013_merge_heads
Revises: 0009_create_artist_tips, 0012_add_user_username
Create Date: 2026-01-16

"""

from alembic import op  # noqa: F401


# revision identifiers, used by Alembic.
revision = "0013_merge_heads"
down_revision = ("0009_create_artist_tips", "0012_add_user_username")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge revision – no schema changes.
    pass


def downgrade() -> None:
    # Merge revision – no schema changes.
    pass


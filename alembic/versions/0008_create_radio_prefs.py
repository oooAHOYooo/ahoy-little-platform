"""0008_create_radio_prefs

Revision ID: 0008_create_radio_prefs
Revises: 0007_create_quests
Create Date: 2025-10-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0008_create_radio_prefs'
down_revision = '0007_create_quests'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        seed_col = sa.Column('seed_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb"))
    else:
        seed_col = sa.Column('seed_tags', sa.JSON(), nullable=False, server_default=sa.text("'[]'"))

    op.create_table(
        'radio_prefs',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('shuffle', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('include_shows', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        seed_col,
        sa.Column('last_station_key', sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('radio_prefs')

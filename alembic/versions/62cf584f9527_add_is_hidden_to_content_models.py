"""Add is_hidden to content models

Revision ID: 62cf584f9527
Revises: 98939985b910
Create Date: 2026-03-03 11:21:16.178080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '62cf584f9527'
down_revision = '98939985b910'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('content_events', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('content_merch', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('content_podcast_episodes', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('content_podcast_shows', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('content_shows', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('content_videos', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade():
    op.drop_column('content_events', 'is_hidden')
    op.drop_column('content_merch', 'is_hidden')
    op.drop_column('content_podcast_episodes', 'is_hidden')
    op.drop_column('content_podcast_shows', 'is_hidden')
    op.drop_column('content_shows', 'is_hidden')
    op.drop_column('content_videos', 'is_hidden')

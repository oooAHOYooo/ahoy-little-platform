"""0024_add_videos_and_whats_new_tables

Revision ID: 0024_videos_whats_new
Revises: 0023_add_events_and_merch
Create Date: 2026-02-07

Videos and What's New from DB (Render-dynamic).
"""
from alembic import op
import sqlalchemy as sa


revision = '0024_videos_whats_new'
down_revision = '0023_add_events_and_merch'
branch_labels = None
depends_on = None


def upgrade():
    # -- Videos (videos.json) --
    op.create_table(
        'content_videos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('video_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('event_id', sa.String(100), nullable=True, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('url', sa.String(1024), nullable=True),
        sa.Column('duration', sa.String(100), nullable=True),
        sa.Column('file_size', sa.String(50), nullable=True),
        sa.Column('format', sa.String(20), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='coming_soon'),
        sa.Column('upload_date', sa.String(50), nullable=True),
        sa.Column('thumbnail', sa.String(1024), nullable=False, server_default=''),
        sa.Column('position', sa.Integer, nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON, nullable=True),
    )

    # -- What's New (whats_new.json) --
    op.create_table(
        'content_whats_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('year', sa.String(10), nullable=False, index=True),
        sa.Column('month', sa.String(10), nullable=False, index=True),
        sa.Column('section', sa.String(50), nullable=False, index=True),
        sa.Column('item_type', sa.String(50), nullable=False, server_default='content'),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('date', sa.String(50), nullable=True),
        sa.Column('link', sa.String(1024), nullable=True),
        sa.Column('link_external', sa.String(1024), nullable=True),
        sa.Column('features', sa.JSON, nullable=True),
        sa.Column('position', sa.Integer, nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON, nullable=True),
    )
    op.create_index('ix_whats_new_year_month', 'content_whats_new', ['year', 'month'])


def downgrade():
    op.drop_index('ix_whats_new_year_month', table_name='content_whats_new')
    op.drop_table('content_whats_new')
    op.drop_table('content_videos')

"""0023_add_events_and_merch_tables

Revision ID: 0023_add_events_and_merch
Revises: 0022_add_content_tables
Create Date: 2026-02-06

Events and merch catalog from DB (Render-dynamic).
"""
from alembic import op
import sqlalchemy as sa


revision = '0023_add_events_and_merch'
down_revision = '0022_add_content_tables'
branch_labels = None
depends_on = None


def upgrade():
    # -- Events (events.json) --
    op.create_table(
        'content_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('date', sa.String(50), nullable=False, server_default=''),
        sa.Column('time', sa.String(100), nullable=False, server_default=''),
        sa.Column('venue', sa.String(255), nullable=False, server_default=''),
        sa.Column('venue_address', sa.String(500), nullable=False, server_default=''),
        sa.Column('event_type', sa.String(100), nullable=False, server_default=''),
        sa.Column('status', sa.String(50), nullable=False, server_default='upcoming'),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('photos', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('image', sa.String(1024), nullable=False, server_default=''),
        sa.Column('rsvp_external_url', sa.String(1024), nullable=True),
        sa.Column('rsvp_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rsvp_limit', sa.String(50), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )

    # -- Merch (data/merch.json) --
    op.create_table(
        'content_merch',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('item_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(500), nullable=False, server_default=''),
        sa.Column('image_url', sa.String(1024), nullable=False, server_default=''),
        sa.Column('image_url_back', sa.String(1024), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=False, server_default='20.0'),
        sa.Column('kind', sa.String(50), nullable=False, server_default='merch'),
        sa.Column('available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_table('content_merch')
    op.drop_table('content_events')

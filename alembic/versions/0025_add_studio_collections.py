"""0025_add_studio_collections

Revision ID: 0025_studio_collections
Revises: 0024_videos_whats_new
Create Date: 2026-03-06

Studio collections table for /studio page (photo galleries, BTS, live events).
"""
from alembic import op
import sqlalchemy as sa


revision = '0025_studio_collections'
down_revision = 'f0f9b3832b09'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'studio_collections',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('collection_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('date', sa.String(50), nullable=False, server_default=''),
        sa.Column('tag', sa.String(100), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('cover', sa.String(1024), nullable=False, server_default=''),
        sa.Column('photos', sa.JSON, nullable=True),
        sa.Column('is_hidden', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('position', sa.Integer, nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON, nullable=True),
    )


def downgrade():
    op.drop_table('studio_collections')

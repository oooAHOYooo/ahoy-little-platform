"""0022_add_content_tables

Revision ID: 0022_add_content_tables
Revises: 0021_purchase_decimal_precision
Create Date: 2026-02-06

Migrate music, shows, artists, and podcasts from static JSON files
to database tables. Preserves all existing fields and ordering.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0022_add_content_tables'
down_revision = '0021_purchase_decimal_precision'
branch_labels = None
depends_on = None


def upgrade():
    # -- Tracks (music.json) --
    op.create_table(
        'content_tracks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('track_id', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('artist', sa.String(255), nullable=False, server_default=''),
        sa.Column('album', sa.String(255), nullable=False, server_default=''),
        sa.Column('genre', sa.String(100), nullable=False, server_default=''),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('audio_url', sa.String(1024), nullable=False, server_default=''),
        sa.Column('preview_url', sa.String(1024), nullable=False, server_default=''),
        sa.Column('cover_art', sa.String(1024), nullable=False, server_default=''),
        sa.Column('added_date', sa.String(50), nullable=False, server_default=''),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('artist_slug', sa.String(255), nullable=False, server_default='', index=True),
        sa.Column('artist_url', sa.String(1024), nullable=True),
        sa.Column('background_image', sa.String(1024), nullable=True),
        sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('date_added', sa.String(50), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )

    # -- Shows (shows.json) --
    op.create_table(
        'content_shows',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('show_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('host', sa.String(255), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('video_url', sa.String(1024), nullable=False, server_default=''),
        sa.Column('trailer_url', sa.String(1024), nullable=True),
        sa.Column('thumbnail', sa.String(1024), nullable=False, server_default=''),
        sa.Column('published_date', sa.String(50), nullable=False, server_default=''),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('show_type', sa.String(50), nullable=False, server_default=''),
        sa.Column('is_live', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('host_slug', sa.String(255), nullable=True, index=True),
        sa.Column('category', sa.String(100), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )

    # -- Artists (artists.json) --
    op.create_table(
        'content_artists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('artist_id', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False, server_default=''),
        sa.Column('slug', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('artist_type', sa.String(50), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('image', sa.String(1024), nullable=False, server_default=''),
        sa.Column('social_links', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('genres', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('followers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at_str', sa.String(50), nullable=False, server_default=''),
        sa.Column('updated_at_str', sa.String(50), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0', index=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )

    # -- Artist Albums --
    op.create_table(
        'content_artist_albums',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('album_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('artist_id_ref', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('release_date', sa.String(50), nullable=False, server_default=''),
        sa.Column('cover_art', sa.String(1024), nullable=False, server_default=''),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
    )

    # -- Artist Album Tracks --
    op.create_table(
        'content_artist_album_tracks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('album_id_ref', sa.String(100), nullable=False, index=True),
        sa.Column('track_id_ref', sa.String(50), nullable=False, server_default=''),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
    )

    # -- Artist Show Refs --
    op.create_table(
        'content_artist_shows',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('artist_id_ref', sa.String(50), nullable=False, index=True),
        sa.Column('show_ref_id', sa.String(100), nullable=False, server_default=''),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('show_type', sa.String(50), nullable=False, server_default=''),
        sa.Column('duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(100), nullable=False, server_default=''),
        sa.Column('published_date', sa.String(50), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
    )

    # -- Artist Track Refs --
    op.create_table(
        'content_artist_tracks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('artist_id_ref', sa.String(50), nullable=False, index=True),
        sa.Column('track_ref_id', sa.String(50), nullable=False, server_default=''),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('album', sa.String(255), nullable=False, server_default=''),
        sa.Column('duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('genre', sa.String(100), nullable=False, server_default=''),
        sa.Column('added_date', sa.String(50), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
    )

    # -- Podcast Shows --
    op.create_table(
        'content_podcast_shows',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('artwork', sa.String(1024), nullable=False, server_default=''),
        sa.Column('last_updated', sa.String(50), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
    )

    # -- Podcast Episodes --
    op.create_table(
        'content_podcast_episodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('episode_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('show_slug', sa.String(100), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('date', sa.String(50), nullable=False, server_default=''),
        sa.Column('duration', sa.String(50), nullable=False, server_default=''),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('audio_url', sa.String(1024), nullable=False, server_default=''),
        sa.Column('artwork', sa.String(1024), nullable=False, server_default=''),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade():
    op.drop_table('content_podcast_episodes')
    op.drop_table('content_podcast_shows')
    op.drop_table('content_artist_tracks')
    op.drop_table('content_artist_shows')
    op.drop_table('content_artist_album_tracks')
    op.drop_table('content_artist_albums')
    op.drop_table('content_artists')
    op.drop_table('content_shows')
    op.drop_table('content_tracks')

"""0001_init

Revision ID: 0001_0001_init
Revises: 
Create Date: 2025-10-08

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # playlists table
    op.create_table(
        'playlists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_playlists_user_id_created_at', 'playlists', ['user_id', 'created_at'], unique=False)

    # playlist_items table
    op.create_table(
        'playlist_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('playlist_id', sa.Integer(), sa.ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_id', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_playlist_items_playlist_id_position', 'playlist_items', ['playlist_id', 'position'], unique=False)

    # bookmarks table
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_id', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', 'media_id', 'media_type', name='uq_bookmarks_user_media'),
    )
    op.create_index('ix_bookmarks_user_id_created_at', 'bookmarks', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_bookmarks_user_id_media_id', 'bookmarks', ['user_id', 'media_id'], unique=False)

    # play_history table
    op.create_table(
        'play_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_id', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('played_at', sa.DateTime(), nullable=False),
        sa.Column('progress_seconds', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_play_history_user_id_created_at', 'play_history', ['user_id', 'played_at'], unique=False)

    # feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('message', sa.String(length=2000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_feedback_user_id_created_at', 'feedback', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_feedback_user_id_created_at', table_name='feedback')
    op.drop_table('feedback')

    op.drop_index('ix_play_history_user_id_created_at', table_name='play_history')
    op.drop_table('play_history')

    op.drop_index('ix_bookmarks_user_id_media_id', table_name='bookmarks')
    op.drop_index('ix_bookmarks_user_id_created_at', table_name='bookmarks')
    op.drop_table('bookmarks')

    op.drop_index('ix_playlist_items_playlist_id_position', table_name='playlist_items')
    op.drop_table('playlist_items')

    op.drop_index('ix_playlists_user_id_created_at', table_name='playlists')
    op.drop_table('playlists')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')



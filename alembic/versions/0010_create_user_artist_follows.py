"""0010_create_user_artist_follows

Revision ID: 0010_create_user_artist_follows
Revises: 0009_create_tips
Create Date: 2025-11-03

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0010_create_user_artist_follows'
down_revision = '0009_create_tips'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    
    if 'user_artist_follows' not in tables:
        # Table doesn't exist, create it
        op.create_table(
            'user_artist_follows',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('artist_id', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'artist_id', name='uq_user_artist_follow_once')
        )
        
        # Create indexes
        op.create_index('ix_user_artist_follows_user_id', 'user_artist_follows', ['user_id'])
        op.create_index('ix_user_artist_follows_artist_id', 'user_artist_follows', ['artist_id'])
        op.create_index('ix_user_artist_follows_user_id_created_at', 'user_artist_follows', ['user_id', 'created_at'])
    else:
        # Table exists, check if unique constraint exists
        constraints = inspector.get_unique_constraints('user_artist_follows')
        constraint_names = [c['name'] for c in constraints]
        
        if 'uq_user_artist_follow_once' not in constraint_names:
            # Add unique constraint using a unique index (SQLite workaround)
            op.create_index('uq_user_artist_follow_once', 'user_artist_follows', ['user_id', 'artist_id'], unique=True)


def downgrade() -> None:
    op.drop_table('user_artist_follows')


"""0009_create_artist_tips

Revision ID: 0009_create_artist_tips
Revises: 0008_create_radio_prefs
Create Date: 2025-11-03

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009_create_artist_tips'
down_revision = '0008_create_radio_prefs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'artist_tips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('artist_name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_artist_tips_user_id_created_at', 'artist_tips', ['user_id', 'created_at'])
    op.create_index('ix_artist_tips_artist_name', 'artist_tips', ['artist_name'])
    op.create_index(op.f('ix_artist_tips_user_id'), 'artist_tips', ['user_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_artist_tips_user_id'), table_name='artist_tips')
    op.drop_index('ix_artist_tips_artist_name', table_name='artist_tips')
    op.drop_index('ix_artist_tips_user_id_created_at', table_name='artist_tips')
    op.drop_table('artist_tips')




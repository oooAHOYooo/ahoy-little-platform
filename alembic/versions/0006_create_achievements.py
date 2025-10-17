"""0006_create_achievements

Revision ID: 0006_create_achievements
Revises: 0005_create_listening_tables
Create Date: 2025-10-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0006_create_achievements'
down_revision = '0005_create_listening_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        ach_id_col = sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))
        ua_id_col = sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    else:
        ach_id_col = sa.Column('id', sa.String(length=36), primary_key=True)
        ua_id_col = sa.Column('id', sa.String(length=36), primary_key=True)

    # achievements
    op.create_table(
        'achievements',
        ach_id_col,
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('icon', sa.String(length=255), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.Column('kind', sa.String(length=20), nullable=False),
        sa.Column('threshold_int', sa.Integer(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('sort', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_achievements_key', 'achievements', ['key'], unique=True)
    op.create_index('ix_achievements_active', 'achievements', ['active'], unique=False)

    # user_achievements
    op.create_table(
        'user_achievements',
        ua_id_col,
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', ach_id_col.type, sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement_once'),
    )
    if dialect == 'postgresql':
        op.create_index('ix_user_achievements_user_id_unlocked_at', 'user_achievements', ['user_id', sa.text('unlocked_at DESC')], unique=False)
    else:
        op.create_index('ix_user_achievements_user_id_unlocked_at', 'user_achievements', ['user_id', 'unlocked_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_achievements_user_id_unlocked_at', table_name='user_achievements')
    op.drop_table('user_achievements')
    op.drop_index('ix_achievements_active', table_name='achievements')
    op.drop_index('ix_achievements_key', table_name='achievements')
    op.drop_table('achievements')

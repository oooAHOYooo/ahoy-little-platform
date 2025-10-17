"""0007_create_quests

Revision ID: 0007_create_quests
Revises: 0006_create_achievements
Create Date: 2025-10-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0007_create_quests'
down_revision = '0006_create_achievements'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        qd_id_col = sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))
        uq_id_col = sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))
        rule_col = sa.Column('rule', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    else:
        qd_id_col = sa.Column('id', sa.String(length=36), primary_key=True)
        uq_id_col = sa.Column('id', sa.String(length=36), primary_key=True)
        rule_col = sa.Column('rule', sa.JSON(), nullable=True)

    # quest_defs
    op.create_table(
        'quest_defs',
        qd_id_col,
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=False, server_default=sa.text('10')),
        sa.Column('cadence', sa.String(length=20), nullable=False),
        sa.Column('kind', sa.String(length=20), nullable=False),
        rule_col,
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_quest_defs_key', 'quest_defs', ['key'], unique=True)
    op.create_index('ix_quest_defs_active', 'quest_defs', ['active'], unique=False)

    # user_quests
    op.create_table(
        'user_quests',
        uq_id_col,
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quest_id', qd_id_col.type, sa.ForeignKey('quest_defs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('day_key', sa.String(length=20), nullable=False),
        sa.Column('progress_int', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('done', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'quest_id', 'day_key', name='uq_user_quest_per_day'),
    )

    if dialect == 'postgresql':
        op.create_index('ix_user_quests_user_id_day_key', 'user_quests', ['user_id', sa.text('day_key DESC')], unique=False)
    else:
        op.create_index('ix_user_quests_user_id_day_key', 'user_quests', ['user_id', 'day_key'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_quests_user_id_day_key', table_name='user_quests')
    op.drop_table('user_quests')
    op.drop_index('ix_quest_defs_active', table_name='quest_defs')
    op.drop_index('ix_quest_defs_key', table_name='quest_defs')
    op.drop_table('quest_defs')

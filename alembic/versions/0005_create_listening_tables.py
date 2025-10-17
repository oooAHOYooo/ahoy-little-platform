"""0005_create_listening_tables

Revision ID: 0005_create_listening_tables
Revises: 0004_add_user_profile_fields
Create Date: 2025-10-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_create_listening_tables'
down_revision = '0004_add_user_profile_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # listening_sessions
    if dialect == 'postgresql':
        id_col = sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    else:
        id_col = sa.Column('id', sa.String(length=36), primary_key=True)

    op.create_table(
        'listening_sessions',
        id_col,
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('media_id', sa.String(length=36), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('seconds', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('source', sa.String(length=20), nullable=False, server_default=sa.text("'manual'")),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Indexes
    if dialect == 'postgresql':
        op.create_index('ix_listening_sessions_user_id_started_at', 'listening_sessions', ['user_id', sa.text('started_at DESC')], unique=False)
    else:
        op.create_index('ix_listening_sessions_user_id_started_at', 'listening_sessions', ['user_id', 'started_at'], unique=False)

    op.create_index('ix_listening_sessions_media', 'listening_sessions', ['media_type', 'media_id'], unique=False)

    # listening_totals
    op.create_table(
        'listening_totals',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('total_seconds', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('listening_totals')
    op.drop_index('ix_listening_sessions_media', table_name='listening_sessions')
    op.drop_index('ix_listening_sessions_user_id_started_at', table_name='listening_sessions')
    op.drop_table('listening_sessions')

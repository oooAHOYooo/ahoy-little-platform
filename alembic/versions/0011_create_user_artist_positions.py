"""0011_create_user_artist_positions

Revision ID: 0011_user_artist_positions
Revises: 0010_create_user_artist_follows
Create Date: 2025-11-03

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
# NOTE: Alembic's default alembic_version.version_num is VARCHAR(32). Keep IDs <= 32 chars.
revision = '0011_user_artist_positions'
down_revision = '0010_create_user_artist_follows'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = sa.inspect(bind)

    # Check if platform_fee column exists before adding it
    tips_columns = [col['name'] for col in inspector.get_columns('tips')]
    if 'platform_fee' not in tips_columns:
        # Add platform_fee column to tips table (nullable for existing records)
        op.add_column('tips', sa.Column('platform_fee', sa.Numeric(10, 2), nullable=True))
        
        # For existing records, copy fee to platform_fee
        op.execute("UPDATE tips SET platform_fee = fee WHERE platform_fee IS NULL")
    else:
        # Column already exists, just ensure existing records have it set
        op.execute("UPDATE tips SET platform_fee = fee WHERE platform_fee IS NULL")
    
    # Create user_artist_positions table if it doesn't exist
    tables = inspector.get_table_names()
    if 'user_artist_positions' not in tables:
        # Include unique constraint in table creation for SQLite compatibility
        if dialect == 'postgresql':
            total_contributed_col = sa.Column('total_contributed', sa.Numeric(10, 2), nullable=False, server_default='0')
        else:
            # SQLite uses DECIMAL which maps to NUMERIC
            total_contributed_col = sa.Column('total_contributed', sa.Numeric(10, 2), nullable=False, server_default='0')
        
        op.create_table(
            'user_artist_positions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('artist_id', sa.String(length=255), nullable=False),
            total_contributed_col,
            sa.Column('last_tip', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'artist_id', name='uq_user_artist_position_once')
        )
        
        # Create indexes
        op.create_index('ix_user_artist_positions_user_id', 'user_artist_positions', ['user_id'])
        op.create_index('ix_user_artist_positions_artist_id', 'user_artist_positions', ['artist_id'])
        op.create_index('ix_user_artist_positions_user_id_updated_at', 'user_artist_positions', ['user_id', 'updated_at'])


def downgrade() -> None:
    op.drop_table('user_artist_positions')
    op.drop_column('tips', 'platform_fee')


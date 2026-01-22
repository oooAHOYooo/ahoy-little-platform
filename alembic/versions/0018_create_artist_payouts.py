"""0018_create_artist_payouts

Revision ID: 0018_create_artist_payouts
Revises: 0017_add_tip_fee_columns
Create Date: 2025-01-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0018_create_artist_payouts'
down_revision = '0017_add_tip_fee_columns'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Create artist_payouts table
    op.create_table(
        'artist_payouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('stripe_transfer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payout_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add JSON column for related_tip_ids (PostgreSQL-specific)
    if dialect == 'postgresql':
        op.execute("ALTER TABLE artist_payouts ADD COLUMN related_tip_ids JSONB")
    else:
        # SQLite fallback - use TEXT for JSON
        op.add_column('artist_payouts', sa.Column('related_tip_ids', sa.Text(), nullable=True))
    
    # Create indexes
    op.create_index('ix_artist_payouts_artist_id', 'artist_payouts', ['artist_id'])
    op.create_index('ix_artist_payouts_status', 'artist_payouts', ['status'])
    op.create_index('ix_artist_payouts_stripe_transfer_id', 'artist_payouts', ['stripe_transfer_id'], unique=True)
    op.create_index('ix_artist_payouts_artist_id_status', 'artist_payouts', ['artist_id', 'status'])
    op.create_index('ix_artist_payouts_created_at', 'artist_payouts', ['created_at'])


def downgrade():
    op.drop_index('ix_artist_payouts_created_at', table_name='artist_payouts')
    op.drop_index('ix_artist_payouts_artist_id_status', table_name='artist_payouts')
    op.drop_index('ix_artist_payouts_stripe_transfer_id', table_name='artist_payouts')
    op.drop_index('ix_artist_payouts_status', table_name='artist_payouts')
    op.drop_index('ix_artist_payouts_artist_id', table_name='artist_payouts')
    op.drop_table('artist_payouts')

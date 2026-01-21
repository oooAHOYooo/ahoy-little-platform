"""0017_add_tip_fee_columns

Revision ID: 0017_add_tip_fee_columns
Revises: 0016_add_stripe_customer_id
Create Date: 2025-01-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0017_add_tip_fee_columns'
down_revision = '0016_add_stripe_customer_id'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fee structure columns to tips table
    # These columns are nullable to support existing records
    op.add_column('tips', sa.Column('stripe_fee', sa.Numeric(10, 2), nullable=True))
    op.add_column('tips', sa.Column('platform_fee', sa.Numeric(10, 2), nullable=True))
    op.add_column('tips', sa.Column('total_paid', sa.Numeric(10, 2), nullable=True))
    op.add_column('tips', sa.Column('artist_payout', sa.Numeric(10, 2), nullable=True))
    op.add_column('tips', sa.Column('platform_revenue', sa.Numeric(10, 2), nullable=True))


def downgrade():
    op.drop_column('tips', 'platform_revenue')
    op.drop_column('tips', 'artist_payout')
    op.drop_column('tips', 'total_paid')
    op.drop_column('tips', 'platform_fee')
    op.drop_column('tips', 'stripe_fee')

"""0020_purchase_tracking_fields

Revision ID: 0020_purchase_tracking_fields
Revises: 0019_purchase_shipping_addr
Create Date: 2026-01-27

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0020_purchase_tracking_fields"
down_revision = "0019_purchase_shipping_addr"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tracking and fulfillment fields to purchases table
    op.add_column('purchases', sa.Column('tracking_number', sa.String(length=100), nullable=True))
    op.add_column('purchases', sa.Column('fulfilled_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('purchases', 'fulfilled_at')
    op.drop_column('purchases', 'tracking_number')

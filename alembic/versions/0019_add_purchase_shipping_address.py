"""0019_add_purchase_shipping_address

Revision ID: 0019_add_purchase_shipping_address
Revises: 0018_create_artist_payouts
Create Date: 2026-01-26

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0019_add_purchase_shipping_address"
down_revision = "0018_create_artist_payouts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add shipping address fields to purchases table
    op.add_column('purchases', sa.Column('shipping_name', sa.String(length=255), nullable=True))
    op.add_column('purchases', sa.Column('shipping_line1', sa.String(length=255), nullable=True))
    op.add_column('purchases', sa.Column('shipping_line2', sa.String(length=255), nullable=True))
    op.add_column('purchases', sa.Column('shipping_city', sa.String(length=100), nullable=True))
    op.add_column('purchases', sa.Column('shipping_state', sa.String(length=50), nullable=True))
    op.add_column('purchases', sa.Column('shipping_postal_code', sa.String(length=20), nullable=True))
    op.add_column('purchases', sa.Column('shipping_country', sa.String(length=2), nullable=True))


def downgrade() -> None:
    op.drop_column('purchases', 'shipping_country')
    op.drop_column('purchases', 'shipping_postal_code')
    op.drop_column('purchases', 'shipping_state')
    op.drop_column('purchases', 'shipping_city')
    op.drop_column('purchases', 'shipping_line2')
    op.drop_column('purchases', 'shipping_line1')
    op.drop_column('purchases', 'shipping_name')

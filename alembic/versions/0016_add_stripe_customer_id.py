"""0016_add_stripe_customer_id

Revision ID: 0016_add_stripe_customer_id
Revises: 0015_add_wallet_system
Create Date: 2025-01-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0016_add_stripe_customer_id'
down_revision = '0015_add_wallet_system'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    op.drop_column('users', 'stripe_customer_id')

"""0015_add_wallet_system

Revision ID: 0015_add_wallet_system
Revises: 0014_create_purchases_table
Create Date: 2025-01-22

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0015_add_wallet_system"
down_revision = "0014_create_purchases_table"
branch_labels = None
depends_on = None


def _has_column(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [col['name'] for col in insp.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()
    
    # Add wallet_balance to users table
    if 'users' in tables and not _has_column('users', 'wallet_balance'):
        op.add_column('users', sa.Column('wallet_balance', sa.Numeric(10, 2), nullable=False, server_default='0.00'))
    
    # Create wallet_transactions table
    if 'wallet_transactions' not in tables:
        op.create_table(
            'wallet_transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('type', sa.String(length=50), nullable=False),  # 'fund', 'spend', 'refund'
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('balance_before', sa.Numeric(10, 2), nullable=False),
            sa.Column('balance_after', sa.Numeric(10, 2), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('reference_id', sa.String(length=255), nullable=True),  # Stripe session ID, purchase ID, etc.
            sa.Column('reference_type', sa.String(length=50), nullable=True),  # 'stripe_checkout', 'purchase', 'boost', etc.
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index('ix_wallet_transactions_user_id', 'wallet_transactions', ['user_id'])
        op.create_index('ix_wallet_transactions_type', 'wallet_transactions', ['type'])
        op.create_index('ix_wallet_transactions_created_at', 'wallet_transactions', ['created_at'])
        op.create_index('ix_wallet_transactions_user_id_created_at', 'wallet_transactions', ['user_id', 'created_at'])
        op.create_index('ix_wallet_transactions_reference_id', 'wallet_transactions', ['reference_id'])


def downgrade() -> None:
    # Drop wallet_transactions table
    op.drop_index('ix_wallet_transactions_reference_id', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_user_id_created_at', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_created_at', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_type', table_name='wallet_transactions')
    op.drop_index('ix_wallet_transactions_user_id', table_name='wallet_transactions')
    op.drop_table('wallet_transactions')
    
    # Remove wallet_balance from users
    if _has_column('users', 'wallet_balance'):
        op.drop_column('users', 'wallet_balance')

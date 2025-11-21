"""0009_create_tips

Revision ID: 0009_create_tips
Revises: 0008_create_radio_prefs
Create Date: 2025-11-03

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0009_create_tips'
down_revision = '0008_create_radio_prefs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        amount_col = sa.Column('amount', sa.Numeric(10, 2), nullable=False)
        fee_col = sa.Column('fee', sa.Numeric(10, 2), nullable=False)
        net_col = sa.Column('net_amount', sa.Numeric(10, 2), nullable=False)
    else:
        # SQLite uses DECIMAL which maps to NUMERIC
        amount_col = sa.Column('amount', sa.Numeric(10, 2), nullable=False)
        fee_col = sa.Column('fee', sa.Numeric(10, 2), nullable=False)
        net_col = sa.Column('net_amount', sa.Numeric(10, 2), nullable=False)

    op.create_table(
        'tips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('artist_id', sa.String(length=255), nullable=False),
        amount_col,
        fee_col,
        net_col,
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_checkout_session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_tips_user_id', 'tips', ['user_id'])
    op.create_index('ix_tips_artist_id', 'tips', ['artist_id'])
    op.create_index('ix_tips_user_id_created_at', 'tips', ['user_id', 'created_at'])
    op.create_index('ix_tips_artist_id_created_at', 'tips', ['artist_id', 'created_at'])
    op.create_index('ix_tips_created_at', 'tips', ['created_at'])
    
    # Unique indexes for Stripe IDs
    op.create_index('ix_tips_stripe_payment_intent_id', 'tips', ['stripe_payment_intent_id'], unique=True)
    op.create_index('ix_tips_stripe_checkout_session_id', 'tips', ['stripe_checkout_session_id'], unique=True)


def downgrade() -> None:
    op.drop_table('tips')





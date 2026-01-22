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
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Use PostgreSQL-specific DO block for more reliable column existence checks
    if dialect == 'postgresql':
        # Check and add columns using PostgreSQL's information_schema
        # This is more reliable than using inspector in some environments
        op.execute("""
            DO $$ 
            BEGIN
                -- Add stripe_fee if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'tips' AND column_name = 'stripe_fee'
                ) THEN
                    ALTER TABLE tips ADD COLUMN stripe_fee NUMERIC(10, 2);
                END IF;
                
                -- Add platform_fee if it doesn't exist (may already exist from migration 0011)
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'tips' AND column_name = 'platform_fee'
                ) THEN
                    ALTER TABLE tips ADD COLUMN platform_fee NUMERIC(10, 2);
                END IF;
                
                -- Add total_paid if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'tips' AND column_name = 'total_paid'
                ) THEN
                    ALTER TABLE tips ADD COLUMN total_paid NUMERIC(10, 2);
                END IF;
                
                -- Add artist_payout if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'tips' AND column_name = 'artist_payout'
                ) THEN
                    ALTER TABLE tips ADD COLUMN artist_payout NUMERIC(10, 2);
                END IF;
                
                -- Add platform_revenue if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'tips' AND column_name = 'platform_revenue'
                ) THEN
                    ALTER TABLE tips ADD COLUMN platform_revenue NUMERIC(10, 2);
                END IF;
            END $$;
        """)
    else:
        # Fallback for other databases (SQLite, etc.)
        inspector = sa.inspect(bind)
        tips_columns = [col['name'] for col in inspector.get_columns('tips')]
        
        if 'stripe_fee' not in tips_columns:
            op.add_column('tips', sa.Column('stripe_fee', sa.Numeric(10, 2), nullable=True))
        
        if 'platform_fee' not in tips_columns:
            op.add_column('tips', sa.Column('platform_fee', sa.Numeric(10, 2), nullable=True))
        
        if 'total_paid' not in tips_columns:
            op.add_column('tips', sa.Column('total_paid', sa.Numeric(10, 2), nullable=True))
        
        if 'artist_payout' not in tips_columns:
            op.add_column('tips', sa.Column('artist_payout', sa.Numeric(10, 2), nullable=True))
        
        if 'platform_revenue' not in tips_columns:
            op.add_column('tips', sa.Column('platform_revenue', sa.Numeric(10, 2), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Get existing columns in tips table
    tips_columns = [col['name'] for col in inspector.get_columns('tips')]
    
    # Drop columns only if they exist
    if 'platform_revenue' in tips_columns:
        op.drop_column('tips', 'platform_revenue')
    if 'artist_payout' in tips_columns:
        op.drop_column('tips', 'artist_payout')
    if 'total_paid' in tips_columns:
        op.drop_column('tips', 'total_paid')
    if 'platform_fee' in tips_columns:
        op.drop_column('tips', 'platform_fee')
    if 'stripe_fee' in tips_columns:
        op.drop_column('tips', 'stripe_fee')

"""0014_create_purchases_table

Revision ID: 0014_create_purchases_table
Revises: 0013_merge_heads
Create Date: 2026-01-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0014_create_purchases_table"
down_revision = "0013_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()
    
    if 'purchases' not in tables:
        op.create_table(
            'purchases',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('type', sa.String(length=50), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('artist_id', sa.String(length=50), nullable=True),
            sa.Column('item_id', sa.String(length=50), nullable=True),
            sa.Column('qty', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('total', sa.Float(), nullable=False),
            sa.Column('stripe_id', sa.String(length=255), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index('ix_purchases_user_id', 'purchases', ['user_id'])
        op.create_index('ix_purchases_artist_id', 'purchases', ['artist_id'])
        op.create_index('ix_purchases_stripe_id', 'purchases', ['stripe_id'])
        op.create_index('ix_purchases_status', 'purchases', ['status'])
        op.create_index('ix_purchases_created_at', 'purchases', ['created_at'])
        op.create_index('ix_purchases_user_id_created_at', 'purchases', ['user_id', 'created_at'])
        op.create_index('ix_purchases_type_created_at', 'purchases', ['type', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_purchases_type_created_at', table_name='purchases')
    op.drop_index('ix_purchases_user_id_created_at', table_name='purchases')
    op.drop_index('ix_purchases_created_at', table_name='purchases')
    op.drop_index('ix_purchases_status', table_name='purchases')
    op.drop_index('ix_purchases_stripe_id', table_name='purchases')
    op.drop_index('ix_purchases_artist_id', table_name='purchases')
    op.drop_index('ix_purchases_user_id', table_name='purchases')
    op.drop_table('purchases')

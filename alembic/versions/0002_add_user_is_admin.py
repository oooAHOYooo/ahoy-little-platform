"""0002_add_user_is_admin

Revision ID: 0002_add_user_is_admin
Revises: 0001_0001_init
Create Date: 2025-10-08

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_add_user_is_admin'
down_revision = '0001_0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index('ix_users_is_admin', 'users', ['is_admin'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_users_is_admin', table_name='users')
    op.drop_column('users', 'is_admin')



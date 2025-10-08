"""0003_add_user_disabled

Revision ID: 0003_add_user_disabled
Revises: 0002_add_user_is_admin
Create Date: 2025-10-08

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_add_user_disabled'
down_revision = '0002_add_user_is_admin'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('disabled', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index('ix_users_disabled', 'users', ['disabled'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_users_disabled', table_name='users')
    op.drop_column('users', 'disabled')



"""0004_add_user_profile_fields

Revision ID: 0004_add_user_profile_fields
Revises: 0003_add_user_disabled
Create Date: 2025-10-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0004_add_user_profile_fields'
down_revision = '0003_add_user_disabled'
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = [c['name'] for c in insp.get_columns(table)]
        return column in cols
    except Exception:
        return False


def upgrade() -> None:
    # display_name
    if not _has_column('users', 'display_name'):
        op.add_column('users', sa.Column('display_name', sa.String(length=255), nullable=True))

    # avatar_url
    if not _has_column('users', 'avatar_url'):
        op.add_column('users', sa.Column('avatar_url', sa.String(length=1024), nullable=True))

    # preferences: JSONB on Postgres, JSON elsewhere
    if not _has_column('users', 'preferences'):
        bind = op.get_bind()
        dialect_name = bind.dialect.name
        if dialect_name == 'postgresql':
            op.add_column('users', sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")))
        else:
            op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=False, server_default=sa.text("'{}'")))

    # last_active_at: timestamptz on Postgres, timezone-aware DateTime otherwise
    if not _has_column('users', 'last_active_at'):
        bind = op.get_bind()
        dialect_name = bind.dialect.name
        if dialect_name == 'postgresql':
            op.add_column('users', sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True))
        else:
            op.add_column('users', sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True))

    # index on last_active_at
    try:
        op.create_index('ix_users_last_active_at', 'users', ['last_active_at'], unique=False)
    except Exception:
        # index may already exist
        pass

    # Ensure disabled exists (added by 0003) - skip if present
    if not _has_column('users', 'disabled'):
        op.add_column('users', sa.Column('disabled', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        try:
            op.create_index('ix_users_disabled', 'users', ['disabled'], unique=False)
        except Exception:
            pass


def downgrade() -> None:
    # Drop index
    try:
        op.drop_index('ix_users_last_active_at', table_name='users')
    except Exception:
        pass

    # Drop columns if exist
    for col in ['last_active_at', 'preferences', 'avatar_url', 'display_name']:
        if _has_column('users', col):
            try:
                op.drop_column('users', col)
            except Exception:
                pass



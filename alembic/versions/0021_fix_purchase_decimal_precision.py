"""0021_purchase_decimal_precision

Revision ID: 0021_purchase_decimal_precision
Revises: 0020_purchase_tracking_fields
Create Date: 2026-01-27

Fix Purchase model to use Numeric(10,2) instead of Float for financial columns.
Float causes precision errors in financial calculations.

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0021_purchase_decimal_precision'
down_revision = '0020_purchase_tracking_fields'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # PostgreSQL: ALTER COLUMN TYPE with explicit cast
        op.execute("""
            ALTER TABLE purchases
            ALTER COLUMN amount TYPE NUMERIC(10, 2) USING amount::numeric(10, 2);
        """)
        op.execute("""
            ALTER TABLE purchases
            ALTER COLUMN total TYPE NUMERIC(10, 2) USING total::numeric(10, 2);
        """)
    else:
        # SQLite: doesn't support ALTER COLUMN, but types are flexible
        # The model change will be used for new inserts; existing data is compatible
        # For a full migration, we'd need to recreate the table, but SQLite's
        # dynamic typing means the existing REAL values work with NUMERIC
        pass


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        op.execute("""
            ALTER TABLE purchases
            ALTER COLUMN amount TYPE DOUBLE PRECISION USING amount::double precision;
        """)
        op.execute("""
            ALTER TABLE purchases
            ALTER COLUMN total TYPE DOUBLE PRECISION USING total::double precision;
        """)
    else:
        # SQLite: no action needed (see upgrade comment)
        pass

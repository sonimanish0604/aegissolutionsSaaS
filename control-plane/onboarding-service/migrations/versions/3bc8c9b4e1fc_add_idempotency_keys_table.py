"""add idempotency_keys table

Revision ID: 3bc8c9b4e1fc
Revises: 
Create Date: 2025-10-07 16:53:37.756079+00:00

"""
from alembic import op
import sqlalchemy as sa
from pathlib import Path

# revision identifiers, used by Alembic.
revision = '3bc8c9b4e1fc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    sql_path = Path(__file__).resolve().parents[1] / "0012_add_idempotency_keys.sql"
    op.execute(sql_path.read_text(encoding="utf-8"))

def downgrade() -> None:
    op.execute("""
    DROP TRIGGER IF EXISTS trg_idemp_touch ON idempotency_keys;
    DROP TABLE IF EXISTS idempotency_keys;
    """)
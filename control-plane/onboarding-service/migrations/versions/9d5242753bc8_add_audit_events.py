"""add audit_events

Revision ID: 9d5242753bc8
Revises: 3bc8c9b4e1fc
Create Date: 2025-10-08 03:58:48.499375+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9d5242753bc8'
down_revision = '3bc8c9b4e1fc'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
      id               BIGSERIAL PRIMARY KEY,
      occurred_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
      tenant_id        UUID NULL,
      actor_id         UUID NULL,
      actor_type       TEXT NOT NULL,
      source_ip        INET NULL,
      user_agent       TEXT NULL,
      correlation_id   TEXT NULL,
      idempotency_key  TEXT NULL,
      route            TEXT NOT NULL,
      action           TEXT NOT NULL,
      target_type      TEXT NULL,
      target_id        TEXT NULL,
      status_code      INTEGER NOT NULL,
      severity         TEXT NOT NULL DEFAULT 'info',
      payload_redacted JSONB NULL
    );

    CREATE INDEX IF NOT EXISTS ix_audit_occurred_at ON audit_events (occurred_at DESC);
    CREATE INDEX IF NOT EXISTS ix_audit_tenant ON audit_events (tenant_id, occurred_at DESC);
    CREATE INDEX IF NOT EXISTS ix_audit_actor ON audit_events (actor_id, occurred_at DESC);
    CREATE INDEX IF NOT EXISTS ix_audit_action ON audit_events (action, occurred_at DESC);
    CREATE INDEX IF NOT EXISTS ix_audit_corr ON audit_events (correlation_id);
    """)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_events;")
"""add audit_outbox + event_id on audit_events

Revision ID: e771b7ca6fe8
Revises: 9d5242753bc8
Create Date: 2025-10-10 04:20:02.439052+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e771b7ca6fe8'
down_revision = '9d5242753bc8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1) event_id on audit_events (idempotent, backfill if extension exists)
    op.execute("""
    ALTER TABLE audit_events
      ADD COLUMN IF NOT EXISTS event_id UUID;
    """)

    # Try to backfill missing event_ids (works if pgcrypto or uuid-ossp is installed)
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
        UPDATE audit_events SET event_id = gen_random_uuid() WHERE event_id IS NULL;
      ELSIF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        UPDATE audit_events SET event_id = uuid_generate_v4() WHERE event_id IS NULL;
      END IF;
    END$$;
    """)

    op.execute("""
    ALTER TABLE audit_events
      ALTER COLUMN event_id SET NOT NULL;
    """)

    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS ux_audit_events_event_id
      ON audit_events (event_id);
    """)

    # 2) audit_outbox table
    op.execute("""
    CREATE TABLE IF NOT EXISTS audit_outbox (
      id               BIGSERIAL PRIMARY KEY,
      event_id         UUID NOT NULL UNIQUE,
      created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
      attempts         INTEGER NOT NULL DEFAULT 0,
      last_error       TEXT NULL,
      next_retry_at    TIMESTAMPTZ NULL,
      payload          JSONB NOT NULL,
      processed_redis  BOOLEAN NOT NULL DEFAULT false,
      processed_rds    BOOLEAN NOT NULL DEFAULT false
    );
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS ix_audit_outbox_pending
      ON audit_outbox (processed_redis, processed_rds, next_retry_at, created_at);
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_audit_outbox_pending;")
    op.execute("DROP TABLE IF EXISTS audit_outbox;")

    op.execute("DROP INDEX IF EXISTS ux_audit_events_event_id;")
    op.execute("ALTER TABLE audit_events DROP COLUMN IF EXISTS event_id;")
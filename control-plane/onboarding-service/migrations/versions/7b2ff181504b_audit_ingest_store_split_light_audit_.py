"""audit ingest/store split: light audit_events + heavy audit_store

Revision ID: 7b2ff181504b
Revises: e771b7ca6fe8
Create Date: 2025-10-16 20:13:08.081735+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = '7b2ff181504b'
down_revision = 'e771b7ca6fe8'
branch_labels = None
depends_on = None

def upgrade():
    # --- Ensure uuid generator is available (prefer pgcrypto.gen_random_uuid(); fallback to uuid-ossp) ---
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    # --- AUDIT_Events: make it write-optimized ingest table ---
    # Add columns (use server_default for NOT NULL adds, then drop the default to avoid sticky defaults)
    #op.add_column(
    #    "audit_events",
    #    sa.Column("event_id", pg.UUID(as_uuid=False), nullable=True)  # will backfill then set NOT NULL + UNIQUE
    #)
    op.add_column("audit_events", sa.Column("service", sa.Text(), nullable=False, server_default=sa.text("'onboarding-service'")))
    op.add_column("audit_events", sa.Column("env", sa.Text(), nullable=False, server_default=sa.text("'dev'")))
    op.add_column("audit_events", sa.Column("method", sa.Text(), nullable=True))
    op.add_column("audit_events", sa.Column("processed_redis", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("audit_events", sa.Column("processed_rds", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("audit_events", sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("audit_events", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("audit_events", sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True))

    # Backfill event_id for existing rows using gen_random_uuid() if available, else uuid_generate_v4()
    op.execute("""
    UPDATE audit_events
       SET event_id = COALESCE(event_id,
                               CASE
                                 WHEN to_regproc('pgcrypto.gen_random_uuid') IS NOT NULL THEN gen_random_uuid()
                                 ELSE uuid_generate_v4()
                               END)
    """)

    # Add NOT NULL + UNIQUE on event_id
    op.alter_column("audit_events", "event_id", nullable=False)
    op.create_unique_constraint("uq_audit_events_event_id", "audit_events", ["event_id"])

    # Drop sticky defaults on service/env to force app to set them explicitly going forward
    op.alter_column("audit_events", "service", server_default=None)
    op.alter_column("audit_events", "env", server_default=None)

    # Drop heavy BTREE indexes if they exist (write-optimization)
    op.execute("DROP INDEX IF EXISTS ix_audit_occurred_at;")
    op.execute("DROP INDEX IF EXISTS ix_audit_tenant;")
    op.execute("DROP INDEX IF EXISTS ix_audit_actor;")
    op.execute("DROP INDEX IF EXISTS ix_audit_action;")
    op.execute("DROP INDEX IF EXISTS ix_audit_corr;")

    # Create light BRIN index on time for cheap range scans/retention
    op.execute("""
    CREATE INDEX IF NOT EXISTS brin_audit_events_occurred_at
        ON audit_events
     USING BRIN (occurred_at)
    """)

    # --- AUDIT_Store: heavy, query-optimized sink table ---
    op.create_table(
        "audit_store",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_id", pg.UUID(as_uuid=False), nullable=False, unique=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.Text(), nullable=False),
        sa.Column("env", sa.Text(), nullable=False),
        sa.Column("tenant_id", pg.UUID(as_uuid=False), nullable=True),
        sa.Column("actor_id", pg.UUID(as_uuid=False), nullable=True),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column("correlation_id", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.Text(), nullable=True),
        sa.Column("route", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("target_type", sa.Text(), nullable=True),
        sa.Column("target_id", sa.Text(), nullable=True),
        sa.Column("method", sa.Text(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("source_ip", pg.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("request_size", sa.Integer(), nullable=True),
        sa.Column("response_size", sa.Integer(), nullable=True),
        sa.Column("payload_redacted", pg.JSONB(), nullable=True),
        sa.Column("payload_hash", sa.Text(), nullable=True),
        sa.Column("checksum", sa.Text(), nullable=True),
    )

    # Query-side indexes (BTREE) - fine here because writes are async
    op.create_index("ix_store_occurred_desc", "audit_store", ["occurred_at"], unique=False, postgresql_using="btree")
    op.create_index("ix_store_tenant", "audit_store", ["tenant_id", "occurred_at"], unique=False, postgresql_using="btree")
    op.create_index("ix_store_actor", "audit_store", ["actor_id", "occurred_at"], unique=False, postgresql_using="btree")
    op.create_index("ix_store_action", "audit_store", ["action", "occurred_at"], unique=False, postgresql_using="btree")
    op.create_index("ix_store_corr", "audit_store", ["correlation_id"], unique=False, postgresql_using="btree")


def downgrade():
    # Drop audit_store + its indexes
    op.drop_index("ix_store_corr", table_name="audit_store")
    op.drop_index("ix_store_action", table_name="audit_store")
    op.drop_index("ix_store_actor", table_name="audit_store")
    op.drop_index("ix_store_tenant", table_name="audit_store")
    op.drop_index("ix_store_occurred_desc", table_name="audit_store")
    op.drop_table("audit_store")

    # Drop BRIN index on audit_events
    op.execute("DROP INDEX IF EXISTS brin_audit_events_occurred_at;")

    # Remove constraints and columns added to audit_events
    op.drop_constraint("uq_audit_events_event_id", "audit_events", type_="unique")

    # Drop columns (reverse order is safer for some backends)
    op.drop_column("audit_events", "next_retry_at")
    op.drop_column("audit_events", "last_error")
    op.drop_column("audit_events", "attempts")
    op.drop_column("audit_events", "processed_rds")
    op.drop_column("audit_events", "processed_redis")
    op.drop_column("audit_events", "method")
    op.drop_column("audit_events", "env")
    op.drop_column("audit_events", "service")
    op.drop_column("audit_events", "event_id")

    # Optionally recreate original BTREE indexes if you want perfect rollback parity
    # op.execute("CREATE INDEX IF NOT EXISTS ix_audit_occurred_at ON audit_events (occurred_at DESC);")
    # op.execute("CREATE INDEX IF NOT EXISTS ix_audit_tenant
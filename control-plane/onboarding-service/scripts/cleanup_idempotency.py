#!/usr/bin/env python3
import os, time, logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://aegis:aegis@localhost:5432/controlplane")

SQL = text("""
DELETE FROM idempotency_keys
WHERE ttl_expires_at IS NOT NULL
  AND ttl_expires_at < now()
RETURNING id
""")

def main():
    start = time.time()
    engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
    with engine.begin() as conn:
        # ensure index exists (safe if already there)
        conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_idemp_ttl ON idempotency_keys (ttl_expires_at)"
        )
        res = conn.execute(SQL)
        purged = res.rowcount or 0

    dur_ms = int((time.time() - start) * 1000)
    logging.info(
        "idempotency cleanup: purged=%s duration_ms=%s at=%s",
        purged, dur_ms, datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    main()
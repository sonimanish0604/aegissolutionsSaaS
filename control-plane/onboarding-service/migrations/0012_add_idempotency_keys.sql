-- idempotency keys (Postgres)
CREATE TABLE IF NOT EXISTS idempotency_keys (
  id                  BIGSERIAL PRIMARY KEY,
  idempotency_key     TEXT        NOT NULL,
  tenant_id           UUID        NULL,              -- set NOT NULL if you always have tenant
  request_fingerprint TEXT        NOT NULL,          -- sha256(method+path+canonicalized_body)
  method              TEXT        NOT NULL,
  path                TEXT        NOT NULL,
  status_code         INTEGER     NULL,              -- set once result is known
  response_body       BYTEA       NULL,              -- gzipped or raw JSON bytes
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  locked_until        TIMESTAMPTZ NULL,              -- cooperative lock
  ttl_expires_at      TIMESTAMPTZ NULL               -- optional expiry window
);

-- unique constraint ensures one logical op result per (tenant,idemp_key)
CREATE UNIQUE INDEX IF NOT EXISTS uq_idemp_tenant_key
  ON idempotency_keys (tenant_id, idempotency_key);

-- fast lookup if no tenant scoping yet:
CREATE UNIQUE INDEX IF NOT EXISTS uq_idemp_key_only
  ON idempotency_keys (idempotency_key) WHERE tenant_id IS NULL;

-- help dedupe accidental replays with different keys but same payload
CREATE INDEX IF NOT EXISTS ix_idemp_fingerprint
  ON idempotency_keys (request_fingerprint);

-- housekeeping
CREATE INDEX IF NOT EXISTS ix_idemp_ttl ON idempotency_keys (ttl_expires_at);

-- trigger to keep updated_at fresh
CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_idemp_touch ON idempotency_keys;
CREATE TRIGGER trg_idemp_touch
BEFORE UPDATE ON idempotency_keys
FOR EACH ROW EXECUTE PROCEDURE touch_updated_at();
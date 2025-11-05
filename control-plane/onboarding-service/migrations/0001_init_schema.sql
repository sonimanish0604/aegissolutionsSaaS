-- ================================
-- Aegis Control Plane (Onboarding)
-- Initial schema for tenancy, identity, marketplace, billing, telemetry
-- Postgres dialect
-- ================================

-- ---------- Enums ----------
DO $$ BEGIN
  CREATE TYPE tenant_status       AS ENUM ('pending_activation','active','suspended','canceled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE user_status         AS ENUM ('active','invited','disabled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE auth_method         AS ENUM ('sso','password','saml','oidc');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE role                AS ENUM ('owner','admin','developer','auditor','billing');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE provider            AS ENUM ('aws','azure','gcp','direct');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE registration_status AS ENUM ('pending','resolved','error');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE entitlement_status  AS ENUM ('active','suspended','canceled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE api_key_status      AS ENUM ('active','revoked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE tenant_product_status AS ENUM ('active','trial','suspended');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE plan_code           AS ENUM ('free','standard','enterprise');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE environment         AS ENUM ('live','test');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE actor_type          AS ENUM ('user','system','webhook');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------- Tables ----------

-- tenants
CREATE TABLE IF NOT EXISTS tenants (
  tenant_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_slug     text NOT NULL UNIQUE,
  name            text,
  status          tenant_status NOT NULL DEFAULT 'pending_activation',
  region          text,                  -- e.g., "us", "eu"
  settings        jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);

-- users (global)
CREATE TABLE IF NOT EXISTS users (
  user_id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email           citext NOT NULL UNIQUE,
  name            text,
  status          user_status NOT NULL DEFAULT 'active',
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz,
  last_login      timestamptz
);

-- identities (auth providers for users)
CREATE TABLE IF NOT EXISTS identities (
  identity_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  provider        auth_method NOT NULL,
  subject         text NOT NULL,         -- provider's sub / id
  email           citext,
  created_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (provider, subject)
);
CREATE INDEX IF NOT EXISTS idx_identities_email ON identities(email);

-- memberships (user belongs to tenant)
CREATE TABLE IF NOT EXISTS memberships (
  membership_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  user_id             uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role                role NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  last_role_change_at timestamptz,
  granted_by_user_id  uuid,
  UNIQUE (tenant_id, user_id)
);

-- products (your engines/APIs)
CREATE TABLE IF NOT EXISTS products (
  product_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text NOT NULL UNIQUE,   -- e.g., "pdf_scanner"
  name            text,
  description     text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- tenant_products (which tenant uses which product/plan)
CREATE TABLE IF NOT EXISTS tenant_products (
  tenant_product_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  product_id         uuid NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
  status             tenant_product_status NOT NULL DEFAULT 'active',
  plan               plan_code NOT NULL DEFAULT 'free',
  limits             jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at         timestamptz NOT NULL DEFAULT now(),
  activated_at       timestamptz,
  UNIQUE (tenant_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_tenant_products_tenant ON tenant_products(tenant_id);

-- marketplace_registrations (ingest/raw linking from marketplaces)
CREATE TABLE IF NOT EXISTS marketplace_registrations (
  registration_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  provider            provider NOT NULL,
  external_account_id text,
  subscription_id     text,
  product_code        text,
  plan                plan_code,
  status              registration_status NOT NULL DEFAULT 'pending',
  token_hash          text,
  idempotency_key     text,
  raw_payload         jsonb,
  created_at          timestamptz NOT NULL DEFAULT now(),
  UNIQUE (provider, external_account_id),
  UNIQUE (provider, subscription_id)
);
CREATE INDEX IF NOT EXISTS idx_mkt_reg_tenant ON marketplace_registrations(tenant_id);

-- entitlements (normalized current state)
CREATE TABLE IF NOT EXISTS entitlements (
  entitlement_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  provider        provider NOT NULL,
  subscription_id text NOT NULL,
  plan            plan_code,
  status          entitlement_status NOT NULL DEFAULT 'active',
  limits          jsonb NOT NULL DEFAULT '{}'::jsonb,
  last_checked_at timestamptz,
  UNIQUE (tenant_id, provider, subscription_id)
);
CREATE INDEX IF NOT EXISTS idx_entitlements_tenant ON entitlements(tenant_id);

-- webhook_events (dedupe + replay safety)
CREATE TABLE IF NOT EXISTS webhook_events (
  webhook_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider         provider NOT NULL,
  event_id         text NOT NULL,
  received_at      timestamptz NOT NULL DEFAULT now(),
  payload          jsonb,
  signature        text,
  processed        boolean NOT NULL DEFAULT false,
  UNIQUE (provider, event_id)
);
CREATE INDEX IF NOT EXISTS idx_webhook_processed ON webhook_events(processed);

-- api_keys (secure storage)
CREATE TABLE IF NOT EXISTS api_keys (
  key_id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  name             text,
  scope            jsonb NOT NULL DEFAULT '[]'::jsonb,
  key_prefix       text,
  last_four        text,
  hash             text NOT NULL,                 -- store digest only
  environment      environment NOT NULL DEFAULT 'live',
  status           api_key_status NOT NULL DEFAULT 'active',
  created_by_user_id uuid REFERENCES users(user_id),
  expires_at       timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  last_used_at     timestamptz,
  UNIQUE (tenant_id, hash)
);
CREATE INDEX IF NOT EXISTS idx_apikeys_tenant ON api_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_apikeys_prefix ON api_keys(tenant_id, key_prefix);

-- audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
  audit_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  user_id       uuid REFERENCES users(user_id),
  actor_type    actor_type NOT NULL DEFAULT 'user',
  event_type    text NOT NULL,
  resource_type text,
  resource_id   uuid,
  ip            inet,
  user_agent    text,
  timestamp     timestamptz NOT NULL DEFAULT now(),
  metadata      jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_time ON audit_logs(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(tenant_id, event_type);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);

-- billing_events (money in minor units)
CREATE TABLE IF NOT EXISTS billing_events (
  billing_event_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  event_type        text NOT NULL,  -- e.g., usage.recorded
  units             integer,
  unit_price_cents  integer,
  amount_cents      integer,
  currency          char(3),
  source            provider NOT NULL DEFAULT 'direct',
  idempotency_key   text,
  event_time        timestamptz NOT NULL DEFAULT now(),
  created_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_billing_tenant_event_time ON billing_events(tenant_id, event_time);
CREATE INDEX IF NOT EXISTS idx_billing_tenant_created ON billing_events(tenant_id, created_at);

-- telemetry (OLTP-friendly; consider TSDB for raw high-volume)
CREATE TABLE IF NOT EXISTS telemetry (
  telemetry_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  product_code  text,
  api_endpoint  text,
  latency_ms    integer,
  status_code   integer,
  timestamp     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_telemetry_tenant_time ON telemetry(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_status ON telemetry(tenant_id, status_code);

-- outbox_events (reliable pub)
CREATE TABLE IF NOT EXISTS outbox_events (
  outbox_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  aggregate_type text,
  aggregate_id   uuid,
  event_type     text,
  payload        jsonb,
  created_at     timestamptz NOT NULL DEFAULT now(),
  processed      boolean NOT NULL DEFAULT false,
  processed_at   timestamptz
);
CREATE INDEX IF NOT EXISTS idx_outbox_processed ON outbox_events(processed);
CREATE INDEX IF NOT EXISTS idx_outbox_aggregate ON outbox_events(aggregate_type, aggregate_id);
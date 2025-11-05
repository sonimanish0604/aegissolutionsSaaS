"""reconcile: create missing core tables

Revision ID: 8c6fd19ffa26
Revises: 7b2ff181504b
Create Date: 2025-10-17 04:28:46.328947+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8c6fd19ffa26'
down_revision = '7b2ff181504b'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "citext";')

    # Enums (only create if not exists)
    op.execute("""
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
    """)

    # Core tables (trimmed, safe if they already exist)
    op.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
      tenant_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_slug TEXT UNIQUE NOT NULL,
      name TEXT,
      status tenant_status NOT NULL DEFAULT 'pending_activation',
      region TEXT,
      settings JSONB NOT NULL DEFAULT '{}'::jsonb,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      deleted_at TIMESTAMPTZ
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
      user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      email CITEXT UNIQUE NOT NULL,
      name TEXT,
      status user_status NOT NULL DEFAULT 'active',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ,
      last_login TIMESTAMPTZ
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS identities (
      identity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
      provider auth_method NOT NULL,
      subject TEXT NOT NULL,
      email CITEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (provider, subject)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
      membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
      user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
      role role NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      last_role_change_at TIMESTAMPTZ,
      granted_by_user_id UUID,
      UNIQUE (tenant_id, user_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS products (
      product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      code TEXT UNIQUE NOT NULL,
      name TEXT,
      description TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS tenant_products (
      tenant_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
      product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
      status tenant_product_status NOT NULL DEFAULT 'active',
      plan plan_code NOT NULL DEFAULT 'free',
      limits JSONB NOT NULL DEFAULT '{}'::jsonb,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      activated_at TIMESTAMPTZ,
      UNIQUE (tenant_id, product_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS marketplace_registrations (
      registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
      provider provider NOT NULL,
      external_account_id TEXT,
      subscription_id TEXT,
      product_code TEXT,
      plan plan_code,
      status registration_status NOT NULL DEFAULT 'pending',
      token_hash TEXT,
      idempotency_key TEXT,
      raw_payload JSONB,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (provider, external_account_id),
      UNIQUE (provider, subscription_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS entitlements (
      entitlement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
      provider provider NOT NULL,
      subscription_id TEXT NOT NULL,
      plan plan_code,
      status entitlement_status NOT NULL DEFAULT 'active',
      limits JSONB NOT NULL DEFAULT '{}'::jsonb,
      last_checked_at TIMESTAMPTZ,
      UNIQUE (tenant_id, provider, subscription_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS webhook_events (
      webhook_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      provider provider NOT NULL,
      event_id TEXT NOT NULL,
      received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      payload JSONB,
      signature TEXT,
      processed BOOLEAN NOT NULL DEFAULT false,
      UNIQUE (provider, event_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
      key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
      name TEXT,
      scope JSONB NOT NULL DEFAULT '[]'::jsonb,
      key_prefix TEXT,
      last_four TEXT,
      hash TEXT NOT NULL,
      environment environment NOT NULL DEFAULT 'live',
      status api_key_status NOT NULL DEFAULT 'active',
      created_by_user_id UUID REFERENCES users(user_id),
      expires_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      last_used_at TIMESTAMPTZ,
      UNIQUE (tenant_id, hash)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS idempotency_keys (
      id BIGSERIAL PRIMARY KEY,
      idempotency_key TEXT NOT NULL,
      tenant_id UUID NULL,
      request_fingerprint TEXT NOT NULL,
      method TEXT NOT NULL,
      path TEXT NOT NULL,
      status_code INTEGER NULL,
      response_body BYTEA NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      locked_until TIMESTAMPTZ NULL,
      ttl_expires_at TIMESTAMPTZ NULL
    );
    """)

    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_idemp_tenant_key ON idempotency_keys (tenant_id, idempotency_key);
    CREATE UNIQUE INDEX IF NOT EXISTS uq_idemp_key_only ON idempotency_keys (idempotency_key) WHERE tenant_id IS NULL;
    CREATE INDEX IF NOT EXISTS ix_idemp_fingerprint ON idempotency_keys (request_fingerprint);
    CREATE INDEX IF NOT EXISTS ix_idemp_ttl ON idempotency_keys (ttl_expires_at);
    """)

    op.execute("""
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
    """)

def downgrade():
    pass
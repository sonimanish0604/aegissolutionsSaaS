-- Enable useful extensions (idempotent)
CREATE EXTENSION IF NOT EXISTS citext;       -- case-insensitive text (emails)
CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- gen_random_uuid(), hashes
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- optional alternative for UUIDs

-- Trigram & GIN helpers (useful for text lookups/logging later)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

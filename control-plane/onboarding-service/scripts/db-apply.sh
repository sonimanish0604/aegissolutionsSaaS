#!/usr/bin/env bash
set -euo pipefail

# Adjust if your container/name differ
CONTAINER="${CONTAINER:-aegis-pg}"
DB="${DB:-controlplane}"
USER="${USER:-aegis}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIG_DIR="${ROOT_DIR}/migrations"

echo "Applying migrations to ${DB} on container ${CONTAINER} ..."

docker exec -i "${CONTAINER}" psql -U "${USER}" -d "${DB}" -v ON_ERROR_STOP=1 -f - < "${MIG_DIR}/0000_extensions.sql"
docker exec -i "${CONTAINER}" psql -U "${USER}" -d "${DB}" -v ON_ERROR_STOP=1 -f - < "${MIG_DIR}/0001_init_schema.sql"

echo "✅ Done."
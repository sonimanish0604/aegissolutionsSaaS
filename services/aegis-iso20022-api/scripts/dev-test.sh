#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.audit-dev.yml"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Compose file $COMPOSE_FILE not found in repo root" >&2
  exit 1
fi

trap 'docker compose -f $COMPOSE_FILE down --remove-orphans' EXIT

docker compose -f $COMPOSE_FILE down --remove-orphans

docker compose -f $COMPOSE_FILE up -d --build

# Wait briefly for services
sleep 5

docker compose -f $COMPOSE_FILE exec translator bash -lc "pip install -r services/aegis-iso20022-api/requirements.txt && pytest services/aegis-iso20022-api/tests -q"


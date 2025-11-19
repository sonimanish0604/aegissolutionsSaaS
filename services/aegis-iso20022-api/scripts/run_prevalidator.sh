#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${APP_HOME:-/app}:${PYTHONPATH:-}"

exec uvicorn src.prevalidator_api.app:app --host 0.0.0.0 --port "${PREVALIDATOR_PORT:-8081}"

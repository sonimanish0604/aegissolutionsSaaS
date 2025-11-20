#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAPS=${KAFKA_BOOTSTRAP_SERVERS:-}
TIMEOUT=${WAIT_FOR_KAFKA_TIMEOUT:-60}

if [ -z "$BOOTSTRAPS" ]; then
  echo "Kafka bootstrap servers not set; proceeding with logging emitter"
else
  for endpoint in ${BOOTSTRAPS//,/ }; do
    host=${endpoint%%:*}
    port=${endpoint##*:}
    if [ "$host" = "$port" ]; then
      port=9092
    fi
    echo "Waiting for Kafka broker $host:$port ..."
    WAIT_HOST=$host WAIT_PORT=$port python - <<'PY'
import os, socket, sys
host = os.environ['WAIT_HOST']
port = int(os.environ['WAIT_PORT'])
sock = socket.socket()
sock.settimeout(int(os.environ.get('TIMEOUT', '60')))
try:
    sock.connect((host, port))
except OSError:
    sys.exit(1)
else:
    sys.exit(0)
PY
    if [ $? -ne 0 ]; then
      echo "Kafka broker $host:$port unreachable, falling back to logging emitter"
      break
    fi
  done
fi

echo "Starting translator API"
export PYTHONPATH="${APP_HOME:-/app}:${PYTHONPATH:-}"
exec uvicorn src.translator_api.routes:app --host 0.0.0.0 --port 8080

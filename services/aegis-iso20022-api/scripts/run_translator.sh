#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAPS=${KAFKA_BOOTSTRAP_SERVERS:-}
TIMEOUT=${WAIT_FOR_KAFKA_TIMEOUT:-180}

if [ -n "$BOOTSTRAPS" ]; then
  for endpoint in ${BOOTSTRAPS//,/ }; do
    host=${endpoint%%:*}
    port=${endpoint##*:}
    if [ "$host" = "$port" ]; then
      port=9092
    fi
    echo "Waiting for Kafka broker $host:$port ..."
    end=$((SECONDS + TIMEOUT))
    while true; do
      WAIT_HOST=$host WAIT_PORT=$port python - <<'PY'
import os, socket, sys
host = os.environ['WAIT_HOST']
port = int(os.environ['WAIT_PORT'])
s = socket.socket()
s.settimeout(5)
try:
    s.connect((host, port))
except OSError:
    sys.exit(1)
else:
    sys.exit(0)
PY
      if [ $? -eq 0 ]; then
        echo "Kafka broker $host:$port is available."
        break
      fi
      if [ $SECONDS -ge $end ]; then
        echo "Timed out waiting for Kafka broker $host:$port"
        exit 1
      fi
      sleep 5
    done
  done
fi

echo "Starting translator API"
export PYTHONPATH="${APP_HOME:-/app}:${PYTHONPATH:-}"
exec uvicorn src.translator_api.routes:app --host 0.0.0.0 --port 8080

if [ -z "$BOOTSTRAPS" ]; then
  echo "Kafka bootstrap servers not set; proceeding with dummy emitter"
fi

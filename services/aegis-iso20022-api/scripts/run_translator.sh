#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAPS=${KAFKA_BOOTSTRAP_SERVERS:-}
TIMEOUT=${WAIT_FOR_KAFKA_TIMEOUT:-60}
SLEEP_INTERVAL=${WAIT_FOR_KAFKA_SLEEP:-5}
REQUIRE_KAFKA=${REQUIRE_KAFKA:-false}

if [ -z "$BOOTSTRAPS" ]; then
  echo "Kafka bootstrap servers not set; proceeding with logging emitter"
else
  echo "Kafka bootstrap servers: $BOOTSTRAPS"
  check_kafka() {
    python - "$@" <<'PY'
import socket, sys
status = 0
for endpoint in sys.argv[1:]:
    if ':' in endpoint:
        host, port = endpoint.rsplit(':', 1)
    else:
        host, port = endpoint, '9092'
    sock = socket.socket()
    sock.settimeout(3)
    try:
        sock.connect((host, int(port)))
    except OSError:
        status = 1
        break
    finally:
        sock.close()
sys.exit(status)
PY
  }

  deadline=$((SECONDS+TIMEOUT))
  while true; do
    set +e
    check_kafka ${BOOTSTRAPS//,/ }
    status=$?
    set -e
    if [ $status -eq 0 ]; then
      echo "Kafka brokers reachable"
      break
    fi

    if [ "$REQUIRE_KAFKA" = "true" ]; then
      if [ $SECONDS -ge $deadline ]; then
        echo "Kafka brokers still unavailable after ${TIMEOUT}s; exiting"
        exit 1
      fi
      echo "Kafka not ready yet; retrying in ${SLEEP_INTERVAL}s"
      sleep "$SLEEP_INTERVAL"
    else
      echo "Kafka unreachable, falling back to logging emitter"
      break
    fi
  done
fi

echo "Starting translator API"
export PYTHONPATH="${APP_HOME:-/app}:${APP_HOME:-/app}/src:${PYTHONPATH:-}"
exec uvicorn src.translator_api.routes:app --host 0.0.0.0 --port 8080

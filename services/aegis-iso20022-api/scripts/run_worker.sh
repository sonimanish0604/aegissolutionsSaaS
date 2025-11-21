#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAPS=${KAFKA_BOOTSTRAP_SERVERS:-}
S3_ENDPOINT=${S3_ENDPOINT_URL:-}
KAFKA_WAIT=${WAIT_FOR_KAFKA_TIMEOUT:-120}
S3_WAIT=${WAIT_FOR_S3_TIMEOUT:-60}
SLEEP_INTERVAL=${WAIT_FOR_SERVICES_SLEEP:-5}

wait_for_kafka() {
  if [ -z "$BOOTSTRAPS" ]; then
    echo "KAFKA_BOOTSTRAP_SERVERS not set; skipping Kafka wait"
    return 0
  fi

  deadline=$((SECONDS+KAFKA_WAIT))
  while true; do
    python - "$BOOTSTRAPS" <<'PY'
import socket, sys
endpoints = sys.argv[1].split(",")
for endpoint in endpoints:
    host, _, port = endpoint.partition(":")
    port = int(port or 9092)
    sock = socket.socket()
    sock.settimeout(3)
    try:
        sock.connect((host, port))
    except OSError:
        sys.exit(1)
    finally:
        sock.close()
sys.exit(0)
PY
    status=$?
    if [ $status -eq 0 ]; then
      echo "Kafka reachable"
      return 0
    fi

    if [ $SECONDS -ge $deadline ]; then
      echo "Kafka unreachable after ${KAFKA_WAIT}s"
      return 1
    fi
    echo "Kafka not ready yet; retrying in ${SLEEP_INTERVAL}s"
    sleep "$SLEEP_INTERVAL"
  done
}

wait_for_s3() {
  if [ -z "$S3_ENDPOINT" ]; then
    echo "S3_ENDPOINT_URL not set; skipping S3 wait"
    return 0
  fi

  deadline=$((SECONDS+S3_WAIT))
  while true; do
    python - "$S3_ENDPOINT" <<'PY'
import sys, urllib.request
url = sys.argv[1]
try:
    with urllib.request.urlopen(url, timeout=3) as resp:
        resp.read(1)
except Exception:
    sys.exit(1)
else:
    sys.exit(0)
PY
    status=$?
    if [ $status -eq 0 ]; then
      echo "S3 endpoint reachable"
      return 0
    fi
    if [ $SECONDS -ge $deadline ]; then
      echo "S3 endpoint unreachable after ${S3_WAIT}s"
      return 1
    fi
    echo "S3 endpoint not ready yet; retrying in ${SLEEP_INTERVAL}s"
    sleep "$SLEEP_INTERVAL"
  done
}

wait_for_kafka
wait_for_s3

export PYTHONPATH="${APP_HOME:-/app}:${APP_HOME:-/app}/src:${PYTHONPATH:-}"
python scripts/audit_worker.py

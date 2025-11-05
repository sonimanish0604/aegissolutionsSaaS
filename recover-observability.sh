#!/usr/bin/env bash
set -euo pipefail

echo "🐳 Ensuring namespaces..."
kubectl get ns aegis >/dev/null 2>&1 || kubectl create ns aegis
kubectl get ns observability >/dev/null 2>&1 || kubectl create ns observability

echo "🟣 Reassert OpenTelemetry Collector (idempotent)"
helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
  -n observability \
  -f shared/infra/otel/otel-values.yaml

echo "🟡 Reassert Postgres (idempotent)"
helm upgrade --install postgres bitnami/postgresql \
  -n aegis \
  --reuse-values \
  -f shared/infra/postgres/postgres-values.yaml

echo "🔴 Reassert Redis (idempotent)"
helm upgrade --install redis bitnami/redis \
  -n aegis \
  -f shared/infra/redis/redis-values.yaml

# (Optional) Reassert Loki/Tempo/Prometheus if you added their values files
# helm upgrade --install loki grafana/loki -n observability -f shared/infra/loki/loki-values.yaml
# helm upgrade --install tempo grafana/tempo -n observability -f shared/infra/tempo/tempo-values.yaml
# helm upgrade --install kps prometheus-community/kube-prometheus-stack -n observability -f shared/infra/kps/kps-values.yaml

echo "🩺 Health check:"
kubectl get pods -A | egrep 'CrashLoop|Error|BackOff' || echo "✅ No pod errors"
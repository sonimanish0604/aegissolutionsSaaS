#!/usr/bin/env bash
set -euo pipefail
kubectl create ns observability >/dev/null 2>&1 || true
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts >/dev/null
helm repo update >/dev/null
helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
  -n observability -f shared/infra/otel/otel-values.yaml
kubectl -n observability get pods,svc

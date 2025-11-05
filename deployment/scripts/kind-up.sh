#!/usr/bin/env bash
set -euo pipefail
kind delete cluster --name aegis >/dev/null 2>&1 || true
kind create cluster --name aegis --config shared/infra/kind/kind-aegis.yaml
kubectl cluster-info
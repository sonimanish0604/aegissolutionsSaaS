#!/usr/bin/env bash
set -euo pipefail
istioctl x precheck || true
istioctl install -y --set profile=minimal --set values.gateways.istio-ingressgateway.enabled=true
kubectl -n istio-system patch svc istio-ingressgateway --type='json' -p='[
  {"op":"replace","path":"/spec/type","value":"NodePort"},
  {"op":"add","path":"/spec/ports/0/nodePort","value":30080},
  {"op":"add","path":"/spec/ports/1/nodePort","value":30443}
]'
kubectl label ns aegis istio-injection=enabled --overwrite || kubectl create ns aegis && kubectl label ns aegis istio-injection=enabled --overwrite
kubectl get pods -n istio-system

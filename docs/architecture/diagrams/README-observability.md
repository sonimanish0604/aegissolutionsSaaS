# Aegis Dev Observability & Mesh (Kind + Istio minimal + OTel Collector)

This diagram (`aegis-istio-otel-kind.ascii`) captures our local dev stack:
- Kind cluster with host ports 80/443 mapped to NodePorts 30080/30443
- Istio (profile=minimal) with one `istio-ingressgateway` (NodePort)
- Namespace `aegis` labeled `istio-injection=enabled` for Envoy sidecars
- OpenTelemetry Collector in `observability` (OTLP 4317/4318) with logging exporter

## Quick commands
```bash
make all-observability       # kind + istio + otel
kubectl -n istio-system get pods,svc
kubectl -n observability get pods,svc

# Onboarding-Service TODOs

## Idempotency (v1.0 done)
- ✅ Idempotency table, logic, and migrations implemented.
- ⏳ [TODO] Add TTL cleanup job for `idempotency_keys`:
  - Decide final environment (pg_cron / ECS Scheduled Task / Lambda).
  - Target cadence: daily @ 02:00 UTC.
  - Verify metrics + log integration.

## Staging readiness checklist
- [ ] Configure `DATABASE_URL` for staging RDS.
- [ ] Add structured logs (tenant_id, idempotency_key, status_code).
- [ ] Integration tests for cleanup job.
- [ ] Observability dashboard (Grafana or CloudWatch metrics).
- [ ] API Gateway / Cognito setup (for staging tenant onboarding).

_Last updated: 2025-10-07_
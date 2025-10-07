# Control Plane TODOs

This file tracks in-flight and planned items across the Control Plane microservices.

---

## ✅ Onboarding Service

- [x] Idempotency table and logic implemented
- [x] Alembic migrations working
- [ ] Add TTL cleanup job for `idempotency_keys`
- [ ] Implement Audit Logging (`feature/onboarding-audit-logging`)
- [ ] Add unit + integration tests for audit logging
- [ ] Enable structured logs (JSON) with correlation IDs
- [ ] Add rate-limit telemetry metrics
- [ ] Prepare staging config (Render → AWS RDS)

---

## 🧾 Billing & Plans (up next)
- [ ] Define plan catalog (Free, Dev, Pro, Enterprise)
- [ ] Map plan → quota → rate-limits
- [ ] Implement usage counters and reset jobs
- [ ] Prepare stub billing adapter

---

## 🧩 Identity / Access
- [ ] Add basic API key auth + tenant roles
- [ ] Add OAuth2/OIDC scaffolding
- [ ] Configure admin RBAC (`owner/admin/auditor`)

---

_Last updated: 2025-10-07_

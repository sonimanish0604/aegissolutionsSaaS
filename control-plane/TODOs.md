# ✅ Control Plane TODO Tracker

Use `[x]` to mark completion; `[~]` for partial progress (optional emoji 🔄 = in progress).  
Each item can have nested sub-items or linked branches / PRs.

---

## 🧠 Service: Onboarding

| Area | Item | Status | Branch / PR | Notes |
|------|------|---------|--------------|-------|
| **Core** | Idempotency logic | ✅ Done | `feature/onboarding-idempotency` | merged to `develop` |
| **Core** | TTL cleanup job | 🔄 In progress | — | to add after staging infra (pg_cron/ECS) |
| **Audit** | Audit logging DB + service | ☐ Not started | `feature/onboarding-audit-logging` | quick-win target |
| **Audit** | Integration tests for audit log | ☐ | — | after schema merged |
| **Infra** | Structured logging (JSON) | ☐ | — | align format with other control-plane services |
| **Infra** | Correlation-ID propagation | ☐ | — | middleware level |
| **Docs** | Update OpenAPI v1 spec | ☐ | — | after audit endpoints ready |

---

## 💳 Service: Billing

| Area | Item | Status | Branch / PR | Notes |
|------|------|---------|--------------|-------|
| **Plans** | Define plan catalog | ☐ | — | Free/Dev/Pro/Enterprise |
| **Limits** | Implement plan→quota mapping | ☐ | — | ties to Redis limits |
| **Usage** | Usage counters + reset jobs | ☐ | — | daily/monthly rollover |
| **Integration** | Billing adapter (stub) | ☐ | — | to mock AWS Marketplace billing |

---

## 🧰 Service: Identity / Access

| Area | Item | Status | Branch / PR | Notes |
|------|------|---------|--------------|-------|
| **AuthN** | API key authentication | ☐ | — | align with rate-limit middleware |
| **AuthZ** | RBAC roles (owner/admin/auditor) | ☐ | — | base policy JSON |
| **SSO** | OIDC scaffolding | ☐ | — | stub for enterprise tenants |

---

## 🧮 Service: Telemetry / Metrics

| Area | Item | Status | Branch / PR | Notes |
|------|------|---------|--------------|-------|
| **Metrics** | Redis + Postgres usage metrics | ☐ | — |  |
| **Health** | `/healthz` & `/readyz` endpoints | ☐ | — |  |
| **Monitoring** | Dashboard setup | ☐ | — | CloudWatch or Grafana |

---

### 🔄 Legend

| Symbol | Meaning |
|---------|----------|
| ✅ | Completed |
| 🔄 / `[~]` | In progress / partially done |
| ☐ | Not started |

---

_Last updated: {2025-10-07}_

# PR Title
<!-- Conventional Commits preferred: feat:, fix:, chore:, docs:, refactor:, perf:, test:, ci:, build: -->

## 0) Linked Work Item(s)
- Closes #<issue_id> (REQUIRED)
- Change Type: □ Feature □ Bugfix □ Security □ Docs □ Refactor
- Affected Service/Area: `aegis-iso20022-api` | `infra` | `pipeline` | other: _____
- Environments touched: □ Testing (ephemeral) □ Staging □ Production

---

## 1) Summary (What/Why)
<!-- Business value, user impact, and scope -->

---

## 2) Design & Risk Assessment
**Approach:**  
<!-- Design notes or ADR link -->

**Risks & Mitigations:**  
- Risk → Mitigation

**Breaking Changes:** □ No □ Yes (describe + rollback)

---

## 3) Security / Privacy / Compliance
- Threat modeling touched? □ N/A □ Yes (link)
- Secrets/keys changed? □ No □ Yes (rotation details)
- Data classification impact? □ N/A □ Yes (describe)
- Controls referenced:
  - ISO 27001: A.8, A.12, A.14, A.18
  - SOC 2: CC1.x, CC5.x, CC6.x, CC7.x
  - NIST 800-53: CM-3, CM-5, CM-8 (optional)

---

## 4) Tests & Evidence
- Unit tests: □ Added □ Updated □ N/A
- Integration: □ Added □ Updated □ N/A
- Regression suite impact: □ None □ New cases (list)
- CI / Coverage / Static Analysis links:

---

## 5) Deployment / Rollout / Rollback
- Infra/IaC change? □ No □ Yes (Terraform plan link)
- Rollout plan (env order, canary, freeze windows):
- Rollback plan (explicit steps, data considerations):
- Ops runbook updated? □ N/A □ Yes (link)

---

## 6) Audit Log & Manifest
- Change Record ID:
- S3 URI: `s3://change-mgmt-logs/changes/<yyyy>/<mm>/<dd>/<changeId>/`
- `manifest.json` SHA256: ______
- `manifest.sig` SHA256: ______
- Signer (KMS key / PGP): ______
- Evidence bundle uploaded? □ Yes □ No (explain)

---

## 7) Checklist Before Merge
- [ ] Issue linked (no Issue → no merge)
- [ ] Branch follows convention (`feature/<issue>-slug`, etc.)
- [ ] Conventional commit messages used
- [ ] CI (tests + security scans) succeeded
- [ ] Terraform plan reviewed & stored (if IaC)
- [ ] Docs/CHANGELOG updated
- [ ] Evidence pushed to S3 + manifest signed

---

## 8) Screenshots / Logs (optional)

---

## 9) Approvals
- Reviewer(s): @_____
- Security/Privacy (if applicable): @_____
- Change authorization note (solo dev): _self-approval allowed per CM policy, automated gates enforced_

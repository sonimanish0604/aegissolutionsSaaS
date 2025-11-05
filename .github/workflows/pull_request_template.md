## 🧭 Summary
<!-- Briefly describe what this PR does and why -->

## 🧩 Changes Introduced
- [ ] Added Docker Compose setup for local Postgres
- [ ] Added initial schema and migrations
- [ ] Added pre-commit hooks
- [ ] Updated .gitignore

## 🧪 How to Test
1. Run `docker compose up -d` from `/deployment/docker`
2. Execute `./scripts/db-apply.sh` under onboarding-service
3. Verify tables in Adminer (`http://localhost:8080`)

## 📸 Screenshots / Output (if applicable)
<!-- Add screenshots, logs, or Adminer output -->

## 🔐 Security & Compliance
- [ ] No sensitive data committed
- [ ] Environment variables handled via `.env`
- [ ] Confirmed DB credentials not in code

## ✅ Checklist Before Merge
- [ ] All tests/lints pass locally
- [ ] Pre-commit hooks run cleanly (`pre-commit run --all-files`)
- [ ] Documentation updated if needed
- [ ] CI checks pass

---

**Reviewer Notes:**  
_Anything specific for reviewers to look at (e.g., schema naming, migration order, etc.)_

---

> 🟩 **Merging Rule:**  
> Feature branches → `develop`  
> Staging/tested → `main` (after QA)
# Change Management Process (Repository-Level)

This repository follows a controlled change process to ensure traceability, testing, and auditability.

## Workflow Summary
Issue → Branch → Commits → Pull Request → CI Tests → Review → Merge → Change Manifest → Immutable Storage

## Steps

1. **Open an Issue**
   - Describe purpose, risk, desired outcome, and rollback considerations.

2. **Create a Branch**
   - Branch naming convention: `feature/<issue-number>-<slug>` (e.g., `feature/123-cloud-workflow`).
   - Branch is pushed and promoted using the standard flow: `develop → testing → staging → main`.

3. **Commit with Reference**
   - Example: `git commit -m "Add mapping logic for MT202 → pacs.009 [#123]"`.
   - Commits reference the Issue ID.

4. **Open a PR**
   - Include “Closes #123” so GitHub auto-links and closes the issue.
   - Fill the PR template fields (risk, testing evidence, rollback plan).

5. **CI Validation**
   - Linting and unit tests (CI workflow).
   - Mapping regression tests.
   - Security scans (CodeQL, etc.).
   - Cloud connectivity + Terraform plan/apply workflows based on branch.

6. **Merge**
   - PR must be approved and branch up to date.
   - Only protected branches (`develop`, `testing`, `staging`, `main`) receive merges.

7. **Change Manifest Generation**
   - CI produces `manifest.json` and `manifest.sig` summarizing Issue → PR → commits → tests → approvals.
   - The manifest is attached to the PR (Actions artifact) and linked in the PR discussion.

## Supporting Files
Refer to the following automation:

- `.github/workflows/issue-link-check.yml` – ensures commits/PRs reference issues.
- `.github/PULL_REQUEST_TEMPLATE.md` – captures risk/testing sections for every PR.

## Change Manifest & Evidence Packet Format

Each merge generates a JSON manifest and optional evidence files (unit-test reports, regression logs, etc.).

```json
{
  "changeId": "chg-2025-02-04-00012",
  "issue": "#412",
  "pr": 563,
  "branch": "feature/ISSUE-412-add-bic-validation",
  "mergeCommit": "5c2b9f…",
  "mergedAt": "2025-02-04T13:22:10Z",
  "mergedBy": "manish-soni",
  "tests": {
    "unit": "passed",
    "regression": "passed",
    "securityScan": "passed"
  },
  "artifacts": [
    {"name": "unit-test-report.xml", "sha256": "abc123…"},
    {"name": "regression.log", "sha256": "def456…"}
  ]
}
```

### Storage Location
Manifests and evidence artifacts live inside GitHub (Actions artifacts + PR comments). If auditors require an external archive, export the artifact bundle and upload it to SharePoint or another immutable store.

### Evidence Storage
All primary change evidence remains inside GitHub:
- Issues/Projects capture the request, risk, labels, and approvals.
- Pull Requests capture the code diff, CI runs, reviews, and merge metadata.
- GitHub retains immutable timelines/audit logs for every Issue and PR.

Periodic exports (e.g., monthly snapshots) can be generated and uploaded to SharePoint or another archive if required by auditors. (Future enhancement: add an automated export workflow that bundles issue/PR metadata and publishes it to SharePoint.)

# SOC 2 Compliance Automation

This repository publishes a SOC 2 compliance report for every pull request (and for pushes to the `main` or `develop` branches). Each report captures the outcome of the automated test and security checks and is archived in the [`aegis-compliance-evidence`](https://github.com/sonimanish0604/aegis-compliance-evidence) repository for audit purposes.

## Workflow summary

1. **Trigger** – the workflow `.github/workflows/soc2-compliance.yml` runs on `pull_request` events and on pushes to `main` or `develop`.
2. **Checks** – the workflow installs the service dependencies and executes `scripts/soc2_compliance.py`, which:
   - runs `pytest -q`,
   - executes security tooling (`gitleaks`, `semgrep scan`, `syft`, `grype`),
   - captures metadata (timestamp, commit, branch), and
   - writes a JSON report.
3. **Artifacts** – the JSON file is uploaded to the workflow artifacts for quick inspection.
4. **Archival** – if the secret `COMPLIANCE_BOT_TOKEN` is available, the workflow clones the `aegis-compliance-evidence` repository and pushes the report into `reports/<year>/<month>/` with a timestamped filename.

## Required secret

Create a repository secret named `COMPLIANCE_BOT_TOKEN` that holds a GitHub Personal Access Token (or GitHub App token) with **`repo`** scope and access to the `aegis-compliance-evidence` repository (public or private). The workflow skips the publishing step when the secret is not defined, but the compliance checks still run and produce the local artifact.

## Local usage

You can run the compliance script locally:

```bash
cd services/aegis-iso20022-api
python scripts/soc2_compliance.py --output ../../soc2_report.json
```

Use `--skip-pytest` and/or `--skip-security-tools` if you need a quick local report without running the full suite (for example, when debugging the script). The SOC 2 workflow always runs with both sets of checks enabled.

# Release Management & Semantic Versioning

This project promotes code through a four-branch pipeline (`develop → testing → staging → main`)
and uses [semantic-release](https://semantic-release.gitbook.io/) to cut tagged releases that
follow `MAJOR.MINOR.PATCH` semantics. The controls below satisfy the traceability expectations
of SOC 2 and ISO 27001 by ensuring every promotion runs an automated test & compliance suite and
records auditable evidence.

## Branch Promotion Rules

| Source → Target | Automation | Purpose |
|-----------------|------------|---------|
| Feature → `develop` | Unit tests, SOC2 check, conventional commit lint | Integration of new work |
| `develop` → `testing` | Full integration suite (Kafka, S3, KMS) + SOC2 (triggered on PR/merge to `testing`) | Pre-release hardening |
| `testing` → `staging` | Release workflow (SOC2 + semantic-release prerelease) + integration smoke | Release-candidate sign-off |
| `staging` → `main` | Release workflow (SOC2 + semantic-release full release) + integration smoke | Production promotion |

Merges into any protected branch **must** occur via Pull Request so that the associated GitHub
Actions workflows run and their artifacts are captured.

## Conventional Commit Requirements

All commits are linted using `@commitlint/config-conventional`. Accepted types are:

- `feat`: new functionality (triggers a MINOR release)
- `fix`, `hotfix`, `perf`, `refactor`, `revert`: bug fixes or safe improvements (PATCH)
- `docs`: documentation-only changes (no release by default)
- `build`, `ci`, `test`, `chore`: internal plumbing

Use optional scopes to describe the subsystem (e.g. `feat(translator): ...`). Commit headers must
stay under 100 characters and use imperative mood.

## Release Automation

1. **SOC2 Evidence** – The release workflow re-runs `scripts/soc2_compliance.py` so the resulting
   `artifacts/soc2_report.json` reflects the exact code being promoted. The artifact is uploaded
   and attached to the GitHub Release for auditors.
2. **Changelog & Tagging** – `semantic-release` analyses commits since the previous tag,
   determines the next semantic version, updates `CHANGELOG.md`, creates a git tag, and publishes
   a GitHub Release. Releases from `testing` are suffixed with `-beta.*`, from `staging` with
   `-rc.*`, and from `main` produce stable versions.
3. **Evidence Retention** – Release notes reference the uploaded SOC2 report and the workflow logs.
   These artefacts should also be copied to the external evidence repository per the compliance
   runbook.

### Dry-run Locally

You can inspect the next version without publishing by running:

```bash
npm install --no-save semantic-release @semantic-release/{changelog,git,github,commit-analyzer,release-notes-generator}
GITHUB_TOKEN=dummy npx semantic-release --dry-run
```

This command respects `.releaserc.json` and shows the calculated next version and changelog
summary (no tags or commits are created when `--dry-run` is present).

## Pull Request Checklist

Before requesting review on a promotion PR:

- [ ] All commits conform to the expected prefixes (`feat`, `fix`, `hotfix`, …).
- [ ] Required automated checks on the source branch are green.
- [ ] SOC2 evidence from the latest run is uploaded (or linked) in the PR description.
- [ ] New compliance or release-process documentation updates are included if behaviour changed.

Following this checklist keeps the promotion pipeline predictable and protectable for auditors.

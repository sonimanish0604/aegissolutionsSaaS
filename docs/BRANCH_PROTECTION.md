# Branch protection recommendations

To keep `main` and `develop` stable, configure a branch protection rule for each branch in the repository settings. GitHub requires repo admin access for these changes.

Recommended settings:
- **Require a pull request before merging** – even as a solo developer, raise a PR from your feature branch so checks have to pass before merge. Disable “Allow bypassing the pull request requirement”.
- **Require review from Code Owners** – turn this on after adding yourself to `CODEOWNERS` so that every PR records an explicit approval (self-review today, scalable when more reviewers join).
- **Require status checks to pass** – add the SOC2 workflow (`SOC2 Compliance Checks`), the dedicated test workflow (`CI Tests / pytest`), and CodeQL (`CodeQL / analyze (python)` and `CodeQL / analyze (javascript)`) as required checks.
- **Require branches to be up to date** – forces a rebase/merge with the protected branch before merging, ensuring checks run on the merged commit.
- **Require signed commits** – optional but useful when you want tamper evidence for audit trails.
- **Require linear history** – optional, keeps history clean by forbidding merge commits.
- **Include administrators** – ensures the rules apply to every push, including yours.

Because you are the only maintainer, these rules make GitHub block merges until workflows finish successfully. If an urgent fix is needed, temporarily disable the rule (document the reason in your SOC2 evidence repository) and re-enable after the fix is merged.

## Documenting the control

Capture the process in your SOC 2 control narrative:
- Mention that `CODEOWNERS` enforces structured review and that the founder provides final approval.
- Note that AI tooling assists coding/review but the human owner approves merges.
- Explain that the setup is designed to scale as new contributors join (additional owners can be appended to `CODEOWNERS`).

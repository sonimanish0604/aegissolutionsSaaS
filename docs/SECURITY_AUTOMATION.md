# Security automation checklist

The repository now runs automated testing, static analysis, and dependency scans on every pull request. To close the loop, enable the GitHub-native security features listed below (requires repository admin access):

## Enable Dependabot alerts and security updates

1. Navigate to **Settings → Security & analysis**.
2. Turn on **Dependabot alerts** and **Dependabot security updates**.
3. Optional: restrict Dependabot PRs to specific branches if you want to stage updates before merging.

The file `.github/dependabot.yml` configures weekly checks for:
- `pip` dependencies inside `services/aegis-iso20022-api`, and
- GitHub Actions workflows in the repository root.

## Enable secret scanning

1. Under **Settings → Security & analysis**, enable **Secret scanning**.
2. (Recommended) Enable **Secret scanning push protection** so commits that contain secrets are blocked before they land in the repository.

When secret scanning finds an issue, GitHub will open a security alert. Record the triage outcome in your SOC 2 evidence repository.

## Review schedule alignment

- Dependabot PRs will run through the same CI, SOC2, and CodeQL checks as any other pull request.
- Secret scanning and Dependabot alerts raise issues even outside PRs (for example, direct pushes). Resolve alerts promptly to keep the security dashboard clean for auditors.

Document the above controls in your SOC 2 narrative so auditors know how dependency and secret exposure risks are being managed.

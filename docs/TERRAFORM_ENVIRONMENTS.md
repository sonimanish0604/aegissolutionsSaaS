# Terraform Environment Guide

| Environment | Purpose | Automation |
|-------------|---------|------------|
| Testing | Ephemeral infrastructure created per feature, used for automated integration tests, and destroyed immediately afterwards. | `.github/workflows/terraform-testing.yml` applies on `push` to `testing` (or manual dispatch) and always runs `terraform destroy` in a final step. |
| Staging | Long-lived infrastructure that mirrors the production footprint. Use it for end-to-end validation before promotion. | `.github/workflows/terraform-staging.yml` runs a plan for every PR targeting `staging`. Apply runs only via manual dispatch with explicit approval. |
| Production | Always-on infrastructure serving customers. | `.github/workflows/terraform-production.yml` is manual-only and requires an operator to choose plan/apply. |

## Directory Layout

```
marketplace-adapters/aws/environments/
  testing/     # Feature-specific stack, destroyed after tests
  staging/     # Full stack mirroring production
  production/  # Customer-facing stack
```

Each directory carries its own `main.tf`, `variables.tf`, and `versions.tf`. Shared modules remain in
`marketplace-adapters/modules/`. Environment-specific defaults are captured in `variables.tf`
(for example, NAT gateways enabled only in staging/production).

## Best Practices

1. **Remote State** – configure an environment-specific backend (e.g., `aegis-testing-tfstate`) before running any workflow.
2. **Feature Testing** – when building a new feature, run the `terraform-testing` workflow from the feature branch or when merging into `testing`. The workflow guarantees tear-down so environments stay tidy.
3. **Promotion Flow** – only promote infrastructure changes through the branch hierarchy (`develop` → `testing` → `staging` → `main`). The staging/production workflows intentionally require manual approval before an `apply`.
4. **Policy Drift** – use the AWS Role Connectivity workflow to confirm GitHub can still assume the environment-specific IAM roles before running Terraform.
5. **Centralized Logging** – every environment provisions a dedicated CloudTrail trail, encrypted log bucket, and audit-reader IAM role. Adjust retention defaults via the `cloudtrail_*` variables if compliance mandates longer storage.

# AWS Environment Configurations

Each directory under `marketplace-adapters/aws/environments/` contains a standalone
Terraform configuration that provisions the audit pipeline for a single environment.

| Environment | Path                                           | Lifecycle                  |
|-------------|-----------------------------------------------|----------------------------|
| Testing     | `marketplace-adapters/aws/environments/testing`     | Ephemeral. Created per feature and destroyed after tests run. |
| Staging     | `marketplace-adapters/aws/environments/staging`     | Long lived. Mirrors production footprint for pre-prod validation. |
| Production  | `marketplace-adapters/aws/environments/production`  | Always on. Full capacity with all audit components enabled. |

Each `main.tf` reuses the shared modules in `marketplace-adapters/modules/` and
is parameterised via `variables.tf`. Use the GitHub Actions workflows in
`.github/workflows/terraform-*.yml` to plan/apply the configurations with the
correct IAM roles.

# AWS GitHub Actions Role Module

Reusable module that provisions an IAM role trusted by the GitHub Actions
OIDC provider (`token.actions.githubusercontent.com`). It restricts the trust
relationship to a single repository + branch combination and lets callers
attach AWS managed or inline policies.

## Inputs

| Variable | Description | Default |
|----------|-------------|---------|
| `role_name` | Name of the IAM role to create | n/a |
| `description` | Role description | `"GitHub Actions deployment role"` |
| `oidc_provider_arn` | ARN of the GitHub OIDC provider in the AWS account | n/a |
| `github_repository` | Repository in `<owner>/<repo>` format | n/a |
| `branch` | Branch (without `refs/heads/`) authorised to assume the role | n/a |
| `audience` | Expected OIDC audience claim | `sts.amazonaws.com` |
| `managed_policy_arns` | List of AWS managed policies to attach | `[]` |
| `inline_policies` | Map of inline policy documents | `{}` |
| `max_session_duration` | Role session duration in seconds | `3600` |
| `tags` | Extra tags to attach to the role | `{}` |

## Outputs

- `role_name` – name of the IAM role
- `role_arn` – ARN of the IAM role

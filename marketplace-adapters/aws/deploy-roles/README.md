# AWS GitHub Deploy Roles

Terraform configuration that provisions the GitHub Actions OIDC provider and
three IAM roles used to deploy the audit pipeline across AWS environments:

- `AegisTestingDeploy` – assumed by the `testing` branch
- `AegisStagingDeploy` – assumed by the `staging` branch
- `AegisProductionDeploy` – assumed by `main` (production)

Each role trusts the GitHub OIDC provider (`token.actions.githubusercontent.com`)
and is locked down to a single branch in the configured repository. By default,
roles receive the `arn:aws:iam::aws:policy/AdministratorAccess` policy. Adjust
the `managed_policy_arns` variable to scope permissions once the exact service
boundaries are known.

## Usage

```bash
cd marketplace-adapters/aws/deploy-roles
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Configure a remote backend (e.g., S3 + DynamoDB) before running `plan/apply`
in automation.

## Key Variables

| Name | Description | Default |
|------|-------------|---------|
| `aws_region` | Region hosting the IAM resources | `us-east-1` |
| `github_repository` | Repository in `<owner>/<repo>` format | `AegisSolutions/SaaS-Core` |
| `testing_branch` | Branch mapped to the `AegisTestingDeploy` role | `testing` |
| `staging_branch` | Branch mapped to the `AegisStagingDeploy` role | `staging` |
| `production_branch` | Branch mapped to the `AegisProductionDeploy` role | `main` |
| `managed_policy_arns` | List of managed policy ARNs applied to each role | `["arn:aws:iam::aws:policy/AdministratorAccess"]` |
| `tags` | Base tags assigned to the roles | `{ Product = "aegis-iso20022" }` |

`terraform output deploy_role_arns` reveals the final role ARNs for use in
GitHub Actions.

# Audit Pipeline Terraform Blueprints

The `marketplace-adapters` tree contains Terraform configurations for deploying the audit
pipeline across AWS, Google Cloud Platform, and Microsoft Azure. Each stack provisions the
message queue, immutable storage, and key management services required to capture audit events
emitted by the ISO 20022 API.

## Structure

```
marketplace-adapters/
  modules/
    aws_audit_pipeline/     # AWS MSK + S3 + KMS
    aws_cloudtrail/         # AWS CloudTrail + log bucket + KMS + reader role
    gcp_audit_pipeline/     # GCP Pub/Sub + GCS + KMS
    azure_audit_pipeline/   # Azure Event Hubs + Storage + Key Vault
  aws/deploy-roles/         # GitHub OIDC provider + IAM deploy roles
  aws/environments/
    testing/                # Ephemeral testing stack
    staging/                # Long-lived staging stack
    production/             # Production stack
  gcp/testing/              # GCP testing environment using the module
  azure/testing/            # Azure testing environment using the module
```

Each directory under `aws/environments/` is a complete Terraform configuration that reuses the
shared modules. See `docs/TERRAFORM_ENVIRONMENTS.md` for the lifecycle and automation details.

## Common Capabilities

| Capability | AWS | GCP | Azure |
|------------|-----|-----|-------|
| Message broker | MSK Serverless | Pub/Sub Topic | Event Hub |
| Immutable storage | S3 bucket with Object Lock | GCS bucket with retention policy | Storage container with immutability policy |
| Cryptographic signing | KMS CMK | Cloud KMS crypto key | Key Vault RSA key |
| Workload identities | IAM roles | Service Accounts | Azure AD principals |

All stacks enforce at least seven years of retention for audit artefacts and integrate with the
respective key-management service so manifest signatures remain verifiable.

## Usage Notes

- Backends (S3, GCS, Azure Storage) are not defined; configure remote state according to the
  deployment environment.
- NAT gateways, interconnects, and compute workloads are *not* created. Attach these modules to
  the cluster or orchestrator that runs the translator service.
- Destroy the testing stacks after the integration workflow completes to avoid message broker
  charges.
- Every AWS environment automatically enables CloudTrail (management + S3/Lambda data events +
  Insights). Logs are encrypted with dedicated KMS keys and stored in per-environment S3 buckets
  with optional audit-reader IAM roles.

Refer to the README in each cloud-specific directory for detailed invocation instructions.
For AWS, use the environment-specific README at `marketplace-adapters/aws/environments/README.md`.

## GitHub Actions Integration

- Apply `marketplace-adapters/aws/deploy-roles` to create the GitHub Actions OIDC
  provider plus the `AegisTestingDeploy`, `AegisStagingDeploy`, and
  `AegisProductionDeploy` IAM roles.
- Store the resulting role ARNs as repository secrets:
  `AWS_TESTING_DEPLOY_ROLE_ARN`, `AWS_STAGING_DEPLOY_ROLE_ARN`,
  `AWS_PRODUCTION_DEPLOY_ROLE_ARN`.
- The `.github/workflows/aws-role-connectivity.yml` workflow validates that GitHub can assume the
  environment-specific IAM roles.
- Terraform workflows manage each AWS environment:
  - `.github/workflows/terraform-testing.yml` – applies/destroys the ephemeral testing stack.
  - `.github/workflows/terraform-staging.yml` – runs plans on PRs targeting `staging` and requires a manual dispatch to apply.
  - `.github/workflows/terraform-production.yml` – manual-only plan/apply for production.

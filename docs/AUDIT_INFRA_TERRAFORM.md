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
    gcp_audit_pipeline/     # GCP Pub/Sub + GCS + KMS
    azure_audit_pipeline/   # Azure Event Hubs + Storage + Key Vault
  aws/deploy-roles/         # GitHub OIDC provider + IAM deploy roles
  aws/testing/              # Example “testing” environment wiring the AWS module
  gcp/testing/              # GCP testing environment using the module
  azure/testing/            # Azure testing environment using the module
```

Each “testing” configuration is intended for CI-driven integration runs. Use different
workspaces or variable files to adapt them for staging/production.

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

Refer to the README in each cloud-specific directory for detailed invocation instructions.

## GitHub Actions Integration

- Apply `marketplace-adapters/aws/deploy-roles` to create the GitHub Actions OIDC
  provider plus the `AegisTestingDeploy`, `AegisStagingDeploy`, and
  `AegisProductionDeploy` IAM roles.
- Store the resulting role ARNs as repository secrets:
  `AWS_TESTING_DEPLOY_ROLE_ARN`, `AWS_STAGING_DEPLOY_ROLE_ARN`,
  `AWS_PRODUCTION_DEPLOY_ROLE_ARN`.
- The `.github/workflows/audit-aws-terraform.yml` workflow assumes the
  appropriate role (based on branch) and generates a Terraform plan for the AWS
  audit stack.

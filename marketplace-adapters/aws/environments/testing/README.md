# AWS Testing Stack

Terraform configuration that provisions the audit pipeline components used by the ISO 20022
translator integration tests:

- VPC with public/private subnets for ephemeral workloads
- Amazon MSK Serverless cluster for audit events (`audit.events`)
- S3 bucket with Object Lock (7-year retention) and automatic transition to Glacier Deep Archive
- AWS KMS CMK (rotated annually) used for both S3 encryption and manifest signing
- IAM roles for the translator task and manifest signer Lambda
- KMS-encrypted AWS CloudTrail trail (management + S3/Lambda data events + Insights) with environment-specific log bucket and reader role

## Usage

```bash
cd marketplace-adapters/aws/environments/testing
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

The state backend is intentionally undefined; configure an S3 backend via a separate
`backend.tf` or `-backend-config` flags when you integrate this into CI.

## Inputs

Key variables exposed in `variables.tf`:

| Name | Description | Default |
|------|-------------|---------|
| `aws_region` | Deployment region | `us-east-1` |
| `environment` | Environment label | `testing` |
| `name_prefix` | Resource name prefix | `aegis` |
| `enable_nat_gateway` | Whether to provision a NAT Gateway for private subnet egress | `false` |
| `cloudtrail_retention_days` | Days to retain CloudTrail logs | `30` |
| `cloudtrail_include_data_events` | Capture data events for S3/Lambda | `true` |
| `cloudtrail_enable_insights` | Enable CloudTrail Insights | `true` |

Set `enable_nat_gateway = true` if translators or Lambdas require outbound internet access.

## Outputs

- `audit_bucket_name` – immutable archive bucket
- `audit_kms_key_arn` – CMK for encryption and signing
- `msk_cluster_arn` – IAM-authenticated MSK Serverless ARN
- `translator_role_arn`, `manifest_role_arn` – IAM roles to configure in the application stack
- `cloudtrail_trail_arn` – CloudTrail trail ARN
- `cloudtrail_bucket_name` – S3 bucket receiving CloudTrail logs

Destroy the stack after integration runs to avoid MSK serverless hourly charges.

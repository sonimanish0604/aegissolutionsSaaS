# AWS Production Stack

Production hosts the customer-facing ISO 20022 audit pipeline. This configuration provisions:

- Multi-AZ VPC with public/private subnets sized for production workloads
- Amazon MSK Serverless cluster for `audit.events`
- S3 archive bucket with Object Lock + Glacier Deep Archive transition
- AWS KMS CMKs for storage encryption and manifest signing
- IAM roles for translator workloads and the manifest writer
- Dedicated CloudTrail trail (management + S3/Lambda data events + Insights) with its own encrypted bucket and audit-reader role

## Usage

```bash
cd marketplace-adapters/aws/environments/production
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Configure a remote backend/S3 state before running in CI/CD. Apply changes only after staging verification.

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `aws_region` | Deployment region | `us-east-1` |
| `environment` | Environment label | `production` |
| `name_prefix` | Resource name prefix | `aegis` |
| `enable_nat_gateway` | Provision NAT gateway for private subnets | `true` |
| `cloudtrail_retention_days` | CloudTrail log retention (days) | `1825` |
| `cloudtrail_include_data_events` | Capture S3/Lambda data events | `true` |
| `cloudtrail_enable_insights` | Enable CloudTrail Insights | `true` |

## Outputs

- `audit_bucket_name`
- `audit_kms_key_arn`
- `msk_cluster_arn`
- `translator_role_arn`, `manifest_role_arn`
- `cloudtrail_trail_arn`
- `cloudtrail_bucket_name`

Production stacks are always-on; use staging/testing for experimentation.

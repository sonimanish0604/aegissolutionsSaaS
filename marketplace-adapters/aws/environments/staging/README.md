# AWS Staging Stack

Staging mirrors production so that end-to-end tests exercise the same security, logging, and data paths:

- VPC with public/private subnets sized for long-lived workloads
- Amazon MSK Serverless cluster for `audit.events`
- Immutable S3 archive bucket + Object Lock + lifecycle to Glacier
- AWS KMS CMKs for storage encryption and manifest signing
- IAM roles for the translator task and manifest writer
- Dedicated AWS CloudTrail trail (management + S3/Lambda data events + Insights) with its own encrypted log bucket and audit-reader role

## Usage

```bash
cd marketplace-adapters/aws/environments/staging
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Configure a remote backend before running `apply` in automation.

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `aws_region` | Deployment region | `us-east-1` |
| `environment` | Environment label | `staging` |
| `name_prefix` | Resource name prefix | `aegis` |
| `enable_nat_gateway` | Provision NAT gateway for private subnets | `true` |
| `cloudtrail_retention_days` | CloudTrail log retention | `365` |
| `cloudtrail_include_data_events` | Capture S3/Lambda data events | `true` |
| `cloudtrail_enable_insights` | Enable CloudTrail Insights | `true` |

## Outputs

- `audit_bucket_name` – immutable archive bucket
- `audit_kms_key_arn` – CMK for encryption and signing
- `msk_cluster_arn` – IAM-authenticated MSK Serverless ARN
- `translator_role_arn`, `manifest_role_arn` – IAM roles to configure in the application stack
- `cloudtrail_trail_arn` – CloudTrail trail ARN
- `cloudtrail_bucket_name` – S3 bucket storing CloudTrail logs

Keep the stack running; it serves as the gate for production promotions.

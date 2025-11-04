# GCP Testing Stack

Terraform configuration that provisions the Google Cloud equivalents for the audit trail
integration tests:

- Dedicated VPC + subnet for translator workloads
- Pub/Sub topic (`audit.events`) and subscription for manifest processors
- Cloud Storage bucket with uniform access, versioning, and 7-year retention enforcement
- Cloud KMS key ring + crypto key with annual rotation
- Service accounts for translator and manifest components with least-privilege bindings

## Usage

```bash
cd marketplace-adapters/gcp/testing
terraform init
terraform plan -var project_id=$GOOGLE_PROJECT
terraform apply
```

Configure your preferred backend (e.g. Google Cloud Storage) before running in CI.

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `project_id` | Target GCP project | _none_ (required) |
| `region` | Deployment region | `us-east1` |
| `name_prefix` | Resource name prefix | `aegis` |
| `network_cidr` | Subnet CIDR | `10.70.0.0/16` |

## Outputs

- `pubsub_topic` – Fully qualified audit topic name  
- `audit_bucket` – Immutable storage bucket  
- `kms_crypto_key` – KMS key ID used for encryption/signing  
- `translator_service_account` / `manifest_service_account` – Identities mapped to workloads

Destroy the stack after tests to avoid Pub/Sub subscription charges in idle environments.

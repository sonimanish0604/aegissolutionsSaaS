# Azure Testing Stack

Terraform configuration for the Azure flavour of the audit pipeline used during integration
testing:

- Resource group dedicated to the audit trail components
- Event Hubs namespace + hub for `/translate` audit events
- Storage account + container with immutability policy (7-year retention)
- Key Vault + RSA key for manifest signing, with access policies for translator and signer

## Usage

```bash
cd marketplace-adapters/azure/testing
terraform init
terraform plan \
  -var translator_principal_id=$(az ad signed-in-user show --query id -o tsv) \
  -var manifest_principal_id=$(az ad signed-in-user show --query id -o tsv)
terraform apply
```

Provide the correct Azure AD object IDs for the translator and manifest workload identities.

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `location` | Azure region | `eastus` |
| `environment` | Environment label | `testing` |
| `name_prefix` | Resource prefix | `aegis` |
| `translator_principal_id` | Workload identity that sends audit events | _required_ |
| `manifest_principal_id` | Workload identity that signs manifests | _required_ |

## Outputs

- `storage_account_name` – Immutable audit blob store  
- `eventhub_id` – Event Hub for audit events  
- `key_vault_id` / `signing_key_id` – Manifest signing key location

Tear down the stack outside of test windows to avoid Event Hubs charges.

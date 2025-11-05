output "storage_account_name" {
  value       = module.audit_pipeline.storage_account_name
  description = "Storage account for immutable audit blobs."
}

output "eventhub_id" {
  value       = module.audit_pipeline.eventhub_id
  description = "Event Hub identifier."
}

output "key_vault_id" {
  value       = module.audit_pipeline.key_vault_id
  description = "Key Vault containing the signing key."
}

output "signing_key_id" {
  value       = module.audit_pipeline.signing_key_id
  description = "Key Vault key used for manifest signing."
}

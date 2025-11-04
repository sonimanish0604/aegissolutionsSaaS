output "storage_account_name" {
  description = "Name of the storage account that stores immutable audit blobs."
  value       = azurerm_storage_account.audit.name
}

output "eventhub_id" {
  description = "ID of the Event Hub receiving audit events."
  value       = azurerm_eventhub.audit.id
}

output "eventhub_namespace_id" {
  description = "Event Hub namespace ID."
  value       = azurerm_eventhub_namespace.audit.id
}

output "key_vault_id" {
  description = "Key Vault containing the signing key."
  value       = azurerm_key_vault.audit.id
}

output "signing_key_id" {
  description = "Key identifier used for manifest signatures."
  value       = azurerm_key_vault_key.audit.id
}

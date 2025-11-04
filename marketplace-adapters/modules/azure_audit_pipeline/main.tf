locals {
  base_name = lower("${var.name_prefix}${var.environment}")
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  lower   = true
  number  = true
  special = false
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "audit" {
  name                     = replace("${local.base_name}${random_string.suffix.result}", "-", "")
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  min_tls_version          = "TLS1_2"

  allow_nested_items_to_be_public = false
  allow_blob_public_access        = false

  tags = merge(var.tags, {
    Environment = var.environment
    Purpose     = "audit-log-archive"
  })
}

resource "azurerm_storage_container" "audit" {
  name                  = "audit"
  storage_account_name  = azurerm_storage_account.audit.name
  container_access_type = "private"
}

resource "azurerm_storage_container_immutability_policy" "audit" {
  storage_account_id = azurerm_storage_account.audit.id
  container_name     = azurerm_storage_container.audit.name
  immutability_period_since_creation_in_days = var.immutability_days
  protected_append_writes_enabled            = true
}

resource "azurerm_eventhub_namespace" "audit" {
  name                = "${local.base_name}-ehns"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"

  tags = merge(var.tags, {
    Environment = var.environment
    Purpose     = "audit-events"
  })
}

resource "azurerm_eventhub" "audit" {
  name                = "${local.base_name}-audit"
  namespace_name      = azurerm_eventhub_namespace.audit.name
  resource_group_name = var.resource_group_name
  message_retention   = 5
  partition_count     = 2
}

resource "azurerm_eventhub_authorization_rule" "translator" {
  name                = "translator"
  eventhub_name       = azurerm_eventhub.audit.name
  namespace_name      = azurerm_eventhub_namespace.audit.name
  resource_group_name = var.resource_group_name

  listen = false
  manage = false
  send   = true
}

resource "azurerm_key_vault" "audit" {
  name                       = "${local.base_name}-kv"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = ["Get", "Create", "Delete", "Purge", "Recover", "GetRotationPolicy", "SetRotationPolicy"]
  }

  tags = merge(var.tags, {
    Environment = var.environment
    Purpose     = "audit-key-vault"
  })
}

resource "azurerm_key_vault_key" "audit" {
  name         = "audit-signing"
  key_vault_id = azurerm_key_vault.audit.id
  key_type     = "RSA"
  key_size     = 3072

  rotation_policy {
    automatic {
      time_before_expiry = "P30D"
    }
    expire_after = "P365D"
  }
}

resource "azurerm_key_vault_access_policy" "translator" {
  key_vault_id = azurerm_key_vault.audit.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.translator_principal_id

  key_permissions = [
    "Get",
    "Sign",
    "Verify",
    "Decrypt",
    "Encrypt",
    "UnwrapKey",
    "WrapKey"
  ]
}

resource "azurerm_key_vault_access_policy" "manifest" {
  key_vault_id = azurerm_key_vault.audit.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.manifest_principal_id

  key_permissions = [
    "Get",
    "Sign",
    "Verify",
    "Decrypt",
    "Encrypt",
    "UnwrapKey",
    "WrapKey"
  ]
}

resource "azurerm_role_assignment" "translator_blob" {
  scope                = azurerm_storage_account.audit.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.translator_principal_id
}

resource "azurerm_role_assignment" "manifest_blob" {
  scope                = azurerm_storage_account.audit.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.manifest_principal_id
}

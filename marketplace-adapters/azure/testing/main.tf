provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "audit" {
  name     = "${var.name_prefix}-${var.environment}-rg"
  location = var.location

  tags = merge(var.tags, {
    Environment = var.environment
    Purpose     = "audit-integration"
  })
}

module "audit_pipeline" {
  source                = "../../modules/azure_audit_pipeline"
  resource_group_name   = azurerm_resource_group.audit.name
  location              = var.location
  name_prefix           = var.name_prefix
  environment           = var.environment
  translator_principal_id = var.translator_principal_id
  manifest_principal_id   = var.manifest_principal_id
  tags                  = var.tags
}

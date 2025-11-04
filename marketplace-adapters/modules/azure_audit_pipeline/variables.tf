variable "resource_group_name" {
  description = "Existing Azure resource group for audit resources."
  type        = string
}

variable "location" {
  description = "Azure region (e.g. eastus)."
  type        = string
}

variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "environment" {
  description = "Environment identifier."
  type        = string
}

variable "translator_principal_id" {
  description = "Azure AD object ID of the principal publishing audit events."
  type        = string
}

variable "manifest_principal_id" {
  description = "Azure AD object ID of the principal writing manifests."
  type        = string
}

variable "immutability_days" {
  description = "Immutable retention period (days)."
  type        = number
  default     = 2555
}

variable "tags" {
  description = "Tags applied to Azure resources."
  type        = map(string)
  default     = {}
}

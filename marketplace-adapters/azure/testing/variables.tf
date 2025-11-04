variable "location" {
  description = "Azure region (e.g. eastus)."
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Logical environment label."
  type        = string
  default     = "testing"
}

variable "name_prefix" {
  description = "Resource prefix."
  type        = string
  default     = "aegis"
}

variable "translator_principal_id" {
  description = "Azure AD object ID for the translator workload identity."
  type        = string
}

variable "manifest_principal_id" {
  description = "Azure AD object ID for the manifest signer workload identity."
  type        = string
}

variable "tags" {
  description = "Tags applied to Azure resources."
  type        = map(string)
  default = {
    Product = "aegis-iso20022"
  }
}

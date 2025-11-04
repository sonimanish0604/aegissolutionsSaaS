variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "location" {
  description = "Region for regional resources (e.g. us-east1)."
  type        = string
}

variable "name_prefix" {
  description = "Prefix used for resource naming."
  type        = string
}

variable "environment" {
  description = "Environment label (testing, staging, prod)."
  type        = string
}

variable "translator_service_account" {
  description = "Email of the service account publishing audit events."
  type        = string
}

variable "manifest_service_account" {
  description = "Email of the service account writing manifests."
  type        = string
}

variable "bucket_retention_days" {
  description = "Retention policy for objects (7 years by default)."
  type        = number
  default     = 2555
}

variable "coldline_transition_days" {
  description = "Days before objects move to Coldline storage."
  type        = number
  default     = 1095
}

variable "labels" {
  description = "Common labels applied to resources."
  type        = map(string)
  default     = {}
}

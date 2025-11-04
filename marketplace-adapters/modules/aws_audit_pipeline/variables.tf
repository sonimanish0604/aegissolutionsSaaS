variable "name_prefix" {
  description = "Prefix used for naming AWS resources."
  type        = string
}

variable "environment" {
  description = "Logical environment name (e.g. testing, staging, prod)."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the MSK cluster and supporting resources will run."
  type        = string
}

variable "subnet_ids" {
  description = "List of private subnet IDs used by MSK."
  type        = list(string)
}

variable "kms_deletion_window_in_days" {
  description = "Waiting period before the KMS key can be scheduled for deletion."
  type        = number
  default     = 30
}

variable "bucket_retention_days" {
  description = "Number of days before objects transition to Glacier Deep Archive."
  type        = number
  default     = 1095 # 3 years
}

variable "object_lock_retention_days" {
  description = "Compliance retention days for Object Lock."
  type        = number
  default     = 2555 # ~7 years
}

variable "translator_service_principal" {
  description = "ARN of the service principal (ECS task/role) that publishes audit events."
  type        = string
  default     = null
}

variable "manifest_service_principal" {
  description = "ARN of the service principal (Lambda/function) that writes manifests."
  type        = string
  default     = null
}

variable "tags" {
  description = "Common tags applied to resources."
  type        = map(string)
  default     = {}
}

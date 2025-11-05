variable "project_id" {
  description = "GCP project ID for the testing stack."
  type        = string
}

variable "region" {
  description = "Primary region (e.g. us-east1)."
  type        = string
  default     = "us-east1"
}

variable "environment" {
  description = "Logical environment label."
  type        = string
  default     = "testing"
}

variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
  default     = "aegis"
}

variable "network_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.70.0.0/16"
}

variable "labels" {
  description = "Labels applied to resources."
  type        = map(string)
  default = {
    product = "aegis-iso20022"
  }
}

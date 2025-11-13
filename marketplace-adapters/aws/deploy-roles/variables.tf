variable "aws_region" {
  description = "AWS region that hosts the IAM roles."
  type        = string
  default     = "us-east-1"
}

variable "github_repository" {
  description = "GitHub repository in <owner>/<repo> format authorised to deploy."
  type        = string
  default     = "AegisSolutions/SaaS-Core"

  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repository))
    error_message = "github_repository must be expressed as <owner>/<repo>."
  }
}

variable "testing_branch" {
  description = "Branch that maps to the testing environment."
  type        = string
  default     = "testing"
}

variable "staging_branch" {
  description = "Branch that maps to the staging environment."
  type        = string
  default     = "staging"
}

variable "production_branch" {
  description = "Branch that maps to the production environment."
  type        = string
  default     = "main"
}

variable "managed_policy_arns" {
  description = "Managed policies that will be attached to every deploy role."
  type        = list(string)
  default     = []
}

variable "resource_prefix" {
  description = "Base prefix shared by environment resources (matches name_prefix in env stacks)."
  type        = string
  default     = "aegis"
}

variable "max_session_duration" {
  description = "Maximum session duration (seconds) for the deploy roles."
  type        = number
  default     = 3600
}

variable "tags" {
  description = "Base tags applied to the deploy roles."
  type        = map(string)
  default = {
    "Product" = "aegis-iso20022"
  }
}

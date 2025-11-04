variable "role_name" {
  description = "Name of the IAM role to create."
  type        = string
}

variable "description" {
  description = "IAM role description."
  type        = string
  default     = "GitHub Actions deployment role"
}

variable "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider."
  type        = string
}

variable "github_repository" {
  description = "Repository in <owner>/<repo> format."
  type        = string
}

variable "branch" {
  description = "Branch name (without refs/heads/) authorised to assume the role."
  type        = string
}

variable "audience" {
  description = "Expected OIDC audience claim."
  type        = string
  default     = "sts.amazonaws.com"
}

variable "managed_policy_arns" {
  description = "AWS managed policy ARNs to attach to the role."
  type        = list(string)
  default     = []
}

variable "inline_policies" {
  description = "Map of inline policy name to JSON document."
  type        = map(string)
  default     = {}
}

variable "max_session_duration" {
  description = "Maximum session duration in seconds for role assumptions."
  type        = number
  default     = 3600
}

variable "tags" {
  description = "Additional tags to apply to the IAM role."
  type        = map(string)
  default     = {}
}

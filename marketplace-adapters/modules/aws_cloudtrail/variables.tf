variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "environment" {
  description = "Environment label (testing|staging|production)."
  type        = string
}

variable "retention_days" {
  description = "Number of days to retain CloudTrail logs in S3."
  type        = number
  default     = 365
}

variable "include_data_events" {
  description = "Whether to capture S3/Lambda data events."
  type        = bool
  default     = true
}

variable "enable_insights" {
  description = "Enable CloudTrail Insights (API call rate/error rate)."
  type        = bool
  default     = true
}

variable "audit_reader_principals" {
  description = "List of AWS principal ARNs allowed to assume the audit reader role."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}

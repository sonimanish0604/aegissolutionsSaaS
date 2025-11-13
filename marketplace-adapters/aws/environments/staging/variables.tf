variable "aws_region" {
  description = "AWS region to deploy the staging audit stack."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Logical environment name."
  type        = string
  default     = "staging"
}

variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
  default     = "aegis-iso20022"
}

variable "vpc_cidr" {
  description = "CIDR for the staging VPC."
  type        = string
  default     = "10.70.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use for the staging VPC."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnet egress."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common AWS tags."
  type        = map(string)
  default = {
    "Product"     = "aegis-iso20022"
    "Environment" = "staging"
  }
}

variable "cloudtrail_retention_days" {
  description = "Number of days to retain CloudTrail logs for staging."
  type        = number
  default     = 365
}

variable "cloudtrail_include_data_events" {
  description = "Capture S3/Lambda data events in CloudTrail."
  type        = bool
  default     = true
}

variable "cloudtrail_enable_insights" {
  description = "Enable CloudTrail Insights."
  type        = bool
  default     = true
}

variable "cloudtrail_audit_reader_principals" {
  description = "Additional principals allowed to assume the CloudTrail reader role."
  type        = list(string)
  default     = []
}

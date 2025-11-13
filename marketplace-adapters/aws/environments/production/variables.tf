variable "aws_region" {
  description = "AWS region to deploy the production audit stack."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Logical environment name."
  type        = string
  default     = "production"
}

variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
  default     = "aegis"
}

variable "vpc_cidr" {
  description = "CIDR for the production VPC."
  type        = string
  default     = "10.80.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use for the production VPC."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
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
    "Environment" = "production"
  }
}

variable "cloudtrail_retention_days" {
  description = "Number of days to retain CloudTrail logs for production."
  type        = number
  default     = 1825
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

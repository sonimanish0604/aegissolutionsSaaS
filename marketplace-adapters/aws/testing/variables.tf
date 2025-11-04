variable "aws_region" {
  description = "AWS region to deploy the testing audit stack."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Logical environment name."
  type        = string
  default     = "testing"
}

variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
  default     = "aegis"
}

variable "vpc_cidr" {
  description = "CIDR for the testing VPC."
  type        = string
  default     = "10.60.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use for the test VPC."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnet egress."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common AWS tags."
  type        = map(string)
  default = {
    "Product" = "aegis-iso20022"
  }
}

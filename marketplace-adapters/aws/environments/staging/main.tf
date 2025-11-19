provider "aws" {
  region = var.aws_region
}

locals {
  azs             = var.availability_zones
  private_subnets = [for idx in range(length(local.azs)) : cidrsubnet(var.vpc_cidr, 8, idx)]
  public_subnets  = [for idx in range(length(local.azs)) : cidrsubnet(var.vpc_cidr, 8, idx + 16)]
}

module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "${var.name_prefix}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs             = local.azs
  private_subnets = local.private_subnets
  public_subnets  = local.public_subnets

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = true
  enable_vpn_gateway     = false
  create_igw             = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = merge(var.tags, {
    "Environment" = var.environment
    "Name"        = "${var.name_prefix}-${var.environment}-vpc"
  })
}

data "aws_iam_policy_document" "translator_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "translator" {
  name               = "${var.name_prefix}-${var.environment}-translator"
  assume_role_policy = data.aws_iam_policy_document.translator_assume.json
  tags               = merge(var.tags, { "Environment" = var.environment })
}

data "aws_iam_policy_document" "manifest_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "manifest" {
  name               = "${var.name_prefix}-${var.environment}-manifest"
  assume_role_policy = data.aws_iam_policy_document.manifest_assume.json
  tags               = merge(var.tags, { "Environment" = var.environment })
}

module "audit_pipeline" {
  source      = "../../../modules/aws_audit_pipeline"
  name_prefix = var.name_prefix
  environment = var.environment
  vpc_id      = module.network.vpc_id
  subnet_ids  = module.network.private_subnets

  translator_service_principal = aws_iam_role.translator.arn
  manifest_service_principal   = aws_iam_role.manifest.arn

  tags = var.tags
}

data "aws_iam_policy_document" "translator_access" {
  statement {
    effect = "Allow"
    actions = [
      "kafka-cluster:Connect",
      "kafka-cluster:AlterCluster",
      "kafka-cluster:DescribeCluster",
      "kafka:DescribeCluster",
      "kafka:GetBootstrapBrokers",
      "kafka:DescribeTopic",
      "kafka-cluster:DescribeTopic",
      "kafka-cluster:WriteData",
      "kafka-cluster:AlterTopic"
    ]
    resources = [module.audit_pipeline.msk_cluster_arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      module.audit_pipeline.bucket_arn,
      "${module.audit_pipeline.bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:GenerateDataKey*",
      "kms:Sign"
    ]
    resources = [module.audit_pipeline.kms_key_arn]
  }
}

resource "aws_iam_policy" "translator" {
  name   = "${var.name_prefix}-${var.environment}-translator"
  policy = data.aws_iam_policy_document.translator_access.json
}

resource "aws_iam_role_policy_attachment" "translator" {
  role       = aws_iam_role.translator.name
  policy_arn = aws_iam_policy.translator.arn
}

data "aws_iam_policy_document" "manifest_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      module.audit_pipeline.bucket_arn,
      "${module.audit_pipeline.bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:GenerateDataKey*",
      "kms:Sign",
      "kms:Verify"
    ]
    resources = [module.audit_pipeline.kms_key_arn]
  }
}

resource "aws_iam_policy" "manifest" {
  name   = "${var.name_prefix}-${var.environment}-manifest"
  policy = data.aws_iam_policy_document.manifest_access.json
}

resource "aws_iam_role_policy_attachment" "manifest" {
  role       = aws_iam_role.manifest.name
  policy_arn = aws_iam_policy.manifest.arn
}

module "cloudtrail" {
  source = "../../../modules/aws_cloudtrail"

  name_prefix             = var.name_prefix
  aws_region              = var.aws_region
  environment             = var.environment
  retention_days          = var.cloudtrail_retention_days
  include_data_events     = var.cloudtrail_include_data_events
  enable_insights         = var.cloudtrail_enable_insights
  audit_reader_principals = var.cloudtrail_audit_reader_principals
  tags                    = var.tags
}

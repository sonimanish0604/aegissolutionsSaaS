provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = merge(var.tags, { "Name" = "github-actions" })
}

locals {
  deploy_roles = {
    testing = {
      role_name   = "AegisTestingDeploy"
      branch      = var.testing_branch
      description = "GitHub Actions deploy role for the testing environment"
      tags        = merge(var.tags, { "Environment" = "testing" })
    }
    staging = {
      role_name   = "AegisStagingDeploy"
      branch      = var.staging_branch
      description = "GitHub Actions deploy role for the staging environment"
      tags        = merge(var.tags, { "Environment" = "staging" })
    }
    production = {
      role_name   = "AegisProductionDeploy"
      branch      = var.production_branch
      description = "GitHub Actions deploy role for the production environment"
      tags        = merge(var.tags, { "Environment" = "production" })
    }
  }

  ec2_actions = [
    "ec2:AllocateAddress",
    "ec2:AssociateRouteTable",
    "ec2:AssociateVpcCidrBlock",
    "ec2:AttachInternetGateway",
    "ec2:CreateInternetGateway",
    "ec2:CreateNatGateway",
    "ec2:CreateRoute",
    "ec2:CreateRouteTable",
    "ec2:CreateSecurityGroup",
    "ec2:CreateSubnet",
    "ec2:CreateTags",
    "ec2:CreateVpc",
    "ec2:DeleteInternetGateway",
    "ec2:DeleteNatGateway",
    "ec2:DeleteRoute",
    "ec2:DeleteRouteTable",
    "ec2:DeleteSecurityGroup",
    "ec2:DeleteSubnet",
    "ec2:DeleteTags",
    "ec2:DeleteVpc",
    "ec2:DescribeAccountAttributes",
    "ec2:DescribeAvailabilityZones",
    "ec2:DescribeInternetGateways",
    "ec2:DescribeNatGateways",
    "ec2:DescribeRouteTables",
    "ec2:DescribeSecurityGroups",
    "ec2:DescribeSubnets",
    "ec2:DescribeTags",
    "ec2:DescribeVpcs",
    "ec2:DetachInternetGateway",
    "ec2:DisassociateRouteTable",
    "ec2:ModifyVpcAttribute",
    "ec2:ReleaseAddress",
    "ec2:ReplaceRoute",
    "ec2:RevokeSecurityGroupEgress",
    "ec2:RevokeSecurityGroupIngress",
    "ec2:AuthorizeSecurityGroupEgress",
    "ec2:AuthorizeSecurityGroupIngress"
  ]

  s3_actions = [
    "s3:CreateBucket",
    "s3:DeleteBucket",
    "s3:DeleteObject",
    "s3:GetAccelerateConfiguration",
    "s3:GetBucketAcl",
    "s3:GetBucketEncryption",
    "s3:GetBucketLifecycleConfiguration",
    "s3:GetBucketLocation",
    "s3:GetBucketPolicy",
    "s3:GetBucketPublicAccessBlock",
    "s3:GetBucketTagging",
    "s3:GetBucketVersioning",
    "s3:GetObject",
    "s3:ListBucket",
    "s3:PutBucketAcl",
    "s3:PutBucketEncryption",
    "s3:PutBucketLifecycleConfiguration",
    "s3:PutBucketPolicy",
    "s3:PutBucketPublicAccessBlock",
    "s3:PutBucketTagging",
    "s3:PutBucketVersioning",
    "s3:PutObject"
  ]

  iam_role_scope = {
    for env in keys(local.deploy_roles) :
    env => "arn:aws:iam::*:role/${var.resource_prefix}-${env}-*"
  }

  s3_bucket_arns = {
    for env in keys(local.deploy_roles) :
    env => [
      "arn:aws:s3:::${var.resource_prefix}-${env}-audit-*",
      "arn:aws:s3:::${var.resource_prefix}-${env}-audit-*/*",
      "arn:aws:s3:::${var.resource_prefix}-${env}-trail-*",
      "arn:aws:s3:::${var.resource_prefix}-${env}-trail-*/*"
    ]
  }

  kms_arns = {
    for env in keys(local.deploy_roles) :
    env => [
      "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key/*",
      "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/${var.resource_prefix}-${env}-*"
    ]
  }

  logs_arn = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/${var.resource_prefix}/audit/*"

  cloudtrail_arns = {
    for env in keys(local.deploy_roles) :
    env => "arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/${var.resource_prefix}-${env}-trail"
  }
}

data "aws_iam_policy_document" "deploy_permissions" {
  for_each = local.deploy_roles

  statement {
    sid     = "EC2Networking"
    actions = local.ec2_actions
    resources = ["*"]
  }

  statement {
    sid       = "S3AuditBuckets"
    actions   = local.s3_actions
    resources = local.s3_bucket_arns[each.key]
  }

  statement {
    sid = "IAMRoleLifecycle"
    actions = [
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:CreateServiceLinkedRole",
      "iam:UpdateRole",
      "iam:UpdateAssumeRolePolicy"
    ]
    resources = ["*"]
  }

  statement {
    sid = "IAMRoleManagement"
    actions = [
      "iam:GetRole",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PassRole"
    ]
    resources = [local.iam_role_scope[each.key]]
  }

  statement {
    sid = "KMSManagement"
    actions = [
      "kms:CreateKey",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:DescribeKey",
      "kms:EnableKey",
      "kms:DisableKey",
      "kms:CreateAlias",
      "kms:UpdateAlias",
      "kms:DeleteAlias",
      "kms:ListAliases",
      "kms:PutKeyPolicy",
      "kms:GetKeyPolicy",
      "kms:GenerateDataKey",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:CreateGrant",
      "kms:RetireGrant",
      "kms:ListGrants"
    ]
    resources = local.kms_arns[each.key]
  }

  statement {
    sid = "CloudWatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:DescribeLogGroups",
      "logs:PutRetentionPolicy",
      "logs:DeleteRetentionPolicy",
      "logs:TagLogGroup",
      "logs:UntagLogGroup"
    ]
    resources = [local.logs_arn]
  }

  statement {
    sid = "CloudTrailManagement"
    actions = [
      "cloudtrail:CreateTrail",
      "cloudtrail:UpdateTrail",
      "cloudtrail:DeleteTrail",
      "cloudtrail:StartLogging",
      "cloudtrail:StopLogging",
      "cloudtrail:GetTrailStatus",
      "cloudtrail:PutEventSelectors",
      "cloudtrail:AddTags",
      "cloudtrail:RemoveTags"
    ]
    resources = [local.cloudtrail_arns[each.key]]
  }

  statement {
    sid = "KafkaServerless"
    actions = [
      "kafka:CreateCluster",
      "kafka:DeleteCluster",
      "kafka:DescribeCluster",
      "kafka:ListClusters",
      "kafka:CreateConfiguration",
      "kafka:DeleteConfiguration",
      "kafka:UpdateConfiguration",
      "kafka:DescribeConfiguration",
      "kafka:DescribeConfigurationRevision",
      "kafka:GetBootstrapBrokers",
      "kafka:ListNodes",
      "kafka:TagResource",
      "kafka:UntagResource"
    ]
    resources = ["*"]
  }
}

module "deploy_roles" {
  source = "../../modules/aws_github_actions_role"

  for_each = local.deploy_roles

  role_name            = each.value.role_name
  description          = each.value.description
  oidc_provider_arn    = aws_iam_openid_connect_provider.github.arn
  github_repository    = var.github_repository
  branch               = each.value.branch
  managed_policy_arns  = var.managed_policy_arns
  inline_policies      = { "environment-access" = data.aws_iam_policy_document.deploy_permissions[each.key].json }
  max_session_duration = var.max_session_duration
  tags                 = each.value.tags
}

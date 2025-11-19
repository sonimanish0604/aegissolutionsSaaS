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
      branch      = var.testing_branch
      description = "GitHub Actions deploy role for the testing environment"
      tags        = merge(var.tags, { "Environment" = "testing" })
    }
    staging = {
      branch      = var.staging_branch
      description = "GitHub Actions deploy role for the staging environment"
      tags        = merge(var.tags, { "Environment" = "staging" })
    }
    production = {
      branch      = var.production_branch
      description = "GitHub Actions deploy role for the production environment"
      tags        = merge(var.tags, { "Environment" = "production" })
    }
  }

  github_subject_prefix = "repo:${var.github_repository}"

  connectivity_roles = {
    testing = {
      branch = var.testing_branch
      oidc_subjects = distinct(compact([
        "${local.github_subject_prefix}:ref:refs/heads/${var.testing_branch}",
        "${local.github_subject_prefix}:pull_request",
        "${local.github_subject_prefix}:pull_request:*",
        var.develop_branch != "" ? "${local.github_subject_prefix}:ref:refs/heads/${var.develop_branch}" : null
      ]))
      tags = merge(var.tags, { "Environment" = "testing", "Purpose" = "connectivity-check" })
    }
    staging = {
      branch = var.staging_branch
      oidc_subjects = [
        "${local.github_subject_prefix}:ref:refs/heads/${var.staging_branch}"
      ]
      tags = merge(var.tags, { "Environment" = "staging", "Purpose" = "connectivity-check" })
    }
    production = {
      branch = var.production_branch
      oidc_subjects = [
        "${local.github_subject_prefix}:ref:refs/heads/${var.production_branch}"
      ]
      tags = merge(var.tags, { "Environment" = "production", "Purpose" = "connectivity-check" })
    }
  }

  pr_validation_role = {
    branch = var.develop_branch
    oidc_subjects = distinct(compact([
      "${local.github_subject_prefix}:ref:refs/heads/${var.develop_branch}",
      "${local.github_subject_prefix}:pull_request",
      "${local.github_subject_prefix}:pull_request:*"
    ]))
    tags = merge(var.tags, { "Environment" = "neutral-pr", "Purpose" = "pr-connectivity-check" })
  }

  ec2_actions = [
    "ec2:AllocateAddress",
    "ec2:DescribeVpcAttribute",
    "ec2:AssociateRouteTable",
    "ec2:AssociateVpcCidrBlock",
    "ec2:AttachInternetGateway",
    "ec2:DescribeSecurityGroupRules",
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

  s3_bucket_actions = [
    "s3:DeleteBucket",
    "s3:DeleteObject",
    "s3:GetAccelerateConfiguration",
    "s3:GetBucketAcl",
    "s3:GetBucketLogging",
    "s3:GetBucketRequestPayment",
    "s3:GetBucketWebsite",
    "s3:GetBucketCORS",
    "s3:GetBucketEncryption",
    "s3:GetBucketLifecycleConfiguration",
    "s3:GetBucketLocation",
    "s3:GetBucketPolicy",
    "s3:GetBucketPublicAccessBlock",
    "s3:GetBucketTagging",
    "s3:GetBucketVersioning",
    "s3:GetReplicationConfiguration",
    "s3:GetLifecycleConfiguration",
    "s3:GetObject",
    "s3:ListBucket",
    "s3:PutBucketAcl",
    "s3:PutBucketRequestPayment",
    "s3:PutBucketLogging",
    "s3:PutBucketCORS",
    "s3:PutBucketEncryption",
    "s3:PutBucketLifecycleConfiguration",
    "s3:PutBucketPolicy",
    "s3:PutBucketObjectLockConfiguration",
    "s3:PutBucketPublicAccessBlock",
    "s3:PutBucketTagging",
    "s3:PutBucketVersioning",
    "s3:PutObject"
  ]

  s3_global_actions = [
    "s3:CreateBucket",
    "s3:ListAllMyBuckets"
  ]

  iam_role_scope = {
    for env in keys(local.deploy_roles) :
    env => "arn:aws:iam::*:role/${var.resource_prefix}-${env}-*"
  }

  iam_policy_scope = {
    for env in keys(local.deploy_roles) :
    env => "arn:aws:iam::*:policy/${var.resource_prefix}-${env}-*"
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
    sid       = "EC2Networking"
    actions   = local.ec2_actions
    resources = ["*"]
  }

  statement {
    sid       = "S3Create"
    actions   = local.s3_global_actions
    resources = ["*"]
  }

  statement {
    sid       = "S3AuditBuckets"
    actions   = local.s3_bucket_actions
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
      "iam:PassRole",
      "iam:ListAttachedRolePolicies",
      "iam:ListRolePolicies"
    ]
    resources = [local.iam_role_scope[each.key]]
  }

  statement {
    sid = "IAMPolicyLifecycle"
    actions = [
      "iam:CreatePolicy",
      "iam:DeletePolicy",
      "iam:CreatePolicyVersion",
      "iam:DeletePolicyVersion",
      "iam:SetDefaultPolicyVersion"
    ]
    resources = [local.iam_policy_scope[each.key]]
  }

  statement {
    sid = "IAMPolicyInsights"
    actions = [
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:ListPolicyVersions",
      "iam:TagPolicy",
      "iam:UntagPolicy"
    ]
    resources = [local.iam_policy_scope[each.key]]
  }

  statement {
    sid = "KMSManagement"
    actions = [
      "kms:GetKeyRotationStatus",
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
    sid       = "KMSCreateKey"
    actions   = ["kms:CreateKey"]
    resources = ["*"]
  }

  statement {
    sid = "KMSList"
    actions = [
      "kms:ListAliases",
      "kms:ListKeys"
    ]
    resources = ["*"]
  }

  statement {
    sid = "CloudWatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:ListTagsForResource",
      "logs:DescribeLogGroups",
      "logs:PutRetentionPolicy",
      "logs:DeleteRetentionPolicy",
      "logs:TagLogGroup",
      "logs:UntagLogGroup"
    ]
    resources = ["*"]
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
      "kafka:CreateClusterV2",
      "kafka:DescribeClusterV2",
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

data "aws_iam_policy_document" "connectivity_permissions" {
  for_each = local.connectivity_roles

  statement {
    sid       = "AllowCallerIdentity"
    actions   = ["sts:GetCallerIdentity"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "pr_connectivity_permissions" {
  statement {
    sid       = "AllowCallerIdentity"
    actions   = ["sts:GetCallerIdentity"]
    resources = ["*"]
  }
}

module "deploy_roles" {
  source = "../../modules/aws_github_actions_role"

  for_each = local.deploy_roles

  role_name            = "${var.resource_prefix}-${each.key}-deploy"
  description          = each.value.description
  oidc_provider_arn    = aws_iam_openid_connect_provider.github.arn
  github_repository    = var.github_repository
  branch               = each.value.branch
  oidc_subjects        = var.github_oidc_subjects
  managed_policy_arns  = var.managed_policy_arns
  inline_policies      = { "environment-access" = data.aws_iam_policy_document.deploy_permissions[each.key].json }
  max_session_duration = var.max_session_duration
  tags                 = each.value.tags
}

module "connectivity_roles" {
  source = "../../modules/aws_github_actions_role"

  for_each = local.connectivity_roles

  role_name            = "${var.resource_prefix}-${each.key}-connectivity"
  description          = "GitHub Actions connectivity role for the ${each.key} environment"
  oidc_provider_arn    = aws_iam_openid_connect_provider.github.arn
  github_repository    = var.github_repository
  branch               = each.value.branch
  oidc_subjects        = each.value.oidc_subjects
  inline_policies      = { "connectivity-access" = data.aws_iam_policy_document.connectivity_permissions[each.key].json }
  max_session_duration = var.max_session_duration
  tags                 = each.value.tags
}

module "pr_connectivity_role" {
  source = "../../modules/aws_github_actions_role"

  role_name            = "${var.resource_prefix}-pr-connectivity"
  description          = "Neutral GitHub Actions connectivity role for PR validation"
  oidc_provider_arn    = aws_iam_openid_connect_provider.github.arn
  github_repository    = var.github_repository
  branch               = local.pr_validation_role.branch
  oidc_subjects        = local.pr_validation_role.oidc_subjects
  inline_policies      = { "pr-connectivity-access" = data.aws_iam_policy_document.pr_connectivity_permissions.json }
  max_session_duration = var.max_session_duration
  tags                 = local.pr_validation_role.tags
}

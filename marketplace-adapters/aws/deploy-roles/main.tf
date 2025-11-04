provider "aws" {
  region = var.aws_region
}

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
}

module "deploy_roles" {
  source = "../../modules/aws_github_actions_role"

  for_each = local.deploy_roles

  role_name           = each.value.role_name
  description         = each.value.description
  oidc_provider_arn   = aws_iam_openid_connect_provider.github.arn
  github_repository   = var.github_repository
  branch              = each.value.branch
  managed_policy_arns = var.managed_policy_arns
  max_session_duration = var.max_session_duration
  tags                = each.value.tags
}

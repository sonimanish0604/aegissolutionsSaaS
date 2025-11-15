data "aws_partition" "current" {}

data "aws_caller_identity" "current" {}

locals {
  default_oidc_condition_subs = [
    "repo:${var.github_repository}:ref:refs/heads/${var.branch}",
    "repo:${var.github_repository}:pull_request:*"
  ]

  oidc_condition_subs = length(var.oidc_subjects) > 0 ? var.oidc_subjects : local.default_oidc_condition_subs
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    sid     = "GithubActionsOIDC"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = [var.audience]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.oidc_condition_subs
    }
  }
}

resource "aws_iam_role" "this" {
  name                 = var.role_name
  description          = var.description
  assume_role_policy   = data.aws_iam_policy_document.assume_role.json
  max_session_duration = var.max_session_duration

  tags = merge(
    {
      "ManagedBy" = "terraform"
      "AccountId" = data.aws_caller_identity.current.account_id
      "Partition" = data.aws_partition.current.partition
    },
    var.tags,
  )
}

resource "aws_iam_role_policy_attachment" "managed" {
  for_each = toset(var.managed_policy_arns)

  role       = aws_iam_role.this.name
  policy_arn = each.value
}

resource "aws_iam_role_policy" "inline" {
  for_each = var.inline_policies

  name   = each.key
  role   = aws_iam_role.this.id
  policy = each.value
}

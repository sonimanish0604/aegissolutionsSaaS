locals {
  base_name = lower("${var.name_prefix}-${var.environment}")
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_kms_key" "audit" {
  description             = "KMS key for ${var.environment} audit artifacts"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.kms.json
  tags                    = merge(var.tags, { "Name" = "${local.base_name}-audit-kms" })
}

resource "aws_kms_alias" "audit" {
  name          = "alias/${local.base_name}-audit-${random_id.suffix.hex}"
  target_key_id = aws_kms_key.audit.key_id
}

data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "kms" {
  statement {
    sid    = "EnableRootAccount"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.arn]
    }

    actions   = ["kms:*"]
    resources = ["*"]
  }

  dynamic "statement" {
    for_each = compact([var.translator_service_principal])
    content {
      sid    = "AllowTranslatorUse"
      effect = "Allow"
      principals {
        type        = "AWS"
        identifiers = [statement.value]
      }
      actions = [
        "kms:DescribeKey",
        "kms:GenerateDataKey",
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:ReEncrypt*",
        "kms:Sign"
      ]
      resources = ["*"]
    }
  }

  dynamic "statement" {
    for_each = compact([var.manifest_service_principal])
    content {
      sid    = "AllowManifestUse"
      effect = "Allow"
      principals {
        type        = "AWS"
        identifiers = [statement.value]
      }
      actions = [
        "kms:DescribeKey",
        "kms:GenerateDataKey",
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:ReEncrypt*",
        "kms:Sign",
        "kms:Verify"
      ]
      resources = ["*"]
    }
  }
}

resource "aws_s3_bucket" "audit" {
  bucket              = "${local.base_name}-audit-${random_id.suffix.hex}"
  object_lock_enabled = true

  tags = merge(
    var.tags,
    {
      "Name"        = "${local.base_name}-audit"
      "Environment" = var.environment
      "Purpose"     = "audit-log-archive"
    }
  )
}

resource "aws_s3_bucket_versioning" "audit" {
  bucket = aws_s3_bucket.audit.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.audit.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket                  = aws_s3_bucket.audit.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    id     = "TransitionToDeepArchive"
    status = "Enabled"
    filter {
      prefix = ""
    }
    transition {
      days          = var.bucket_retention_days
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

resource "aws_s3_bucket_object_lock_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    default_retention {
      mode  = "COMPLIANCE"
      days  = var.object_lock_retention_days
    }
  }
}

resource "aws_security_group" "msk" {
  name        = "${local.base_name}-msk"
  description = "Security group for MSK serverless"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = []
    self            = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { "Name" = "${local.base_name}-msk-sg" })
}

resource "aws_msk_serverless_cluster" "audit" {
  cluster_name = "${local.base_name}-audit"
  client_authentication {
    sasl {
      iam {
        enabled = true
      }
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.msk.id]
  }

  tags = merge(
    var.tags,
    {
      "Name"        = "${local.base_name}-audit-msk"
      "Environment" = var.environment
    }
  )
}

resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aegis/audit/msk/${var.environment}"
  retention_in_days = 14
  tags              = merge(var.tags, { "Name" = "${local.base_name}-msk-logs" })
}

resource "aws_msk_configuration" "audit" {
  name              = "${local.base_name}-audit-config"
  kafka_versions    = ["3.8.x"]
  server_properties = <<-EOF
auto.create.topics.enable = true
delete.topic.enable = true
EOF
}

resource "aws_msk_cluster_policy" "audit" {
  cluster_arn = aws_msk_serverless_cluster.audit.arn
  policy      = data.aws_iam_policy_document.msk_policy.json
}

data "aws_iam_policy_document" "msk_policy" {
  statement {
    sid    = "AllowTranslatorAccess"
    effect = "Allow"
    actions = [
      "kafka:GetBootstrapBrokers"
    ]
    resources = [aws_msk_serverless_cluster.audit.arn]
    principals {
      type        = "AWS"
      identifiers = compact([var.translator_service_principal])
    }
  }

  statement {
    sid    = "AllowManifestAccess"
    effect = "Allow"
    actions = [
      "kafka:GetBootstrapBrokers"
    ]
    resources = [aws_msk_serverless_cluster.audit.arn]
    principals {
      type        = "AWS"
      identifiers = compact([var.manifest_service_principal])
    }
  }
}

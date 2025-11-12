locals {
  base_name     = "${var.name_prefix}-${var.environment}-trail"
  audit_readers = length(var.audit_reader_principals) > 0 ? var.audit_reader_principals : ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
}

data "aws_caller_identity" "current" {}

resource "random_id" "bucket" {
  byte_length = 3
}

resource "aws_kms_key" "this" {
  description             = "KMS key for ${var.environment} CloudTrail log encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Sid       : "AllowRootAccount",
        Effect    : "Allow",
        Principal : { AWS : data.aws_caller_identity.current.arn },
        Action    : "kms:*",
        Resource  : "*"
      },
      {
        Sid      : "Allow CloudTrail",
        Effect   : "Allow",
        Principal: { Service : "cloudtrail.amazonaws.com" },
        Action   : [
          "kms:GenerateDataKey*",
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:DescribeKey"
        ],
        Resource : "*",
        Condition: {
          StringEquals : {
            "kms:EncryptionContext:aws:cloudtrail:arn" : "arn:aws:cloudtrail:${data.aws_caller_identity.current.account_id}:trail/${local.base_name}"
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    "Name"        = "${local.base_name}-kms"
    "Environment" = var.environment
  })
}

resource "aws_kms_alias" "this" {
  name          = "alias/${local.base_name}"
  target_key_id = aws_kms_key.this.key_id
}

resource "aws_s3_bucket" "logs" {
  bucket = "${local.base_name}-${random_id.bucket.hex}"

  tags = merge(var.tags, {
    "Name"        = "${local.base_name}-bucket"
    "Environment" = var.environment
  })
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.this.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "RetainAndExpire"
    status = "Enabled"

    expiration {
      days = var.retention_days
    }
  }
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    sid    = "AWSCloudTrailAclCheck"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.logs.arn]
  }

  statement {
    sid    = "AWSCloudTrailWrite"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}

data "aws_iam_policy_document" "reader_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = local.audit_readers
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "audit_reader" {
  name               = "${local.base_name}-reader"
  assume_role_policy = data.aws_iam_policy_document.reader_assume.json

  tags = merge(var.tags, {
    "Name"        = "${local.base_name}-reader"
    "Environment" = var.environment
  })
}

resource "aws_iam_role_policy" "audit_reader" {
  name = "${local.base_name}-reader-policy"
  role = aws_iam_role.audit_reader.id

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : ["s3:GetObject", "s3:ListBucket"],
        Resource : [
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      },
      {
        Effect   : "Allow",
        Action   : ["kms:Decrypt", "kms:DescribeKey"],
        Resource : aws_kms_key.this.arn
      }
    ]
  })
}

resource "aws_cloudtrail" "this" {
  name                          = local.base_name
  s3_bucket_name                = aws_s3_bucket.logs.id
  kms_key_id                    = aws_kms_key.this.arn
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  is_organization_trail         = false

  cloud_watch_logs_group_arn  = null
  cloud_watch_logs_role_arn   = null

  event_selector {
    include_management_events = true
    read_write_type          = "All"
  }

  dynamic "advanced_event_selector" {
    for_each = var.include_data_events ? ["s3", "lambda"] : []
    content {
      name = advanced_event_selector.value == "s3" ? "S3DataEvents" : "LambdaDataEvents"
      field_selector {
        field  = "eventCategory"
        equals = ["Data"]
      }
      field_selector {
        field  = "resources.type"
        equals = [advanced_event_selector.value == "s3" ? "AWS::S3::Object" : "AWS::Lambda::Function"]
      }
    }
  }

  dynamic "insight_selector" {
    for_each = var.enable_insights ? ["ApiCallRateInsight", "ApiErrorRateInsight"] : []
    content {
      insight_type = insight_selector.value
    }
  }

  depends_on = [aws_s3_bucket_policy.logs]

  tags = merge(var.tags, {
    "Name"        = "${local.base_name}"
    "Environment" = var.environment
  })
}

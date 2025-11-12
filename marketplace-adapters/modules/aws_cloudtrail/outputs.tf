output "trail_arn" {
  description = "CloudTrail ARN."
  value       = aws_cloudtrail.this.arn
}

output "log_bucket_name" {
  description = "S3 bucket storing CloudTrail logs."
  value       = aws_s3_bucket.logs.id
}

output "kms_key_arn" {
  description = "KMS key used to encrypt CloudTrail logs."
  value       = aws_kms_key.this.arn
}

output "audit_reader_role_arn" {
  description = "ARN of the audit reader IAM role."
  value       = aws_iam_role.audit_reader.arn
}

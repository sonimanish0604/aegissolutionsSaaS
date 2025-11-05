output "bucket_name" {
  value       = aws_s3_bucket.audit.bucket
  description = "Name of the S3 bucket storing immutable audit artifacts."
}

output "bucket_arn" {
  value       = aws_s3_bucket.audit.arn
  description = "ARN of the S3 bucket storing audit artifacts."
}

output "kms_key_arn" {
  value       = aws_kms_key.audit.arn
  description = "ARN of the audit KMS key."
}

output "kms_alias" {
  value       = aws_kms_alias.audit.name
  description = "Alias associated with the audit KMS key."
}

output "msk_cluster_arn" {
  value       = aws_msk_serverless_cluster.audit.arn
  description = "ARN of the MSK serverless cluster."
}

output "msk_security_group_id" {
  value       = aws_security_group.msk.id
  description = "Security group controlling MSK access."
}

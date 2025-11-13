output "audit_bucket_name" {
  description = "Audit archive S3 bucket name."
  value       = module.audit_pipeline.bucket_name
}

output "audit_kms_key_arn" {
  description = "KMS key securing audit artifacts."
  value       = module.audit_pipeline.kms_key_arn
}

output "msk_cluster_arn" {
  description = "MSK serverless cluster ARN."
  value       = module.audit_pipeline.msk_cluster_arn
}

output "translator_role_arn" {
  description = "IAM role for translator service."
  value       = aws_iam_role.translator.arn
}

output "manifest_role_arn" {
  description = "IAM role for manifest writer."
  value       = aws_iam_role.manifest.arn
}

output "cloudtrail_trail_arn" {
  description = "CloudTrail ARN for this environment."
  value       = module.cloudtrail.trail_arn
}

output "cloudtrail_bucket_name" {
  description = "S3 bucket storing CloudTrail logs."
  value       = module.cloudtrail.log_bucket_name
}

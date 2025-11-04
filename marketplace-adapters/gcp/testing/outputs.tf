output "pubsub_topic" {
  value       = module.audit_pipeline.pubsub_topic
  description = "Audit Pub/Sub topic."
}

output "audit_bucket" {
  value       = module.audit_pipeline.bucket_name
  description = "GCS bucket storing immutable audit artifacts."
}

output "kms_crypto_key" {
  value       = module.audit_pipeline.kms_key_id
  description = "KMS crypto key for encrypting audit data."
}

output "translator_service_account" {
  value       = google_service_account.translator.email
  description = "Service account email for the translator workload."
}

output "manifest_service_account" {
  value       = google_service_account.manifest.email
  description = "Service account email for manifest verification workload."
}

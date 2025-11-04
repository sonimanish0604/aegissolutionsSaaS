output "bucket_name" {
  description = "GCS bucket holding immutable audit artifacts."
  value       = google_storage_bucket.audit.name
}

output "kms_key_id" {
  description = "Resource ID of the KMS crypto key."
  value       = google_kms_crypto_key.audit.id
}

output "pubsub_topic" {
  description = "Audit Pub/Sub topic name."
  value       = google_pubsub_topic.audit.name
}

output "manifest_subscription" {
  description = "Subscription for manifest processing."
  value       = google_pubsub_subscription.manifest.name
}

locals {
  base_name = lower("${var.name_prefix}-${var.environment}")
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "google_kms_key_ring" "audit" {
  project  = var.project_id
  name     = "${local.base_name}-audit"
  location = var.location
}

resource "google_kms_crypto_key" "audit" {
  name            = "${local.base_name}-audit"
  key_ring        = google_kms_key_ring.audit.id
  rotation_period = "31536000s" # 1 year

  purpose = "ENCRYPT_DECRYPT"

  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}

resource "google_storage_bucket" "audit" {
  name          = "${local.base_name}-audit-${random_id.suffix.hex}"
  project       = var.project_id
  location      = upper(var.location)
  force_destroy = false

  uniform_bucket_level_access = true
  storage_class               = "STANDARD"

  versioning {
    enabled = true
  }

  retention_policy {
    retention_period = var.bucket_retention_days * 86400
  }

  lifecycle_rule {
    condition {
      age        = var.coldline_transition_days
      with_state = "LIVE"
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  labels = merge(var.labels, {
    environment = var.environment
    purpose     = "audit-log-archive"
  })
}

resource "google_storage_bucket_iam_member" "translator" {
  bucket = google_storage_bucket.audit.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.translator_service_account}"
}

resource "google_storage_bucket_iam_member" "translator_reader" {
  bucket = google_storage_bucket.audit.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.translator_service_account}"
}

resource "google_storage_bucket_iam_member" "manifest" {
  bucket = google_storage_bucket.audit.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.manifest_service_account}"
}

resource "google_pubsub_topic" "audit" {
  name    = "${local.base_name}-audit-events"
  project = var.project_id

  labels = merge(var.labels, {
    environment = var.environment
    purpose     = "audit-events"
  })
}

resource "google_pubsub_subscription" "manifest" {
  name  = "${local.base_name}-manifest"
  topic = google_pubsub_topic.audit.name

  ack_deadline_seconds = 30
  retain_acked_messages = true
  message_retention_duration = "432000s" # 5 days

  expiration_policy {
    ttl = ""
  }
}

resource "google_project_iam_member" "translator_kms" {
  project = var.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member  = "serviceAccount:${var.translator_service_account}"
}

resource "google_project_iam_member" "manifest_kms" {
  project = var.project_id
  role    = "roles/cloudkms.signerVerifier"
  member  = "serviceAccount:${var.manifest_service_account}"
}

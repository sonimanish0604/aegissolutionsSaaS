provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  network_name = "${var.name_prefix}-${var.environment}-vpc"
}

resource "google_compute_network" "audit" {
  name                    = local.network_name
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"
}

resource "google_compute_subnetwork" "audit" {
  name          = "${local.network_name}-subnet"
  ip_cidr_range = var.network_cidr
  region        = var.region
  network       = google_compute_network.audit.id
}

resource "google_service_account" "translator" {
  account_id   = replace("${var.name_prefix}-${var.environment}-translator", "-", "_")
  display_name = "Aegis Translator (${var.environment})"
}

resource "google_service_account" "manifest" {
  account_id   = replace("${var.name_prefix}-${var.environment}-manifest", "-", "_")
  display_name = "Aegis Manifest (${var.environment})"
}

module "audit_pipeline" {
  source      = "../../modules/gcp_audit_pipeline"
  project_id  = var.project_id
  location    = var.region
  name_prefix = var.name_prefix
  environment = var.environment

  translator_service_account = google_service_account.translator.email
  manifest_service_account   = google_service_account.manifest.email
  labels                     = var.labels
}

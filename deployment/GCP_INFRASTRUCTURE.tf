# Terraform plan for the Brant Roofing System GCP Infrastructure
# This plan provisions all prerequisite resources mentioned in GCP_DEPLOYMENT.md.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

# ------------------------------------------------------------------------------
# VARIABLES
# ------------------------------------------------------------------------------

variable "project_id" {
  description = "The GCP project ID to deploy resources to."
  type        = string
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "The password for the Cloud SQL database user. This should be a strong, generated password."
  type        = string
  sensitive   = true
}

variable "db_user" {
  description = "The username for the Cloud SQL database."
  type        = string
  default     = "brant_user"
}

variable "db_name" {
  description = "The name of the Cloud SQL database."
  type        = string
  default     = "brant_db"
}

# ------------------------------------------------------------------------------
# PROVIDER & API CONFIGURATION
# ------------------------------------------------------------------------------

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable all necessary APIs for the project
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "documentai.googleapis.com",
    "vpcaccess.googleapis.com",
    "redis.googleapis.com",
    "compute.googleapis.com",      # For VPC
    "certificatemanager.googleapis.com", # For SSL Certs
    "servicenetworking.googleapis.com" # For private service connection
  ])

  project                    = var.project_id
  service                    = each.key
  disable_dependent_services = true
}

# ------------------------------------------------------------------------------
# NETWORKING
# ------------------------------------------------------------------------------

# VPC Network for private communication between services
resource "google_compute_network" "vpc_network" {
  name                    = "brant-vpc"
  auto_create_subnetworks = false
}

# Subnet for the services
resource "google_compute_subnetwork" "subnet" {
  name          = "brant-subnet"
  ip_cidr_range = "10.10.0.0/24"
  network       = google_compute_network.vpc_network.id
  region        = var.region
}

# Required for private IP for Cloud SQL and Memorystore
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-for-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# 5. Serverless VPC Access Connector
resource "google_vpc_access_connector" "connector" {
  name          = "brant-vpc-connector"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28" # Must be an unused /28 block in your VPC
  network       = google_compute_network.vpc_network.name

  depends_on = [google_project_service.apis]
}

# ------------------------------------------------------------------------------
# IAM & SERVICE ACCOUNTS
# ------------------------------------------------------------------------------

# 2. Service Account for the Cloud Run applications
resource "google_service_account" "app_sa" {
  account_id   = "brant-app-sa"
  display_name = "Brant Application Service Account"
}

# Grant necessary runtime roles to the service account
resource "google_project_iam_member" "sa_roles" {
  for_each = toset([
    "roles/secretmanager.secretAccessor",
    "roles/cloudsql.client",
    "roles/documentai.user",
    "roles/storage.objectAdmin" # As per cloudbuild.yaml
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# ------------------------------------------------------------------------------
# LOAD BALANCER & EDGE SECURITY (NEW)
# ------------------------------------------------------------------------------

# Reserve a static global IP for the load balancer
resource "google_compute_global_address" "lb_static_ip" {
  name = "brant-lb-static-ip"
}

# Cloud Armor WAF policy
resource "google_compute_security_policy" "armor_policy" {
  name        = "brant-api-security-policy"
  description = "Cloud Armor WAF policy for the Brant API"

  # Default rule to allow traffic that doesn't match other rules
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow all"
  }

  # Pre-configured WAF rule for SQL Injection
  rule {
    action   = "deny(403)"
    priority = 1000
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Deny SQL injection attacks"
  }

  # Pre-configured WAF rule for Cross-Site Scripting (XSS)
  rule {
    action   = "deny(403)"
    priority = 1001
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Deny XSS attacks"
  }
}

# ------------------------------------------------------------------------------
# SERVICES (DATABASES, REGISTRY, STORAGE)
# ------------------------------------------------------------------------------

# 3. Cloud SQL for PostgreSQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "brant-postgres-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-g1-small" # Choose an appropriate tier for your needs
    # Set availability to REGIONAL for high availability.
    # This creates a standby instance in a different zone for automatic failover.
    availability_type = "REGIONAL"
    ip_configuration {
      ipv4_enabled    = false # Disable public IP for security
      private_network = google_compute_network.vpc_network.id
    }
  }
  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# 4. Memorystore for Redis instance
resource "google_redis_instance" "redis" {
  name               = "brant-redis-instance"
  # STANDARD_HA provides a replica and automatic failover for high availability.
  tier               = "STANDARD_HA"
  memory_size_gb     = 1
  region             = var.region
  authorized_network = google_compute_network.vpc_network.id
  depends_on         = [google_service_networking_connection.private_vpc_connection]
}

# 6. Artifact Registry for Docker images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "brant-repo"
  description   = "Docker repository for Brant application"
  format        = "DOCKER"
}

# GCS Bucket for file uploads (mentioned in SECRETS.md)
resource "google_storage_bucket" "uploads_bucket" {
  name                        = "${var.project_id}-brant-uploads" # Bucket names must be globally unique
  location                    = var.region
  force_destroy               = false # Set to true for dev/test if you need to easily destroy it
  uniform_bucket_level_access = true
}

# ------------------------------------------------------------------------------
# SECRETS MANAGEMENT
# ------------------------------------------------------------------------------

# 7. Create secrets in Secret Manager
resource "google_secret_manager_secret" "secrets" {
  for_each = toset([
    "brant-database-url", "brant-anthropic-api-key", "brant-celery-broker-url",
    "brant-celery-result-backend", "brant-secret-key", "brant-google-cloud-storage-bucket",
    "brant-document-ai-processor-id", "brant-document-ai-location"
  ])
  secret_id = each.key
  replication { automatic = true }
}

# Create initial versions for the secrets.
# IMPORTANT: You MUST manually update the placeholder values in the GCP console after creation.
resource "google_secret_manager_secret_version" "secret_versions" {
  for_each = {
    "brant-database-url"                  = "postgresql+asyncpg://${var.db_user}:${var.db_password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${var.db_name}"
    "brant-celery-broker-url"             = "redis://${google_redis_instance.redis.host}:6379/0"
    "brant-celery-result-backend"         = "redis://${google_redis_instance.redis.host}:6379/0"
    "brant-google-cloud-storage-bucket"   = google_storage_bucket.uploads_bucket.name
    "brant-anthropic-api-key"             = "placeholder-update-in-gcp-console"
    "brant-secret-key"                    = "placeholder-update-in-gcp-console-with-openssl-rand-hex-32"
    "brant-document-ai-processor-id"      = "placeholder-update-in-gcp-console"
    "brant-document-ai-location"          = "placeholder-update-in-gcp-console"
  }
  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value
}

# ------------------------------------------------------------------------------
# AUTOMATED MIGRATIONS (NEW)
# ------------------------------------------------------------------------------

# Cloud Run Job for database migrations, to be triggered by Cloud Build.
resource "google_cloud_run_v2_job" "db_migrator" {
  name     = "brant-db-migrations"
  location = var.region

  template {
    template {
      service_account = google_service_account.app_sa.email
      containers {
        # The image will be updated by the Cloud Build pipeline on each run.
        image   = "us-central1-docker.pkg.dev/${var.project_id}/brant-repo/brant-api:latest"
        command = ["alembic", "upgrade", "head"]
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
      }
      vpc_access {
        connector = google_vpc_access_connector.connector.id
        egress    = "ALL_TRAFFIC"
      }
    }
  }
}
# ------------------------------------------------------------------------------
# OUTPUTS (NEW)
# ------------------------------------------------------------------------------

output "load_balancer_ip" {
  description = "The static IP address of the Global External HTTPS Load Balancer. Use this for your DNS 'A' record."
  value       = google_compute_global_address.lb_static_ip.address
}

output "cloud_run_api_service_name" {
  description = "The name of the API Cloud Run service, used for the Serverless NEG."
  value       = "brant-api" # Must match _SERVICE_NAME_API in cloudbuild.yaml
}

output "cloud_armor_policy_name" {
  description = "The name of the Cloud Armor policy to attach to the LB backend."
  value       = google_compute_security_policy.armor_policy.name
}

output "instructions" {
  description = "Post-Terraform manual steps to complete LB setup."
  value = <<EOT
Terraform has provisioned the core infrastructure. The Load Balancer cannot be fully configured
until Cloud Run deploys the 'brant-api' service for the first time.

After running your Cloud Build pipeline once:
1. Create a Serverless NEG (Network Endpoint Group):
   - Name: brant-api-sneg
   - Region: ${var.region}
   - Cloud Run Service: brant-api

2. Create a Backend Service:
   - Name: brant-api-backend-service
   - Backend type: Serverless Network Endpoint Group
   - Attach the 'brant-api-sneg' you just created.
   - Security: Attach the Cloud Armor policy '${google_compute_security_policy.armor_policy.name}'.
   - Enable Cloud CDN.

3. Create an HTTPS Load Balancer:
   - Frontend: Use IP address '${google_compute_global_address.lb_static_ip.address}' and create a Google-managed SSL certificate for your domain.
   - Backend: Use the 'brant-api-backend-service'.

4. Update your DNS 'A' record to point to '${google_compute_global_address.lb_static_ip.address}'.

5. Update your Cloud Build Trigger's '_API_URL' variable with your final HTTPS domain URL.
EOT
}
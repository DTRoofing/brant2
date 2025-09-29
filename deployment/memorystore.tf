# Google Cloud Memorystore Redis Instance
# This file creates a Memorystore Redis instance for the Brant Roofing System

# Enable the Redis API
resource "google_project_service" "redis_api" {
  service = "redis.googleapis.com"
  disable_on_destroy = false
}

# Create a VPC network for Memorystore (if not using default)
resource "google_compute_network" "brant_vpc" {
  name                    = "brant-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Create a subnet for Memorystore
resource "google_compute_subnetwork" "brant_subnet" {
  name          = "brant-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.brant_vpc.id
  project       = var.project_id
}

# Create a private service connection for Memorystore
resource "google_compute_global_address" "brant_private_ip_alloc" {
  name          = "brant-private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.brant_vpc.id
  project       = var.project_id
}

resource "google_service_networking_connection" "brant_private_vpc_connection" {
  network                 = google_compute_network.brant_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.brant_private_ip_alloc.name]
  project                 = var.project_id
}

# Memorystore Redis Instance
resource "google_redis_instance" "brant_redis" {
  name           = "brant-redis-instance"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size_gb
  region         = var.region
  project        = var.project_id

  # Network configuration
  authorized_network = google_compute_network.brant_vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Redis configuration
  redis_version     = var.redis_version
  display_name      = "Brant Roofing System Redis"
  reserved_ip_range = google_compute_global_address.brant_private_ip_alloc.name

  # Security configuration
  auth_enabled = var.redis_auth_enabled
  transit_encryption_mode = var.redis_transit_encryption_mode

  # Maintenance configuration
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }

  # Backup configuration
  dynamic "redis_configs" {
    for_each = var.redis_configs
    content {
      key   = redis_configs.key
      value = redis_configs.value
    }
  }

  depends_on = [
    google_project_service.redis_api,
    google_service_networking_connection.brant_private_vpc_connection
  ]

  lifecycle {
    prevent_destroy = true
  }
}

# Output the Redis instance details
output "redis_instance_host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.brant_redis.host
}

output "redis_instance_port" {
  description = "The port of the Redis instance"
  value       = google_redis_instance.brant_redis.port
}

output "redis_instance_auth_string" {
  description = "The AUTH string for the Redis instance"
  value       = google_redis_instance.brant_redis.auth_string
  sensitive   = true
}

output "redis_instance_current_location_id" {
  description = "The current location ID of the Redis instance"
  value       = google_redis_instance.brant_redis.current_location_id
}

# IAM binding for Cloud Run service account
resource "google_redis_instance_iam_binding" "brant_redis_iam" {
  project  = var.project_id
  instance = google_redis_instance.brant_redis.name
  role     = "roles/redis.editor"
  members = [
    "serviceAccount:${var.cloud_run_service_account_email}"
  ]
}

# Monitoring and alerting
resource "google_monitoring_alert_policy" "redis_memory_usage" {
  display_name = "Redis Memory Usage Alert"
  combiner     = "OR"
  conditions {
    display_name = "Redis memory usage is high"
    condition_threshold {
      filter          = "resource.type=\"redis_instance\" AND resource.labels.instance_id=\"${google_redis_instance.brant_redis.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.8
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  notification_channels = var.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "redis_connection_count" {
  display_name = "Redis Connection Count Alert"
  combiner     = "OR"
  conditions {
    display_name = "Redis connection count is high"
    condition_threshold {
      filter          = "resource.type=\"redis_instance\" AND resource.labels.instance_id=\"${google_redis_instance.brant_redis.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 1000
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  notification_channels = var.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

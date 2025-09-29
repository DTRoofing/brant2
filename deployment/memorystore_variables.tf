# Variables for Memorystore configuration

variable "redis_tier" {
  description = "The service tier of the Redis instance"
  type        = string
  default     = "BASIC"
  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.redis_tier)
    error_message = "Redis tier must be either BASIC or STANDARD_HA."
  }
}

variable "redis_memory_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
  validation {
    condition     = var.redis_memory_size_gb >= 1 && var.redis_memory_size_gb <= 300
    error_message = "Redis memory size must be between 1 and 300 GB."
  }
}

variable "redis_version" {
  description = "The version of Redis software"
  type        = string
  default     = "REDIS_7_0"
  validation {
    condition     = contains(["REDIS_6_X", "REDIS_7_0"], var.redis_version)
    error_message = "Redis version must be either REDIS_6_X or REDIS_7_0."
  }
}

variable "redis_auth_enabled" {
  description = "Indicates whether OSS Redis AUTH is enabled"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_mode" {
  description = "The TLS mode of the Redis instance"
  type        = string
  default     = "SERVER_AUTHENTICATION"
  validation {
    condition     = contains(["DISABLED", "SERVER_AUTHENTICATION"], var.redis_transit_encryption_mode)
    error_message = "Redis transit encryption mode must be either DISABLED or SERVER_AUTHENTICATION."
  }
}

variable "redis_configs" {
  description = "Redis configuration parameters"
  type        = map(string)
  default = {
    "maxmemory-policy" = "allkeys-lru"
    "timeout"          = "300"
    "tcp-keepalive"    = "60"
  }
}

variable "cloud_run_service_account_email" {
  description = "Email of the Cloud Run service account"
  type        = string
  default     = ""
}

variable "notification_channels" {
  description = "List of notification channels for alerts"
  type        = list(string)
  default     = []
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

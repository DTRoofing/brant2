# Terraform Infrastructure Audit & Fix Guide for Google Cloud Platform

*A comprehensive guide to analyze, debug, and fix Terraform configurations for production-ready Google Cloud deployments*

---

## Executive Summary

This guide provides a systematic approach to conducting forensic-level analysis of Terraform configurations for Google Cloud Platform deployments. It covers the five critical pillars of infrastructure readiness: bug detection, network configuration, service linkage, best practices compliance, and edge case analysis.

**Target Audience**: DevOps Engineers, Cloud Architects, Site Reliability Engineers  
**Estimated Time**: 4-8 hours for complete audit  
**Prerequisites**: Terraform 1.0+, Google Cloud CLI, appropriate IAM permissions

---

## TERRAFORM ANALYSIS FRAMEWORK

### The 5-Pillar Production Readiness Model

1. **🔍 BUG DETECTION & ANALYSIS** - Runtime bugs, service integration bugs, configuration bugs
2. **🌐 PORT & NETWORK CONFIGURATION VALIDATION** - Port binding, firewall rules, network configuration  
3. **🔗 SERVICE LINKAGE & INTEGRATION VERIFICATION** - Service dependencies, authentication chains, API integrations
4. **✅ BEST PRACTICES COMPLIANCE AUDIT** - Security, performance, cost optimization, operational practices
5. **⚠️ EDGE CASE & FAILURE MODE ANALYSIS** - Network edge cases, resource exhaustion, concurrent access, error propagation

---

# PILLAR 1: COMPREHENSIVE BUG DETECTION

## Phase 1.1: Runtime Bug Investigation

### Memory Management Issues

Analyze for these critical patterns:

```python
# Memory leak patterns to detect:
def find_memory_leaks():
    """
    Search for:
    - Event listeners not removed (addEventListener without removeEventListener)
    - Circular references in object graphs
    - Global variables accumulating data
    - Closures capturing large objects
    - Timers/intervals not cleared
    - Database connections not closed
    - File handles not properly released
    """

# Example patterns that cause leaks:
LEAK_PATTERNS = [
    "setInterval without clearInterval",
    "setTimeout in loops without cleanup",
    "addEventListener without removeEventListener", 
    "database connections without .close()",
    "file streams without .end() or .close()",
    "global arrays that only grow"
]
```

### Concurrency & Threading Issues

```python
# Race condition detection patterns:
def detect_race_conditions():
    """
    Find these dangerous patterns:
    - Shared mutable state without proper locking
    - Non-atomic read-modify-write operations
    - Database transactions without proper isolation
    - File system operations without locking
    - Cache operations without consistency guarantees
    - Async operations with shared state
    """

RACE_CONDITION_INDICATORS = [
    "global variables modified by multiple functions",
    "database updates without transactions", 
    "file operations without locking",
    "shared counters without atomic operations",
    "async functions modifying same object properties"
]
```

### Error Handling Deficiencies

```javascript
// Error handling anti-patterns to catch:
const ERROR_ANTIPATTERNS = {
    "swallowed_exceptions": "catch blocks with no logging or action",
    "generic_catches": "catch(error) without specific error handling",
    "missing_finally": "resource cleanup not in finally blocks",
    "unhandled_promises": "Promise without .catch() or try/catch in async",
    "network_errors": "HTTP requests without timeout/error handling",
    "database_errors": "DB queries without connection error handling"
};

// Find these specific patterns:
function findErrorHandlingBugs(code) {
    // Look for:
    // - try/catch with empty catch blocks
    // - async functions without error handling
    // - network requests without timeout
    // - database operations without connection error handling
    // - JSON.parse without try/catch
    // - Missing validation of external inputs
}
```

## Phase 1.2: Service Integration Bug Analysis

### Google Cloud Service Integration Issues

```python
# Cloud Storage integration bugs:
def analyze_cloud_storage_bugs():
    """
    Common Cloud Storage bugs to detect:
    - Missing bucket existence checks before operations
    - Hardcoded bucket names in multiple files
    - Race conditions in concurrent uploads/downloads
    - Missing error handling for network timeouts
    - Improper handling of eventually consistent operations
    - Missing retry logic for transient failures
    - Signed URL generation without expiration validation
    - Missing CORS configuration for browser uploads
    """

# Cloud SQL/Database integration bugs:
def analyze_database_bugs():
    """
    Database integration issues:
    - Connection pool exhaustion scenarios  
    - SQL injection vulnerabilities
    - Missing transaction management
    - Database migrations without rollback procedures
    - Connection leaks in error paths
    - Missing connection timeout configuration
    - Improper handling of connection failures
    - N+1 query problems
    """

# Vision API/Document AI bugs:
def analyze_ai_api_bugs():
    """
    AI API integration issues:
    - Missing file size validation before API calls
    - No handling of quota exhaustion
    - Missing retry logic for rate limiting
    - Improper error handling for malformed inputs
    - No timeout configuration for long-running operations
    - Missing confidence score validation
    - Batch processing without proper error isolation
    """
```

### Authentication & Authorization Bugs

```yaml
# Authentication bug patterns:
auth_bugs_to_detect:
  service_accounts:
    - "Hardcoded service account keys in code"
    - "Missing service account validation" 
    - "Overprivileged service accounts"
    - "Service account keys committed to version control"
    
  jwt_handling:
    - "JWT tokens without expiration validation"
    - "Missing JWT signature verification"
    - "Hardcoded JWT secrets"
    - "No token refresh logic"
    
  oauth_flows:
    - "Missing CSRF protection in OAuth flows"
    - "Improper redirect URI validation"
    - "State parameter not validated"
    - "Authorization code reuse"
```

## Phase 1.3: Configuration Bug Detection

### Environment Configuration Issues

```bash
# Configuration bugs to detect:

# Missing environment variables
REQUIRED_ENV_VARS=(
    "DATABASE_URL"
    "GOOGLE_CLOUD_PROJECT" 
    "STORAGE_BUCKET"
    "REDIS_URL"
)

# Check for:
config_issues=(
    "Hardcoded production URLs in code"
    "Missing environment variable validation"
    "Default values that aren't production-safe" 
    "Configuration files committed with secrets"
    "Missing configuration schema validation"
    "Environment-specific configs in wrong files"
)
```

### Build & Deployment Configuration Bugs

```dockerfile
# Dockerfile issues to detect:
FROM node:18-alpine
# Check for:
# - Running as root user (security issue)
# - Missing .dockerignore file
# - Installing dev dependencies in production
# - Missing health checks
# - Hardcoded values instead of build args
# - Missing multi-stage builds for size optimization
# - Vulnerable base images
```

---

# PILLAR 2: PORT & NETWORK CONFIGURATION VALIDATION

## Phase 2.1: Port Binding Analysis

### Dynamic Port Configuration

```javascript
// Check for proper port configuration patterns:
const PORT_VALIDATION_PATTERNS = {
    "correct": [
        "const port = process.env.PORT || 8080",
        "app.listen(process.env.PORT)",
        "server.listen(PORT, '0.0.0.0')"
    ],
    "incorrect": [
        "app.listen(3000)",  // Hardcoded port
        "server.listen(8080, 'localhost')",  // Localhost binding
        "app.listen(PORT, '127.0.0.1')"  // Loopback only
    ]
};

// Cloud Run specific port issues:
function validateCloudRunPorts() {
    // Must listen on 0.0.0.0
    // Must use PORT environment variable
    // Cannot bind to multiple ports
    // Must handle SIGTERM gracefully
}
```

### Service Port Mapping Validation

```yaml
# Kubernetes service configuration validation:
apiVersion: v1
kind: Service
spec:
  ports:
  - port: 80          # External port
    targetPort: 8080  # Container port - MUST match app
    protocol: TCP
  
# Common port mapping bugs:
port_mapping_issues:
  - "Service port doesn't match container port"
  - "Health check port different from service port"
  - "LoadBalancer port not in allowed range"
  - "NodePort conflicts with other services"
```

## Phase 2.2: Firewall & Network Security Analysis

### Firewall Rule Validation

```bash
# Firewall rule patterns to validate:

# Overly permissive rules (SECURITY RISK):
DANGEROUS_RULES=(
    "0.0.0.0/0 on any port"
    "* source tags with wide port ranges"
    "Default-allow-internal without restrictions"
)

# Missing required rules:
REQUIRED_RULES=(
    "Health check ingress (130.211.0.0/22, 35.191.0.0/16)"
    "Load balancer ingress on application ports"
    "Egress rules for external API dependencies"
)

# Network security validation:
function validate_network_security() {
    # Check for:
    # - Default VPC usage (should use custom VPC)
    # - Missing Private Google Access
    # - Overly broad firewall rules  
    # - Missing egress restrictions
    # - Unencrypted traffic (should enforce HTTPS)
}
```

### Load Balancer Configuration Issues

```yaml
# Load balancer configuration bugs:
load_balancer_issues:
  health_checks:
    - "Health check path returns 404"
    - "Health check timeout too short" 
    - "Missing readiness vs liveness distinction"
    - "Health check port incorrect"
    
  ssl_configuration:
    - "Missing SSL redirect"
    - "Weak SSL ciphers allowed"
    - "Certificate auto-renewal not configured"
    - "HSTS headers not set"
    
  backend_configuration:
    - "Session affinity incorrectly configured"
    - "Connection draining timeout too short"
    - "Backend service capacity incorrect"
```

## Phase 2.3: Internal Network Connectivity

### VPC & Subnet Configuration

```python
# Network connectivity issues to detect:
def analyze_vpc_connectivity():
    """
    Network connectivity problems:
    - Services in different VPCs unable to communicate
    - Subnet IP ranges overlapping
    - Missing routes for internal communication
    - NAT gateway misconfiguration
    - Private Google Access not enabled
    - Service mesh configuration issues
    """

CONNECTIVITY_TESTS = [
    "App Engine to Cloud SQL connectivity",
    "Cloud Run to Cloud Storage access", 
    "GKE pods to external APIs",
    "Internal load balancer accessibility",
    "Cross-region service communication"
]
```

---

# PILLAR 3: SERVICE LINKAGE & INTEGRATION VERIFICATION

## Phase 3.1: Service Dependency Mapping

### Critical Service Dependencies

```mermaid
# Service dependency analysis required:
graph TD
    A[Web App] --> B[Cloud SQL]
    A --> C[Cloud Storage] 
    A --> D[Redis Cache]
    A --> E[External APIs]
    B --> F[Cloud SQL Proxy]
    C --> G[CDN]
    H[Cloud Functions] --> B
    H --> I[Pub/Sub]
    
# For each connection, validate:
# - Authentication mechanism
# - Error handling and retries
# - Timeout configuration
# - Fallback/degraded mode
# - Health check dependencies
```

### Authentication Chain Validation

```python
# Service-to-service authentication bugs:
def validate_auth_chains():
    """
    Authentication issues to detect:
    - Service accounts without required IAM roles
    - Missing Workload Identity binding in GKE
    - Application Default Credentials not working
    - Cross-project service authentication failures
    - Token refresh not implemented
    - Service account key rotation issues
    """

AUTH_CHAIN_TESTS = {
    "app_engine_to_cloud_sql": "validate service account has cloudsql.client role",
    "cloud_run_to_storage": "validate service account has storage.objectAdmin",
    "gke_to_secret_manager": "validate workload identity and secretmanager.accessor",
    "cloud_function_to_firestore": "validate service account has datastore.user"
}
```

## Phase 3.2: API Integration Analysis

### External API Integration Issues

```javascript
// API integration patterns to validate:
const API_INTEGRATION_BUGS = {
    timeout_issues: [
        "No request timeout configured",
        "Timeout longer than service timeout",
        "Missing connection timeout",
        "Read timeout not set"
    ],
    
    retry_logic: [
        "No retry for transient failures",
        "Infinite retry loops",
        "No exponential backoff", 
        "Retrying non-idempotent operations"
    ],
    
    error_handling: [
        "Not checking HTTP status codes",
        "Assuming all responses are JSON",
        "No handling for rate limiting",
        "Missing circuit breaker pattern"
    ]
};

// Example proper API integration:
async function robustApiCall(url, options) {
    // Must have: timeout, retry, error handling, logging
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        // Proper error logging and re-throwing
        logger.error('API call failed', { url, error: error.message });
        throw error;
    } finally {
        clearTimeout(timeout);
    }
}
```

### Database Integration Validation

```sql
-- Database integration issues to detect:

-- Connection pooling problems:
SELECT 
    count(*) as active_connections,
    max_connections,
    count(*) * 100.0 / max_connections as connection_usage_percent
FROM information_schema.processlist
CROSS JOIN (SELECT @@max_connections as max_connections) t;

-- Check for these patterns in code:
-- 1. Database connections not properly closed
-- 2. Connection pool exhaustion 
-- 3. Long-running transactions
-- 4. Missing query timeouts
-- 5. N+1 query problems
-- 6. Missing indexes on frequently queried columns
-- 7. Transactions without proper error handling
```

---

# PILLAR 4: BEST PRACTICES COMPLIANCE AUDIT

## Phase 4.1: Security Best Practices

### Secret Management Audit

```python
# Secret management issues to detect:
SECRET_VIOLATIONS = {
    "hardcoded_secrets": [
        "API keys in source code",
        "Database passwords in configuration files",
        "JWT secrets as string literals",
        "Service account keys in repositories"
    ],
    
    "improper_secret_access": [
        "Secrets in environment variables (visible in process list)",
        "Secrets in Docker build args", 
        "Secrets in Kubernetes ConfigMaps (should use Secrets)",
        "Missing Secret Manager integration"
    ],
    
    "secret_rotation": [
        "No automatic secret rotation",
        "Hardcoded certificate expiration dates",
        "Manual secret update processes"
    ]
}

# Proper secret management pattern:
def get_secret(secret_name):
    """Use Google Secret Manager instead of environment variables"""
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(
        request={"name": f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"}
    )
    return response.payload.data.decode("UTF-8")
```

### Input Validation & Security

```javascript
// Security validation patterns:
const SECURITY_CHECKS = {
    input_validation: [
        "SQL injection prevention (parameterized queries)",
        "XSS prevention (input sanitization)",
        "CSRF protection (tokens/headers)",
        "File upload validation (type, size limits)",
        "JSON schema validation",
        "Rate limiting implementation"
    ],
    
    authentication: [
        "Password complexity requirements",
        "Multi-factor authentication support",
        "Session timeout configuration", 
        "Secure cookie attributes (httpOnly, secure, sameSite)"
    ],
    
    authorization: [
        "Role-based access control (RBAC)",
        "Resource-level permissions",
        "API endpoint authorization",
        "Principle of least privilege"
    ]
};

// Example secure input validation:
function validateAndSanitizeInput(input, schema) {
    // 1. Schema validation
    const validationResult = validateSchema(input, schema);
    if (!validationResult.valid) {
        throw new ValidationError(validationResult.errors);
    }
    
    // 2. Sanitization  
    const sanitized = sanitizeHtml(input, {
        allowedTags: [],
        allowedAttributes: {}
    });
    
    // 3. Additional business logic validation
    return sanitized;
}
```

## Phase 4.2: Performance Best Practices

### Caching Strategy Analysis

```python
# Caching implementation validation:
def analyze_caching_strategy():
    """
    Caching issues to detect:
    - Missing caching for expensive operations
    - Cache invalidation strategy not implemented
    - No cache warming for critical data
    - Cache stampede problems (multiple processes rebuilding same cache)
    - Missing cache monitoring and hit rate tracking
    - Inconsistent TTL values across related data
    """

CACHING_PATTERNS = {
    "application_level": "In-memory caching with proper eviction",
    "database_level": "Query result caching with invalidation",
    "cdn_level": "Static asset caching with appropriate headers",
    "api_level": "Response caching with cache-control headers"
}

# Example proper caching implementation:
import redis
import json
from datetime import timedelta

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT', 6379),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def get_or_set(self, key, fetch_function, ttl=3600):
        """Get from cache or fetch and cache"""
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
        except redis.RedisError as e:
            logger.warning(f"Cache read failed: {e}")
        
        # Fetch fresh data
        value = fetch_function()
        
        # Cache the result
        try:
            self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value, default=str)
            )
        except redis.RedisError as e:
            logger.warning(f"Cache write failed: {e}")
        
        return value
```

## Phase 4.3: Cost Optimization Analysis

### Resource Right-Sizing

```yaml
# Resource optimization checks:
resource_optimization:
  compute_engine:
    - "Instance types match actual usage patterns"
    - "Committed use discounts applied where appropriate" 
    - "Preemptible instances used for batch workloads"
    - "Auto-scaling configured to prevent over-provisioning"
    
  cloud_storage:
    - "Storage classes match access patterns"
    - "Lifecycle policies configured for archival"
    - "Regional vs multi-regional based on need"
    - "CDN caching reduces storage access costs"
    
  cloud_sql:
    - "Instance size matches actual usage"
    - "Read replicas used appropriately"
    - "Automated backups configured efficiently"
    - "High availability only where needed"
```

---

# PILLAR 5: EDGE CASE & FAILURE MODE ANALYSIS

## Phase 5.1: Network Edge Cases

### Connection Failure Scenarios

```python
# Network edge cases to test:
NETWORK_EDGE_CASES = {
    "connection_timeout": {
        "scenario": "External API takes longer than expected to respond",
        "test": "Verify timeout configuration and graceful degradation",
        "expected_behavior": "Request fails fast with proper error handling"
    },
    
    "dns_resolution_failure": {
        "scenario": "DNS server becomes unavailable",
        "test": "Verify DNS caching and fallback mechanisms", 
        "expected_behavior": "Service continues with cached DNS or fails gracefully"
    },
    
    "ssl_certificate_expiration": {
        "scenario": "SSL certificate expires during operation",
        "test": "Verify certificate validation and renewal processes",
        "expected_behavior": "Automatic renewal or clear error reporting"
    },
    
    "network_partition": {
        "scenario": "Network split isolates parts of the system",
        "test": "Verify behavior when services can't communicate",
        "expected_behavior": "Graceful degradation with appropriate user feedback"
    }
}

# Example network resilience pattern:
async function resilientNetworkCall(url, options = {}) {
    const maxRetries = 3;
    const baseDelay = 1000;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 10000);
            
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (response.ok) {
                return response;
            } else if (response.status >= 500 && attempt < maxRetries) {
                // Retry on server errors
                await delay(baseDelay * Math.pow(2, attempt - 1));
                continue;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            if (attempt === maxRetries) {
                throw error;
            }
            await delay(baseDelay * Math.pow(2, attempt - 1));
        }
    }
}
```

## Phase 5.2: Resource Exhaustion Edge Cases

### Memory & CPU Exhaustion

```javascript
// Resource exhaustion scenarios:
const RESOURCE_EXHAUSTION_TESTS = {
    memory_pressure: {
        scenario: "Application consumes all available memory",
        indicators: [
            "Large object creation in loops",
            "Memory-intensive operations without cleanup", 
            "Event listener accumulation",
            "Global variable growth"
        ],
        mitigation: "Memory monitoring, garbage collection tuning, resource limits"
    },
    
    cpu_throttling: {
        scenario: "CPU-intensive operations block the event loop",
        indicators: [
            "Synchronous heavy computations",
            "Large array processing without yielding",
            "Complex regex on large strings", 
            "Infinite or near-infinite loops"
        ],
        mitigation: "Async processing, worker threads, operation splitting"
    },
    
    file_descriptor_exhaustion: {
        scenario: "Too many open files/connections",
        indicators: [
            "Database connections not closed",
            "File handles not released",
            "HTTP connections not properly managed"
        ],
        mitigation: "Connection pooling, proper resource cleanup, monitoring"
    }
};

// Example resource monitoring:
function monitorResourceUsage() {
    const usage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    if (usage.heapUsed / usage.heapTotal > 0.9) {
        logger.warn('High memory usage detected', { 
            heapUsed: usage.heapUsed,
            heapTotal: usage.heapTotal 
        });
        // Trigger garbage collection or alert
    }
}

setInterval(monitorResourceUsage, 30000);
```

---

# TERRAFORM CONFIGURATION BEST PRACTICES

## State Management & Configuration

### Proper State Backend Setup

```hcl
# terraform/backend.tf
terraform {
  backend "gcs" {
    bucket  = "your-terraform-state-bucket"
    prefix  = "terraform/state"
  }
}

# Create state bucket first:
resource "google_storage_bucket" "terraform_state" {
  name     = "${var.project_id}-terraform-state"
  location = var.region
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  uniform_bucket_level_access = true
}
```

### Version Constraints

```hcl
# terraform/versions.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.84.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4.3"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.1"
    }
  }
}
```

## Resource Configuration Examples

### Compute Engine Best Practices

```hcl
# modules/compute/main.tf
resource "google_compute_instance" "web" {
  name         = "${var.environment}-web-${random_id.instance_suffix.hex}"
  machine_type = var.machine_type
  zone         = data.google_compute_zones.available.names[0]
  
  tags = ["web-server", var.environment]
  
  boot_disk {
    initialize_params {
      image = data.google_compute_image.debian.self_link
      size  = var.boot_disk_size
      type  = var.boot_disk_type
    }
  }
  
  network_interface {
    network    = var.vpc_id
    subnetwork = var.subnet_id
    
    dynamic "access_config" {
      for_each = var.external_ip ? [1] : []
      content {}
    }
  }
  
  metadata = {
    ssh-keys               = "${var.ssh_user}:${file(var.ssh_public_key_path)}"
    enable-oslogin        = "TRUE"
    startup-script        = file("${path.module}/scripts/startup.sh")
  }
  
  service_account {
    email  = google_service_account.compute.email
    scopes = ["cloud-platform"]
  }
  
  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      metadata["ssh-keys"]
    ]
  }
  
  depends_on = [
    google_project_service.required_apis
  ]
}

resource "random_id" "instance_suffix" {
  byte_length = 4
}

data "google_compute_image" "debian" {
  family  = "debian-11"
  project = "debian-cloud"
}

data "google_compute_zones" "available" {
  region = var.region
}

resource "google_service_account" "compute" {
  account_id   = "${var.environment}-compute-sa"
  display_name = "Compute Engine Service Account"
  description  = "Service account for compute instances"
}
```

### Cloud SQL Best Practices

```hcl
# modules/database/main.tf
resource "google_sql_database_instance" "main" {
  name                = "${var.environment}-db-${random_id.db_suffix.hex}"
  database_version    = var.database_version
  region              = var.region
  deletion_protection = var.environment == "production" ? true : false
  
  settings {
    tier                        = var.database_tier
    availability_type          = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_type                  = "PD_SSD"
    disk_size                  = var.database_disk_size
    disk_autoresize           = true
    disk_autoresize_limit     = var.database_max_disk_size
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }
    
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                              = var.vpc_id
      enable_private_path_for_google_cloud_services = true
    }
    
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    
    maintenance_window {
      day          = 7    # Sunday
      hour         = 3    # 3 AM
      update_track = "stable"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
  }
  
  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_project_service.required_apis
  ]
  
  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      settings[0].disk_size
    ]
  }
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.environment}-private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = var.vpc_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = var.vpc_id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "random_id" "db_suffix" {
  byte_length = 4
}
```

### Networking Best Practices

```hcl
# modules/networking/main.tf
resource "google_compute_network" "vpc" {
  name                    = "${var.environment}-vpc"
  auto_create_subnetworks = false
  description            = "VPC network for ${var.environment} environment"
}

resource "google_compute_subnetwork" "web" {
  name          = "${var.environment}-web-subnet"
  ip_cidr_range = var.web_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
  
  private_ip_google_access = true
  
  dynamic "secondary_ip_range" {
    for_each = var.enable_gke ? [1] : []
    content {
      range_name    = "gke-pods"
      ip_cidr_range = var.gke_pods_cidr
    }
  }
  
  dynamic "secondary_ip_range" {
    for_each = var.enable_gke ? [1] : []
    content {
      range_name    = "gke-services"
      ip_cidr_range = var.gke_services_cidr
    }
  }
}

resource "google_compute_firewall" "web" {
  name    = "${var.environment}-allow-web"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
  
  description = "Allow HTTP and HTTPS traffic to web servers"
}

resource "google_compute_firewall" "internal" {
  name    = "${var.environment}-allow-internal"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "icmp"
  }
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  source_ranges = [var.web_subnet_cidr]
  description   = "Allow internal communication within VPC"
}
```

---

# PRODUCTION-READY TEMPLATES

## Complete Main Configuration

```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "terraform/state"
  }
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.84.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4.3"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.1"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

locals {
  name_prefix = "${var.environment}-${var.project_name}"
  
  common_labels = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
    team        = var.team
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "storage.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
  
  timeouts {
    create = "10m"
    update = "10m"
  }
}

resource "time_sleep" "api_propagation" {
  depends_on = [google_project_service.required_apis]
  create_duration = "60s"
}

module "networking" {
  source = "./modules/networking"
  
  project_id   = var.project_id
  environment  = var.environment
  project_name = var.project_name
  region       = var.region
  
  web_subnet_cidr     = var.web_subnet_cidr
  database_subnet_cidr = var.database_subnet_cidr
  
  depends_on = [time_sleep.api_propagation]
}

module "compute" {
  source = "./modules/compute"
  
  project_id   = var.project_id
  environment  = var.environment
  project_name = var.project_name
  region       = var.region
  
  vpc_id           = module.networking.vpc_id
  subnet_id        = module.networking.web_subnet_id
  machine_type     = var.machine_type
  instance_count   = var.instance_count
  
  depends_on = [module.networking]
}

module "database" {
  source = "./modules/database"
  
  project_id   = var.project_id
  environment  = var.environment
  project_name = var.project_name
  region       = var.region
  
  vpc_id              = module.networking.vpc_id
  database_version    = var.database_version
  database_tier       = var.database_tier
  database_name       = var.database_name
  database_user       = var.database_user
  database_password   = var.database_password
  
  depends_on = [module.networking]
}
```

## Variables Configuration

```hcl
# variables.tf
variable "project_id" {
  description = "The GCP project ID"
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Project ID must be 6-30 characters, start with letter, contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "myapp"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
  validation {
    condition = contains([
      "us-central1", "us-east1", "us-west1", "us-west2",
      "europe-west1", "europe-west2", "asia-southeast1"
    ], var.region)
    error_message = "Region must be a valid GCP region."
  }
}

variable "team" {
  description = "Team responsible for the infrastructure"
  type        = string
  default     = "platform"
}

variable "web_subnet_cidr" {
  description = "CIDR block for web subnet"
  type        = string
  default     = "10.0.1.0/24"
  validation {
    condition     = can(cidrhost(var.web_subnet_cidr, 0))
    error_message = "Web subnet CIDR must be a valid IPv4 CIDR block."
  }
}

variable "database_subnet_cidr" {
  description = "CIDR block for database subnet"
  type        = string
  default     = "10.0.2.0/24"
  validation {
    condition     = can(cidrhost(var.database_subnet_cidr, 0))
    error_message = "Database subnet CIDR must be a valid IPv4 CIDR block."
  }
}

variable "machine_type" {
  description = "Machine type for compute instances"
  type        = string
  default     = "e2-micro"
  validation {
    condition = contains([
      "e2-micro", "e2-small", "e2-medium", "e2-standard-2", "e2-standard-4"
    ], var.machine_type)
    error_message = "Machine type must be a valid GCP machine type."
  }
}

variable "instance_count" {
  description = "Number of compute instances"
  type        = number
  default     = 1
  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}

variable "database_version" {
  description = "Database version"
  type        = string
  default     = "POSTGRES_13"
  validation {
    condition = contains([
      "POSTGRES_13", "POSTGRES_14", "POSTGRES_15",
      "MYSQL_5_7", "MYSQL_8_0"
    ], var.database_version)
    error_message = "Database version must be a supported version."
  }
}

variable "database_tier" {
  description = "Database tier"
  type        = string
  default     = "db-f1-micro"
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "database_user" {
  description = "Database user"
  type        = string
  default     = "appuser"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

## Environment-Specific Configuration

```hcl
# environments/production/terraform.tfvars
project_id   = "my-production-project-123456"
environment  = "production"
project_name = "myapp"
region       = "us-central1"
team         = "platform"

# Network configuration
web_subnet_cidr      = "10.0.1.0/24"
database_subnet_cidr = "10.0.2.0/24"

# Compute configuration
machine_type   = "e2-standard-2"
instance_count = 3

# Database configuration
database_version = "POSTGRES_14"
database_tier    = "db-standard-2"
database_name    = "myapp_prod"
database_user    = "myapp_user"
```

---

# DEPLOYMENT & TROUBLESHOOTING

## Deployment Scripts

### Deploy Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-dev}
PROJECT_ID=${2}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <environment> <project_id>"
    echo "Example: $0 production my-project-123456"
    exit 1
fi

echo "Deploying to $ENVIRONMENT environment in project $PROJECT_ID..."

# Set up environment
cd "environments/$ENVIRONMENT"

# Initialize Terraform
terraform init -upgrade

# Validate configuration
terraform validate

# Plan deployment
terraform plan -var="project_id=$PROJECT_ID" -out=tfplan

# Apply if plan is successful
read -p "Apply the plan? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply tfplan
    rm -f tfplan
    echo "Deployment completed successfully!"
else
    echo "Deployment cancelled."
    rm -f tfplan
fi
```

### Destroy Script

```bash
#!/bin/bash
# scripts/destroy.sh

set -e

ENVIRONMENT=${1:-dev}
PROJECT_ID=${2}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <environment> <project_id>"
    echo "Example: $0 dev my-project-123456"
    exit 1
fi

if [ "$ENVIRONMENT" == "production" ]; then
    echo "ERROR: Cannot destroy production environment using this script"
    echo "Manual destruction required for production safety"
    exit 1
fi

echo "WARNING: This will destroy all resources in $ENVIRONMENT environment!"
read -p "Are you sure? Type 'yes' to confirm: " -r

if [ "$REPLY" != "yes" ]; then
    echo "Destruction cancelled."
    exit 1
fi

cd "environments/$ENVIRONMENT"

# Plan destruction
terraform plan -destroy -var="project_id=$PROJECT_ID" -out=destroy.tfplan

# Apply destruction plan
terraform apply destroy.tfplan
rm -f destroy.tfplan

echo "Environment $ENVIRONMENT has been destroyed."
```

## Common Issues & Solutions

### State Management Issues

```bash
# Fix corrupted state
terraform refresh

# Import existing resources
terraform import google_compute_instance.web projects/$PROJECT_ID/zones/$ZONE/instances/$INSTANCE_NAME

# Remove resources from state
terraform state rm google_compute_instance.web

# Move resources in state
terraform state mv 'google_compute_instance.old' 'google_compute_instance.new'
```

### Permission Issues

```bash
# Required roles for Terraform service account
REQUIRED_ROLES=(
    "roles/compute.admin"
    "roles/storage.admin" 
    "roles/cloudsql.admin"
    "roles/container.admin"
    "roles/iam.serviceAccountAdmin"
    "roles/resourcemanager.projectIamAdmin"
    "roles/serviceusage.serviceUsageAdmin"
)

# Grant roles
for role in "${REQUIRED_ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
done
```

### API Quota Issues

```bash
# Check current quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Request quota increases
gcloud compute quotas --help
```

---

# PRODUCTION READINESS CHECKLIST

## Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Remote state backend configured with locking
- [ ] All required Google Cloud APIs enabled
- [ ] Service accounts created with minimal permissions
- [ ] Network security rules properly configured
- [ ] SSL/TLS certificates configured and auto-renewal enabled
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery procedures tested

### Security Requirements
- [ ] No hardcoded secrets in configuration files
- [ ] Service accounts using workload identity where possible
- [ ] Network access properly restricted
- [ ] Audit logging enabled
- [ ] Encryption at rest and in transit configured
- [ ] Security scanning completed

### Performance Requirements
- [ ] Resources right-sized for expected load
- [ ] Auto-scaling configured where appropriate
- [ ] Caching strategies implemented
- [ ] Database performance optimized
- [ ] CDN configured for static assets

### Cost Optimization
- [ ] Committed use discounts considered
- [ ] Preemptible instances used where appropriate
- [ ] Storage lifecycle policies configured
- [ ] Resource scheduling implemented for non-production
- [ ] Cost monitoring and alerting configured

### Operational Requirements
- [ ] Infrastructure as code properly documented
- [ ] Deployment procedures tested
- [ ] Rollback procedures documented and tested
- [ ] Team training completed
- [ ] On-call procedures established

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: DevOps Team

*This guide is a living document and should be updated as new best practices emerge and Google Cloud Platform evolves.*

# Brant Roofing System - Administrator Guide

## 👨‍💼 Administrator Overview

This guide is designed for system administrators responsible for managing the Brant Roofing System infrastructure, user accounts, and system configuration.

## 🔧 System Administration

### **User Management**

#### **Creating User Accounts**

1. **Access Admin Panel**: Navigate to Admin → User Management
2. **Add New User**: Click "Add User" button
3. **Enter Details**:
   - Full Name
   - Email Address
   - Role (Admin, Manager, User, Viewer)
   - Department
   - Contact Information
4. **Set Permissions**: Configure access levels and restrictions
5. **Send Invitation**: System sends login credentials via email

#### **User Roles and Permissions**

| Role | Document Upload | Processing | Admin Panel | Reports | API Access |
|------|----------------|------------|-------------|---------|------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manager** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **User** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Viewer** | ❌ | ❌ | ❌ | ✅ | ❌ |

#### **Managing User Access**

- **Suspend Users**: Temporarily disable user accounts
- **Reset Passwords**: Force password reset for security
- **Modify Permissions**: Change user roles and access levels
- **Audit Logs**: Review user activity and access patterns

### **System Configuration**

#### **Application Settings**

```yaml
# System Configuration
app:
  name: "Brant Roofing System"
  version: "1.0.0"
  debug: false
  max_file_size: "200MB"
  allowed_formats: ["pdf", "png", "jpg", "tiff", "dwg"]
  
# Processing Settings
processing:
  max_concurrent_jobs: 10
  timeout_minutes: 30
  retry_attempts: 3
  confidence_threshold: 0.7
  
# Security Settings
security:
  session_timeout: 3600
  password_min_length: 8
  require_2fa: true
  max_login_attempts: 5
```

#### **Database Configuration**

```sql
-- Database Performance Settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Create Indexes for Performance
CREATE INDEX CONCURRENTLY idx_documents_status ON documents(processing_status);
CREATE INDEX CONCURRENTLY idx_documents_created ON documents(created_at);
CREATE INDEX CONCURRENTLY idx_measurements_document ON measurements(document_id);
```

#### **Google Cloud Configuration**

```yaml
# GCP Service Configuration
google_cloud:
  project_id: "brant-roofing-system-2025"
  storage_bucket: "brant-documents-prod"
  document_ai:
    location: "us"
    processors:
      invoice: "dc22888af5489eae"
      form_parser: "processor-id-2"
      ocr: "processor-id-3"
  vision_api:
    enabled: true
    max_requests_per_minute: 1000
```

## 📊 Monitoring and Maintenance

### **System Monitoring**

#### **Health Checks**

```bash
#!/bin/bash
# system-health-check.sh

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/v1/health)
if [ $API_STATUS -ne 200 ]; then
    echo "API Health Check Failed: HTTP $API_STATUS"
    exit 1
fi

# Check database connectivity
DB_STATUS=$(docker-compose exec -T postgres psql -U brant_user -d brant_roofing -c "SELECT 1;" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Database Health Check Failed"
    exit 1
fi

# Check Redis connectivity
REDIS_STATUS=$(docker-compose exec -T redis redis-cli ping 2>/dev/null)
if [ "$REDIS_STATUS" != "PONG" ]; then
    echo "Redis Health Check Failed"
    exit 1
fi

echo "All health checks passed"
```

#### **Performance Monitoring**

- **CPU Usage**: Monitor application CPU consumption
- **Memory Usage**: Track RAM usage and memory leaks
- **Disk Space**: Monitor storage usage and cleanup
- **Network I/O**: Track network traffic and bandwidth
- **Database Performance**: Query execution times and connections

#### **Log Management**

```bash
# Log Rotation Configuration
# /etc/logrotate.d/brant-roofing
/var/log/brant-roofing/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 brant brant
    postrotate
        docker-compose restart api worker
    endscript
}
```

### **Backup and Recovery**

#### **Database Backup**

```bash
#!/bin/bash
# database-backup.sh

BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="brant_roofing_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
docker-compose exec -T postgres pg_dump -U brant_user brant_roofing > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Upload to cloud storage
gsutil cp $BACKUP_DIR/$BACKUP_FILE.gz gs://brant-backups/database/

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Database backup completed: $BACKUP_FILE.gz"
```

#### **File Storage Backup**

```bash
#!/bin/bash
# storage-backup.sh

# Sync Google Cloud Storage
gsutil -m rsync -r gs://brant-documents-prod/ gs://brant-backups/documents/

# Verify backup integrity
gsutil ls -l gs://brant-documents-prod/ | wc -l
gsutil ls -l gs://brant-backups/documents/ | wc -l

echo "File storage backup completed"
```

### **System Updates**

#### **Application Updates**

```bash
#!/bin/bash
# update-application.sh

# Pull latest code
git pull origin main

# Build new Docker image
docker-compose build --no-cache

# Run database migrations
docker-compose exec api alembic upgrade head

# Restart services with zero downtime
docker-compose up -d --scale api=2
sleep 30
docker-compose up -d --scale api=1

# Verify update
curl -f http://localhost:3001/api/v1/health

echo "Application update completed"
```

#### **Security Updates**

```bash
#!/bin/bash
# security-update.sh

# Update system packages
apt update && apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image brant-roofing:latest

echo "Security update completed"
```

## 🔒 Security Management

### **Access Control**

#### **API Security**

```yaml
# API Security Configuration
api_security:
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_size: 200
  
  authentication:
    jwt_secret: "your-secret-key"
    token_expiry: 3600
    refresh_token_expiry: 86400
  
  cors:
    allowed_origins: ["https://app.brant-roofing.com"]
    allowed_methods: ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: ["Authorization", "Content-Type"]
```

#### **Network Security**

```bash
# Firewall Configuration
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 5432/tcp   # PostgreSQL (internal only)
ufw deny 6379/tcp   # Redis (internal only)
ufw enable
```

#### **SSL/TLS Configuration**

```nginx
# Nginx SSL Configuration
server {
    listen 443 ssl http2;
    server_name api.brant-roofing.com;
    
    ssl_certificate /etc/letsencrypt/live/api.brant-roofing.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.brant-roofing.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### **Audit and Compliance**

#### **Audit Logging**

```python
# Audit Log Configuration
AUDIT_LOGGING = {
    'enabled': True,
    'log_level': 'INFO',
    'log_file': '/var/log/brant-roofing/audit.log',
    'events': [
        'user_login',
        'user_logout',
        'document_upload',
        'document_process',
        'admin_action',
        'permission_change'
    ]
}
```

#### **Compliance Monitoring**

- **GDPR Compliance**: Data privacy and protection measures
- **SOX Compliance**: Financial data handling and controls
- **HIPAA Compliance**: Health information protection (if applicable)
- **Industry Standards**: Roofing industry best practices

## 📈 Performance Optimization

### **Database Optimization**

#### **Query Performance**

```sql
-- Analyze slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Create missing indexes
CREATE INDEX CONCURRENTLY idx_documents_updated 
ON documents(updated_at) WHERE processing_status = 'completed';

-- Update table statistics
ANALYZE documents;
ANALYZE measurements;
```

#### **Connection Pooling**

```python
# Database Connection Pool Configuration
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'echo': False
}
```

### **Application Optimization**

#### **Caching Strategy**

```python
# Redis Caching Configuration
CACHE_CONFIG = {
    'default': {
        'backend': 'redis',
        'location': 'redis://localhost:6379/1',
        'timeout': 300
    },
    'sessions': {
        'backend': 'redis',
        'location': 'redis://localhost:6379/2',
        'timeout': 3600
    }
}
```

#### **Background Processing**

```python
# Celery Configuration
CELERY_CONFIG = {
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'worker_concurrency': 4,
    'worker_prefetch_multiplier': 1
}
```

## 🚨 Troubleshooting

### **Common Issues**

#### **High CPU Usage**

```bash
# Identify high CPU processes
top -p $(pgrep -f "brant-roofing")

# Check for memory leaks
docker stats brant-api-1

# Restart services if needed
docker-compose restart api worker
```

#### **Database Performance Issues**

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Kill problematic queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <process_id>;
```

#### **Storage Issues**

```bash
# Check disk usage
df -h

# Clean up Docker images
docker system prune -a

# Clean up old logs
find /var/log/brant-roofing -name "*.log" -mtime +30 -delete
```

### **Emergency Procedures**

#### **System Recovery**

1. **Identify Issue**: Check logs and monitoring dashboards
2. **Isolate Problem**: Stop affected services
3. **Restore from Backup**: Use latest backup if needed
4. **Verify Functionality**: Run health checks
5. **Notify Users**: Communicate status updates

#### **Data Recovery**

1. **Stop Services**: Prevent further data corruption
2. **Restore Database**: Use latest backup
3. **Verify Data Integrity**: Check data consistency
4. **Restart Services**: Gradually bring services online
5. **Monitor System**: Watch for recurring issues

## 📞 Support and Escalation

### **Support Levels**

- **Level 1**: Basic user support and common issues
- **Level 2**: Technical issues and system configuration
- **Level 3**: Complex problems and vendor escalation
- **Emergency**: Critical system failures and data loss

### **Escalation Procedures**

1. **Document Issue**: Record problem details and steps taken
2. **Check Resources**: Review documentation and knowledge base
3. **Contact Support**: Use appropriate support channel
4. **Provide Context**: Include logs, screenshots, and error messages
5. **Follow Up**: Track progress and provide additional information

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Document Owner**: Brant Roofing System Development Team

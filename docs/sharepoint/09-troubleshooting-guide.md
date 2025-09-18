# Brant Roofing System - Troubleshooting Guide

## 🔧 Quick Reference

This guide provides solutions to common issues encountered with the Brant Roofing System. Issues are categorized by severity and include step-by-step resolution procedures.

## 🚨 Critical Issues

### **System Down - Complete Service Failure**

#### **Symptoms**

- API returns 500 errors
- All endpoints unresponsive
- Database connection failures
- All users affected

#### **Diagnosis Steps**

```bash
# Check service status
docker-compose ps

# Check system resources
docker stats

# Check logs for errors
docker-compose logs --tail=100 api
docker-compose logs --tail=100 postgres
docker-compose logs --tail=100 redis
```

#### **Resolution Steps**

1. **Check Infrastructure**

   ```bash
   # Verify disk space
   df -h
   
   # Check memory usage
   free -h
   
   # Check CPU usage
   top
   ```

2. **Restart Services**

   ```bash
   # Restart all services
   docker-compose down
   docker-compose up -d
   
   # Verify services are running
   docker-compose ps
   ```

3. **Check Database**

   ```bash
   # Test database connection
   docker-compose exec postgres psql -U brant_user -d brant_roofing -c "SELECT 1;"
   ```

4. **Verify API Health**

   ```bash
   # Test API endpoint
   curl -f http://localhost:3001/api/v1/health
   ```

#### **Prevention**

- Monitor system resources continuously
- Set up automated alerts for resource usage
- Implement health checks and auto-restart
- Regular backup and disaster recovery testing

### **Database Connection Lost**

#### **Symptoms**

- "Database connection failed" errors
- Users cannot save or retrieve data
- Processing jobs fail with database errors

#### **Diagnosis Steps**

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Check connection count
docker-compose exec postgres psql -U brant_user -d brant_roofing -c "SELECT count(*) FROM pg_stat_activity;"

# Check database logs
docker-compose logs postgres | grep ERROR
```

#### **Resolution Steps**

1. **Check Database Service**

   ```bash
   # Restart PostgreSQL
   docker-compose restart postgres
   
   # Wait for startup
   sleep 30
   
   # Test connection
   docker-compose exec postgres psql -U brant_user -d brant_roofing -c "SELECT 1;"
   ```

2. **Check Connection Pool**

   ```bash
   # Check active connections
   docker-compose exec postgres psql -U brant_user -d brant_roofing -c "
   SELECT state, count(*) 
   FROM pg_stat_activity 
   GROUP BY state;"
   ```

3. **Kill Long-Running Queries**

   ```bash
   # Find long-running queries
   docker-compose exec postgres psql -U brant_user -d brant_roofing -c "
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
   
   # Kill problematic queries
   docker-compose exec postgres psql -U brant_user -d brant_roofing -c "SELECT pg_terminate_backend(pid);"
   ```

## ⚠️ High Priority Issues

### **Document Processing Failures**

#### **Symptoms**

- Documents stuck in "processing" status
- Processing jobs fail with errors
- Users receive processing error messages

#### **Diagnosis Steps**

```bash
# Check Celery worker status
docker-compose exec worker celery -A app.workers.celery_app inspect active

# Check failed tasks
docker-compose exec worker celery -A app.workers.celery_app inspect failed

# Check processing logs
docker-compose logs worker | grep ERROR
```

#### **Resolution Steps**

1. **Check Google Cloud Services**

   ```bash
   # Test GCS access
   docker-compose exec worker gsutil ls gs://your-bucket-name
   
   # Check Document AI access
   docker-compose exec worker python -c "
   from app.integrations.gcp_services import GoogleCloudService # Path updated after reorganization
   service = GoogleCloudService()
   print('GCS accessible:', service.gcs_client is not None)
   "
   ```

2. **Restart Processing Workers**

   ```bash
   # Restart Celery workers
   docker-compose restart worker
   
   # Check worker status
   docker-compose exec worker celery -A app.workers.celery_app inspect stats
   ```

3. **Retry Failed Tasks**

   ```bash
   # Retry all failed tasks
   docker-compose exec worker celery -A app.workers.celery_app control retry_failed
   ```

### **High Memory Usage**

#### **Symptoms**

- System becomes slow and unresponsive
- Out of memory errors in logs
- Services restart frequently

#### **Diagnosis Steps**

```bash
# Check memory usage
docker stats

# Check specific container memory
docker-compose exec api cat /proc/meminfo

# Check for memory leaks
docker-compose logs api | grep -i "memory\|oom"
```

#### **Resolution Steps**

1. **Restart Services**

   ```bash
   # Restart all services to clear memory
   docker-compose restart
   ```

2. **Optimize Memory Usage**

   ```bash
   # Check for large files
   find /var/lib/docker -name "*.log" -size +100M
   
   # Clean up Docker
   docker system prune -a
   ```

3. **Adjust Resource Limits**

   ```yaml
   # Update docker-compose.yml
   services:
     api:
       deploy:
         resources:
           limits:
             memory: 1G
           reservations:
             memory: 512M
   ```

## 🔍 Medium Priority Issues

### **Slow API Response Times**

#### **Symptoms**

- API requests take longer than 5 seconds
- Users experience timeouts
- System appears sluggish

#### **Diagnosis Steps**

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3001/api/v1/health

# Check database query performance
docker-compose exec postgres psql -U brant_user -d brant_roofing -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

#### **Resolution Steps**

1. **Optimize Database Queries**

   ```sql
   -- Analyze slow queries
   EXPLAIN ANALYZE SELECT * FROM documents WHERE processing_status = 'completed';
   
   -- Update table statistics
   ANALYZE documents;
   ANALYZE measurements;
   ```

2. **Check Index Usage**

   ```sql
   -- Check index usage
   SELECT schemaname, tablename, attname, n_distinct, correlation 
   FROM pg_stats 
   WHERE tablename IN ('documents', 'measurements');
   ```

3. **Restart Services**

   ```bash
   # Restart to clear caches
   docker-compose restart api
   ```

### **File Upload Issues**

#### **Symptoms**

- File uploads fail or timeout
- "File too large" errors
- Upload progress gets stuck

#### **Diagnosis Steps**

```bash
# Check file size limits
grep -r "MAX_FILE_SIZE" app/

# Check disk space
df -h

# Check upload logs
docker-compose logs api | grep -i upload
```

#### **Resolution Steps**

1. **Check File Size Limits**

   ```python
   # Update settings in app/core/config.py
   MAX_FILE_SIZE: int = 209715200  # 200MB
   ```

2. **Check Disk Space**

   ```bash
   # Clean up old files
   find /tmp -name "*.tmp" -mtime +1 -delete
   
   # Check Docker volumes
   docker system df
   ```

3. **Restart Upload Service**

   ```bash
   # Restart API service
   docker-compose restart api
   ```

## 🔧 Low Priority Issues

### **Authentication Problems**

#### **Symptoms**

- Users cannot log in
- "Invalid credentials" errors
- Session timeouts

#### **Diagnosis Steps**

```bash
# Check authentication logs
docker-compose logs api | grep -i auth

# Check Redis session storage
docker-compose exec redis redis-cli keys "*session*"
```

#### **Resolution Steps**

1. **Check User Credentials**

   ```sql
   -- Verify user exists
   SELECT id, email, is_active FROM users WHERE email = 'user@example.com';
   ```

2. **Clear Session Cache**

   ```bash
   # Clear Redis sessions
   docker-compose exec redis redis-cli FLUSHDB
   ```

3. **Restart Authentication Service**

   ```bash
   # Restart API service
   docker-compose restart api
   ```

### **Email Notifications Not Working**

#### **Symptoms**

- Users don't receive email notifications
- Processing completion emails missing
- Password reset emails not sent

#### **Diagnosis Steps**

```bash
# Check email service logs
docker-compose logs api | grep -i email

# Test email configuration
docker-compose exec api python -c "
from app.core.config import settings
print('SMTP configured:', hasattr(settings, 'SMTP_HOST'))
"
```

#### **Resolution Steps**

1. **Check Email Configuration**

   ```env
   # Verify .env settings
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. **Test Email Service**

   ```python
   # Test email sending
   import smtplib
   from email.mime.text import MIMEText
   
   msg = MIMEText('Test email')
   msg['Subject'] = 'Test'
   msg['From'] = 'test@example.com'
   msg['To'] = 'recipient@example.com'
   
   smtp = smtplib.SMTP('smtp.gmail.com', 587)
   smtp.starttls()
   smtp.login('your-email@gmail.com', 'your-password')
   smtp.send_message(msg)
   smtp.quit()
   ```

## 📊 Performance Monitoring

### **System Health Checks**

#### **Automated Health Check Script**

```bash
#!/bin/bash
# health-check.sh

# API Health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/v1/health)
if [ $API_STATUS -ne 200 ]; then
    echo "❌ API Health Check Failed: HTTP $API_STATUS"
    exit 1
fi

# Database Health
DB_STATUS=$(docker-compose exec -T postgres psql -U brant_user -d brant_roofing -c "SELECT 1;" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Database Health Check Failed"
    exit 1
fi

# Redis Health
REDIS_STATUS=$(docker-compose exec -T redis redis-cli ping 2>/dev/null)
if [ "$REDIS_STATUS" != "PONG" ]; then
    echo "❌ Redis Health Check Failed"
    exit 1
fi

echo "✅ All health checks passed"
```

#### **Performance Metrics Collection**

```bash
#!/bin/bash
# collect-metrics.sh

# CPU Usage
CPU_USAGE=$(docker stats --no-stream --format "table {{.CPUPerc}}" api | tail -n 1)

# Memory Usage
MEMORY_USAGE=$(docker stats --no-stream --format "table {{.MemUsage}}" api | tail -n 1)

# Disk Usage
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}')

# Database Connections
DB_CONNECTIONS=$(docker-compose exec -T postgres psql -U brant_user -d brant_roofing -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tail -n 1)

echo "CPU: $CPU_USAGE"
echo "Memory: $MEMORY_USAGE"
echo "Disk: $DISK_USAGE"
echo "DB Connections: $DB_CONNECTIONS"
```

## 🆘 Emergency Procedures

### **Complete System Recovery**

#### **Step 1: Assess Damage**

```bash
# Check service status
docker-compose ps

# Check system resources
df -h
free -h
top
```

#### **Step 2: Stop All Services**

```bash
# Stop all services
docker-compose down

# Clean up containers
docker system prune -f
```

#### **Step 3: Restore from Backup**

```bash
# Restore database
docker-compose up -d postgres
sleep 30
docker-compose exec -T postgres psql -U brant_user -d brant_roofing < backup.sql

# Restore files
gsutil -m rsync -r gs://brant-backups/documents/ gs://brant-documents-prod/
```

#### **Step 4: Restart Services**

```bash
# Start services
docker-compose up -d

# Verify functionality
curl -f http://localhost:3001/api/v1/health
```

### **Data Recovery Procedures**

#### **Database Recovery**

```bash
# Stop API service
docker-compose stop api

# Restore database
docker-compose exec -T postgres psql -U brant_user -d brant_roofing < backup.sql

# Start API service
docker-compose start api
```

#### **File Recovery**

```bash
# Restore from Google Cloud Storage
gsutil -m rsync -r gs://brant-backups/documents/ gs://brant-documents-prod/

# Verify file integrity
gsutil ls gs://brant-documents-prod/ | wc -l
```

## 📞 Support Escalation

### **When to Escalate**

- **Critical Issues**: System down for more than 15 minutes
- **Data Loss**: Any data corruption or loss
- **Security Breach**: Suspected unauthorized access
- **Performance**: System unusable for more than 1 hour

### **Escalation Process**

1. **Document Issue**: Record problem details and steps taken
2. **Gather Information**: Collect logs, screenshots, and error messages
3. **Contact Support**: Use appropriate support channel
4. **Provide Context**: Include all relevant information
5. **Follow Up**: Track progress and provide updates

### **Support Contacts**

- **Level 1 Support**: <support@brant-roofing.com>
- **Level 2 Support**: <tech-support@brant-roofing.com>
- **Emergency Hotline**: 1-800-BRANT-HELP
- **On-call Engineer**: Available 24/7 for critical issues

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Document Owner**: Brant Roofing System Development Team

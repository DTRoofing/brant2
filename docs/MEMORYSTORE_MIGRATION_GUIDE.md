# Google Cloud Memorystore Migration Guide

This guide walks you through migrating your Brant Roofing System from local Redis to Google Cloud Memorystore.

## Overview

Google Cloud Memorystore is a fully managed Redis service that provides:
- **High availability** with automatic failover
- **Scalability** from small to large instances
- **Security** with VPC-native networking
- **Monitoring** integrated with Google Cloud
- **Backup and restore** capabilities

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Memorystore API** enabled
3. **Appropriate IAM permissions** for Memorystore
4. **VPC network** configured for Memorystore access

## Step 1: Enable Required APIs

```bash
# Enable Memorystore API
gcloud services enable redis.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled --filter="name:redis.googleapis.com"
```

## Step 2: Create Memorystore Instance

### Option A: Using gcloud CLI

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Create Memorystore instance
gcloud redis instances create brant-redis-instance \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic \
    --network=projects/$PROJECT_ID/global/networks/default
```

### Option B: Using Google Cloud Console

1. Go to [Memorystore for Redis](https://console.cloud.google.com/memorystore/redis)
2. Click "Create Instance"
3. Configure:
   - **Instance ID**: `brant-redis-instance`
   - **Region**: `us-central1`
   - **Tier**: `Basic` (for development) or `Standard` (for production)
   - **Memory size**: `1GB` (minimum)
   - **Redis version**: `Redis 7.0`
   - **Network**: `default` or your VPC

## Step 3: Configure Environment Variables

### For Development (.env)

```bash
# Copy the Memorystore template
cp .env.memorystore .env

# Edit .env with your values
nano .env
```

Update these values in `.env`:
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Memorystore Configuration
USE_MEMORYSTORE=true
MEMORYSTORE_REGION=us-central1
MEMORYSTORE_INSTANCE_NAME=brant-redis-instance

# Database Configuration (if using Cloud SQL)
DATABASE_URL=postgresql+asyncpg://user:password@YOUR_CLOUD_SQL_IP:5432/brant_roofing
```

### For Production (Cloud Run)

Set these environment variables in Cloud Run:

```bash
# Memorystore Configuration
USE_MEMORYSTORE=true
MEMORYSTORE_REGION=us-central1
MEMORYSTORE_INSTANCE_NAME=brant-redis-instance

# Google Cloud Project
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Other production settings...
```

## Step 4: Test the Migration

### Test Local Setup

```bash
# Start local Redis (for testing)
docker run -d --name redis-test -p 6379:6379 redis:7-alpine

# Test the migration script
python scripts/migrate_to_memorystore.py --test-only

# Clean up local Redis
docker stop redis-test && docker rm redis-test
```

### Test Memorystore Connection

```bash
# Test only Memorystore (requires GCP setup)
python scripts/migrate_to_memorystore.py --test-only
```

## Step 5: Deploy with Memorystore

### Using Docker Compose

```bash
# Set environment variables
export USE_MEMORYSTORE=true
export MEMORYSTORE_REGION=us-central1
export MEMORYSTORE_INSTANCE_NAME=brant-redis-instance
export GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Start services
docker-compose up -d
```

### Using Cloud Run

```bash
# Build and deploy
gcloud run deploy brant-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --set-env-vars="USE_MEMORYSTORE=true,MEMORYSTORE_REGION=us-central1,MEMORYSTORE_INSTANCE_NAME=brant-redis-instance,GOOGLE_CLOUD_PROJECT_ID=your-project-id"
```

## Step 6: Verify Migration

### Check Application Logs

```bash
# Check API logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=brant-api" --limit 50

# Look for these log messages:
# "Successfully connected to Memorystore Redis: brant-redis-instance"
# "Celery broker URL: redis://YOUR_MEMORYSTORE_IP:6379/0"
```

### Test Celery Workers

```bash
# Check Celery worker logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=brant-worker" --limit 50

# Test Celery connection
python -c "from app.workers.celery_app import celery_app; print(celery_app.broker_connection().ensure_connection())"
```

### Test Redis Caching

```bash
# Test Redis caching functionality
python -c "
from app.models.config_repository import redis_client
if redis_client:
    redis_client.set('test_key', 'test_value')
    print('Redis test:', redis_client.get('test_key'))
else:
    print('Redis client not available')
"
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```
   ERROR: Permission denied on resource project your-project-id
   ```
   **Solution**: Ensure your service account has the `Redis Admin` role or `Cloud Redis Admin` role.

2. **Network Access Issues**
   ```
   ERROR: Could not connect to Memorystore Redis
   ```
   **Solution**: Ensure your Cloud Run service is in the same VPC as Memorystore or has proper network access.

3. **Instance Not Found**
   ```
   ERROR: Memorystore instance brant-redis-instance not found
   ```
   **Solution**: Verify the instance name and region match your configuration.

### Debug Commands

```bash
# Check Memorystore instance status
gcloud redis instances describe brant-redis-instance --region=us-central1

# List all Memorystore instances
gcloud redis instances list

# Check IAM permissions
gcloud projects get-iam-policy your-project-id

# Test Redis connection directly
gcloud redis instances get-auth-string brant-redis-instance --region=us-central1
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_MEMORYSTORE` | Enable Memorystore instead of local Redis | `false` | No |
| `MEMORYSTORE_REGION` | Memorystore region | `us-central1` | Yes (if enabled) |
| `MEMORYSTORE_INSTANCE_NAME` | Memorystore instance name | `brant-redis-instance` | Yes (if enabled) |
| `GOOGLE_CLOUD_PROJECT_ID` | Google Cloud project ID | - | Yes |

### Redis Database Usage

- **Database 0**: Celery broker
- **Database 1**: Celery result backend  
- **Database 2**: Application caching

## Cost Considerations

### Memorystore Pricing (US Central)

- **Basic Tier**: $0.054/GB/hour
- **Standard Tier**: $0.054/GB/hour + additional features
- **Minimum**: 1GB instance

### Example Monthly Costs

- **1GB Basic**: ~$39/month
- **4GB Basic**: ~$156/month
- **8GB Basic**: ~$312/month

## Security Best Practices

1. **Use VPC-native networking** for Memorystore
2. **Enable AUTH** for production instances
3. **Use IAM roles** with least privilege
4. **Enable audit logging** for compliance
5. **Regular backup** of critical data

## Monitoring and Alerting

### Key Metrics to Monitor

- **Memory usage** (should stay below 80%)
- **Connection count** (monitor for connection leaks)
- **Command latency** (should be < 1ms)
- **Error rate** (should be < 0.1%)

### Recommended Alerts

```bash
# Memory usage alert
gcloud alpha monitoring policies create \
    --policy-from-file=memorystore-memory-alert.yaml

# Connection count alert  
gcloud alpha monitoring policies create \
    --policy-from-file=memorystore-connections-alert.yaml
```

## Rollback Plan

If you need to rollback to local Redis:

1. **Set environment variable**: `USE_MEMORYSTORE=false`
2. **Restart services**: `docker-compose restart`
3. **Verify local Redis**: Ensure local Redis is running
4. **Test functionality**: Run the migration script in test mode

## Support

For issues with this migration:

1. Check the [troubleshooting section](#troubleshooting)
2. Review [Google Cloud Memorystore documentation](https://cloud.google.com/memorystore/docs/redis)
3. Check application logs for specific error messages
4. Verify IAM permissions and network configuration

## Next Steps

After successful migration:

1. **Monitor performance** for the first week
2. **Set up alerts** for critical metrics
3. **Plan backup strategy** for production data
4. **Consider scaling** based on usage patterns
5. **Document any custom configurations** for your team

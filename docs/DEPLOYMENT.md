---
title: "Brant Roofing System - Deployment Guide"
version: "1.2.0"
last_updated: "2025-01-15"
owner: "DevOps Team"
audience: "DevOps Engineers, System Administrators"
status: "Active"
type: "Deployment Guide"
tags: ["deployment", "google-cloud", "production", "cicd"]
related_docs: ["setup_instructions.md", "api-documentation.md"]
review_date: "2025-04-15"
priority: "High"
---

# Brant Roofing System - Deployment Guide

This comprehensive guide details the process for deploying the Brant Roofing System to Google Cloud Platform using automated CI/CD pipeline with serverless technologies for scalable production environments.

## 📋 Table of Contents

- [Deployment Overview](#-deployment-overview)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Infrastructure Setup](#-infrastructure-setup)
- [CI/CD Configuration](#-cicd-configuration)
- [Deployment Process](#-deployment-process)
- [Post-Deployment Setup](#-post-deployment-setup)
- [Monitoring and Maintenance](#-monitoring-and-maintenance)
- [Troubleshooting](#-troubleshooting)

## 🚀 Deployment Overview

The Brant Roofing System deploys as a microservices architecture on Google Cloud Platform using:

- **Cloud Run** for containerized services
- **Cloud SQL** for PostgreSQL database
- **Memorystore** for Redis caching
- **Cloud Build** for CI/CD automation
- **Secret Manager** for secure configuration
- **Document AI** for PDF processing

### Deployment Environments

| Environment | Purpose | Branch | URL |
|-------------|---------|--------|-----|
| **Development** | Local development | `develop` | http://localhost:3000 |
| **Staging** | Pre-production testing | `staging` | https://staging.brant-roofing.com |
| **Production** | Live system | `main` | https://brant-roofing.com |

## 🏗️ System Architecture

The system deploys as three distinct Cloud Run services:

### Core Services

1. **`brant-frontend`**
   - Next.js user interface
   - Public-facing web application
   - Serves static assets and dynamic pages

2. **`brant-api`**
   - FastAPI backend service
   - Business logic and API endpoints
   - Database and external service integration

3. **`brant-worker`**
   - Celery background worker
   - Asynchronous PDF processing
   - Document AI integration

### Infrastructure Components

- **Cloud SQL PostgreSQL**: Primary data storage
- **Memorystore Redis**: Caching and task queue
- **VPC Connector**: Secure service communication
- **Load Balancer**: HTTPS termination and routing
- **Artifact Registry**: Container image storage

## 📋 Prerequisites

### Required Google Cloud APIs

Enable the following APIs in your GCP project:

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  sql-component.googleapis.com \
  documentai.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com
```

### Required Tools

- **Google Cloud SDK** 400.0.0+
- **Docker** 20.0.0+
- **Git** 2.30.0+
- **Node.js** 18.0.0+ (for local development)

### Access Requirements

- GCP Project with billing enabled
- Editor/Admin permissions on target project
- GitHub/GitLab repository access for CI/CD

## 🔧 Infrastructure Setup

### Step 1: Service Account Creation

Create a dedicated service account with required permissions:

```bash
# Create service account
gcloud iam service-accounts create brant-app-sa \
  --display-name="Brant Roofing System Service Account"

# Assign required roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:brant-app-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:brant-app-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:brant-app-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 2: Database Infrastructure

#### Cloud SQL PostgreSQL Instance

```bash
# Create Cloud SQL instance
gcloud sql instances create brant-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --enable-ip-alias \
  --no-assign-ip

# Create database and user
gcloud sql databases create brant_roofing --instance=brant-postgres
gcloud sql users create brant_user --instance=brant-postgres --password=SECURE_PASSWORD
```

#### Memorystore Redis Instance

```bash
# Create Redis instance
gcloud redis instances create brant-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x
```

### Step 3: Networking Setup

#### VPC Connector

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create brant-connector \
  --region=us-central1 \
  --subnet=default \
  --subnet-project=PROJECT_ID \
  --min-instances=2 \
  --max-instances=3
```

### Step 4: Container Registry

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create brant-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Brant Roofing System container images"
```

### Step 5: Secret Configuration

Configure required secrets in Google Secret Manager:

```bash
# Database connection
gcloud secrets create DATABASE_URL --data-file=-
# Enter: postgresql://brant_user:PASSWORD@PRIVATE_IP/brant_roofing

# Redis connection
gcloud secrets create REDIS_URL --data-file=-
# Enter: redis://REDIS_PRIVATE_IP:6379/0

# Application secrets
gcloud secrets create SECRET_KEY --data-file=-
gcloud secrets create ANTHROPIC_API_KEY --data-file=-
gcloud secrets create DOCUMENT_AI_PROCESSOR_ID --data-file=-
```

## ⚙️ CI/CD Configuration

### Cloud Build Trigger Setup

1. **Navigate to Cloud Build > Triggers** in GCP Console
2. **Create new trigger** with these settings:

| Setting | Value |
|---------|-------|
| **Name** | Deploy Brant Roofing Production |
| **Event** | Push to branch |
| **Source** | Connect your repository |
| **Branch** | `^main$` |
| **Configuration** | Cloud Build configuration file |
| **Location** | `/cloudbuild.yaml` |

3. **Configure Substitution Variables**:

```yaml
_REGION: us-central1
_SERVICE_ACCOUNT: brant-app-sa@PROJECT_ID.iam.gserviceaccount.com
_VPC_CONNECTOR: brant-connector
_API_URL: https://api.brant-roofing.com  # Update after Load Balancer setup
```

### Manual Deployment

For manual deployments or testing:

```bash
# Deploy from local machine
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_SERVICE_ACCOUNT=brant-app-sa@PROJECT_ID.iam.gserviceaccount.com

# Monitor deployment
gcloud builds list --limit=5
```

## 🚀 Deployment Process

### Automated Deployment Pipeline

The CI/CD pipeline executes these stages:

1. **Code Checkout and Testing**
   - Source code retrieval
   - Unit and integration tests
   - Security vulnerability scans

2. **Container Image Building**
   - Multi-stage Docker builds
   - Image optimization and security scanning
   - Push to Artifact Registry

3. **Service Deployment**
   - Deploy API service to Cloud Run
   - Deploy Frontend service to Cloud Run
   - Deploy Worker service to Cloud Run

4. **Database Migration**
   - Automated schema migrations
   - Data migration validation
   - Rollback preparation

5. **Health Checks and Validation**
   - Service health verification
   - Integration testing
   - Performance validation

### Deployment Monitoring

Monitor deployment progress:

```bash
# View build logs
gcloud builds log BUILD_ID --stream

# Check service status
gcloud run services list --platform=managed

# View service logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50
```

## 🌐 Post-Deployment Setup

### Load Balancer Configuration

Set up HTTPS Load Balancer for production traffic:

```bash
# Create static IP
gcloud compute addresses create brant-lb-ip --global

# Create SSL certificate
gcloud compute ssl-certificates create brant-ssl-cert \
  --domains=brant-roofing.com,api.brant-roofing.com \
  --global

# Create Network Endpoint Group
gcloud compute network-endpoint-groups create brant-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=brant-api
```

### DNS Configuration

Configure your domain DNS:

```text
# A Records
brant-roofing.com     -> Load Balancer IP
api.brant-roofing.com -> Load Balancer IP

# CNAME Records
www.brant-roofing.com -> brant-roofing.com
```

### SSL Certificate Setup

```bash
# Verify certificate status
gcloud compute ssl-certificates list

# Check certificate provisioning
gcloud compute ssl-certificates describe brant-ssl-cert --global
```

## 📊 Monitoring and Maintenance

### Health Monitoring

#### Service Health Checks

```bash
# API health check
curl -f https://api.brant-roofing.com/api/v1/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

#### Automated Monitoring

Set up monitoring alerts:

```bash
# Create uptime check
gcloud alpha monitoring uptime create-uptime-check-config \
  --config-from-file=monitoring-config.yaml
```

### Log Analysis

#### Centralized Logging

```bash
# View application logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=brant-api" \
  --limit=100 \
  --format="table(timestamp,resource.labels.revision_name,textPayload)"

# View error logs only
gcloud logs read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50
```

#### Log Aggregation

Key log sources to monitor:

- **Application Logs**: Business logic errors
- **Access Logs**: HTTP request patterns
- **System Logs**: Infrastructure issues
- **Security Logs**: Authentication failures

### Performance Monitoring

#### Metrics Dashboard

Monitor these key metrics:

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Response Time** | < 200ms P95 | Scale up if exceeded |
| **Error Rate** | < 1% | Alert on spike |
| **CPU Utilization** | < 70% | Scale up containers |
| **Memory Usage** | < 80% | Optimize or scale |

#### Database Performance

```bash
# Monitor database connections
gcloud sql operations list --instance=brant-postgres --limit=10

# Check database metrics
gcloud logging read "resource.type=cloudsql_database" --limit=20
```

## 🚨 Troubleshooting

### Common Issues

#### Deployment Failures

**Issue**: Cloud Build timeout

```bash
# Increase build timeout
gcloud builds submit --timeout=3600s --config cloudbuild.yaml
```

**Issue**: Service not receiving traffic

```bash
# Check service allocation
gcloud run services describe brant-api --region=us-central1

# Verify traffic allocation
gcloud run services update-traffic brant-api --to-latest --region=us-central1
```

#### Database Connection Issues

**Issue**: Connection pool exhaustion

```bash
# Scale API service
gcloud run services update brant-api \
  --region=us-central1 \
  --max-instances=10 \
  --concurrency=80
```

#### Performance Issues

**Issue**: High latency

1. Check service metrics in GCP Console
2. Analyze log patterns for bottlenecks
3. Scale services if needed
4. Optimize database queries

### Emergency Procedures

#### Rollback Deployment

```bash
# List recent revisions
gcloud run revisions list --service=brant-api --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic brant-api \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

#### Service Recovery

```bash
# Restart service
gcloud run services replace-traffic brant-api --to-latest --region=us-central1

# Check service health
gcloud run services describe brant-api --region=us-central1 --format="get(status.conditions)"
```

## 📚 Additional Resources

### Documentation Links

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Configuration](https://cloud.google.com/build/docs/build-config-file-schema)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)

### Support Contacts

| Issue Type | Contact | Response SLA |
|------------|---------|--------------|
| **Critical Production** | DevOps Team | 15 minutes |
| **General Deployment** | Development Team | 2 hours |
| **Infrastructure** | Platform Team | 4 hours |

---

**Next Review**: April 15, 2025  
**Document Owner**: DevOps Team  
**Last Updated**: January 15, 2025
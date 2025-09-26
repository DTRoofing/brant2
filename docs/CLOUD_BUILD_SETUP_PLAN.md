# Cloud Build Setup Plan for Brant Roofing System

## Overview
This plan outlines the complete setup of Google Cloud Build for automated CI/CD deployment of the Brant Roofing System. The current deployment seems to have issues, and Cloud Build will provide a robust, automated solution.

## Current State Analysis

### ✅ What's Already Configured
- **Cloud Build YAML**: Both root and deployment directory have `cloudbuild.yaml` files
- **Terraform Infrastructure**: Complete GCP infrastructure setup in `deployment/GCP_INFRASTRUCTURE.tf`
- **Docker Configuration**: Backend, worker, and frontend Dockerfiles are ready
- **Service Architecture**: Well-defined microservices (API, Worker, Frontend)
- **Database Migrations**: Automated migration job configuration

### ❌ Current Issues
- Deployment pipeline not working
- No active Cloud Build triggers
- Missing GCP project configuration
- Service account permissions may be incomplete

## Benefits of Cloud Build for This App

### 🚀 **High Value Benefits**
1. **Automated Deployments**: Push to main branch → automatic deployment
2. **Quality Gates**: Automated testing and vulnerability scanning
3. **Consistent Environments**: Reproducible builds across dev/staging/prod
4. **Rollback Capability**: Easy rollback to previous versions
5. **Cost Optimization**: Pay-per-use model, no idle costs
6. **Security**: Built-in vulnerability scanning and secret management

### 📊 **Specific to Brant App**
- **Multi-Service Deployment**: Handles API, Worker, and Frontend simultaneously
- **Database Migrations**: Automated Alembic migrations before deployment
- **Image Caching**: Kaniko caching reduces build times
- **VPC Integration**: Proper networking for Cloud SQL and Redis access

## Implementation Plan

### Phase 1: Prerequisites Setup (30 minutes)

#### 1.1 GCP Project Configuration
```bash
# Set your project ID
export PROJECT_ID="brant-roofing-system-2025"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable documentai.googleapis.com
gcloud services enable vpcaccess.googleapis.com
gcloud services enable redis.googleapis.com
```

#### 1.2 Terraform Infrastructure Deployment
```bash
cd deployment/
terraform init
terraform plan -var="project_id=$PROJECT_ID"
terraform apply -var="project_id=$PROJECT_ID"
```

### Phase 2: Artifact Registry Setup (15 minutes)

#### 2.1 Create Repository
```bash
gcloud artifacts repositories create brant-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Brant Roofing System Docker Repository"
```

#### 2.2 Configure Docker Authentication
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Phase 3: Service Account Configuration (20 minutes)

#### 3.1 Create Cloud Build Service Account
```bash
gcloud iam service-accounts create brant-cloudbuild \
    --display-name="Brant Cloud Build Service Account"
```

#### 3.2 Grant Required Permissions
```bash
# Cloud Build permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

# Cloud Run deployment permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Artifact Registry permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Phase 4: Cloud Build Trigger Setup (25 minutes)

#### 4.1 Create Build Trigger
```bash
gcloud builds triggers create github \
    --repo-name=brant2 \
    --repo-owner=DTRoofing \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --service-account="brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com"
```

#### 4.2 Configure Substitution Variables
Set these in the Cloud Build trigger settings:

| Variable | Value | Description |
|----------|-------|-------------|
| `_REGION` | `us-central1` | GCP region for deployment |
| `_GCR_HOSTNAME` | `us-central1-docker.pkg.dev` | Artifact Registry hostname |
| `_REPO_NAME` | `brant-repo` | Artifact Registry repository name |
| `_SERVICE_NAME_API` | `brant-api` | Cloud Run service name for API |
| `_SERVICE_NAME_WORKER` | `brant-worker` | Cloud Run service name for Worker |
| `_SERVICE_NAME_FRONTEND` | `brant-frontend` | Cloud Run service name for Frontend |
| `_SERVICE_ACCOUNT` | `brant-system-service@$PROJECT_ID.iam.gserviceaccount.com` | Runtime service account |
| `_VPC_CONNECTOR` | `brant-vpc-connector` | VPC connector name |
| `_API_URL` | `https://api.dtrooftools.com` | Public API URL (dtrooftools.com domain) |

### Phase 5: Secrets Configuration (15 minutes)

#### 5.1 Update Secret Manager Values
```bash
# Update each secret with real values
gcloud secrets versions add brant-anthropic-api-key --data-file=- <<< "your-anthropic-key"
gcloud secrets versions add brant-secret-key --data-file=- <<< "$(openssl rand -hex 32)"
gcloud secrets versions add brant-document-ai-processor-id --data-file=- <<< "your-processor-id"
gcloud secrets versions add brant-document-ai-location --data-file=- <<< "us"
```

### Phase 6: Testing and Validation (20 minutes)

#### 6.1 Test Build Locally
```bash
# Test the build configuration
gcloud builds submit --config=cloudbuild.yaml .
```

#### 6.2 Monitor First Deployment
```bash
# Watch the build logs
gcloud builds log --stream

# Check Cloud Run services
gcloud run services list --region=us-central1
```

## Expected Outcomes

### 🎯 **Immediate Benefits**
- **Automated Deployments**: Every push to main triggers deployment
- **Quality Assurance**: Automated testing and security scanning
- **Consistent Builds**: Reproducible deployment process
- **Faster Deployments**: Cached builds and parallel processing

### 📈 **Long-term Benefits**
- **Zero-downtime Deployments**: Rolling updates with health checks
- **Easy Rollbacks**: One-click rollback to previous versions
- **Cost Optimization**: Pay only for build time used
- **Security**: Automated vulnerability scanning and secret management

## Monitoring and Maintenance

### 📊 **Monitoring Setup**
1. **Cloud Build Logs**: Monitor build success/failure rates
2. **Cloud Run Metrics**: Track service performance and errors
3. **Cost Monitoring**: Track build and deployment costs
4. **Security Alerts**: Monitor for security vulnerabilities

### 🔧 **Maintenance Tasks**
- **Weekly**: Review build logs and performance metrics
- **Monthly**: Update base images and dependencies
- **Quarterly**: Review and optimize build configuration

## Troubleshooting Common Issues

### 🚨 **Build Failures**
- Check service account permissions
- Verify Artifact Registry access
- Review substitution variables

### 🔧 **Deployment Issues**
- Ensure VPC connector is properly configured
- Check Cloud SQL and Redis connectivity
- Verify secret values are correctly set

## Cost Estimation

### 💰 **Expected Monthly Costs**
- **Cloud Build**: ~$10-20 (based on 50 builds/month)
- **Artifact Registry**: ~$5-10 (storage costs)
- **Cloud Run**: Existing costs (no change)
- **Total Additional**: ~$15-30/month

## Next Steps

1. **Execute Phase 1**: Set up GCP project and APIs
2. **Deploy Infrastructure**: Run Terraform configuration
3. **Configure Secrets**: Set up all required secrets
4. **Create Trigger**: Set up Cloud Build trigger
5. **Test Pipeline**: Push a test commit to trigger build
6. **Monitor**: Watch first deployment and verify all services

## Success Criteria

- ✅ Cloud Build trigger created and active
- ✅ All three services (API, Worker, Frontend) deploy successfully
- ✅ Database migrations run automatically
- ✅ Health checks pass for all services
- ✅ Build time under 10 minutes
- ✅ Zero manual intervention required for deployments

---

**Ready to proceed?** Start with Phase 1 and work through each phase systematically. Each phase builds on the previous one, so follow the order for best results.

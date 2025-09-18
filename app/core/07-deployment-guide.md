> **[DEPRECATED]** This document describes a legacy Kubernetes-based deployment. The current, recommended deployment method uses Google Cloud Run and is automated via the `cloudbuild.yaml` pipeline. Please refer to the main `GCP_DEPLOYMENT.md` file for the correct instructions.
> ---

# Brant Roofing System - Deployment Guide

## 🚀 Deployment Overview

This guide covers the complete deployment process for the Brant Roofing System, including development, staging, and production environments.

## 📋 Prerequisites

### **System Requirements**
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Docker**: Version 20.10+ with Docker Compose
- **Kubernetes**: Version 1.21+ (for production)
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 50GB+ available disk space
- **Network**: Stable internet connection for cloud services

### **Required Services**
- **Google Cloud Platform**: Active project with billing enabled
- **PostgreSQL**: Version 13+ (managed or self-hosted)
- **Redis**: Version 6+ (managed or self-hosted)
- **Domain**: Valid domain name for production deployment

## 🏗️ Environment Setup

### **Development Environment**

#### 1. Clone Repository
```bash
git clone https://github.com/brant-roofing/system.git
cd brant-roofing-system
```

#### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

#### 3. Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/brant_dev
POSTGRES_DB=brant_dev
POSTGRES_USER=brant_user
POSTGRES_PASSWORD=secure_password

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key-here
DEBUG=true
PORT=3001

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=brant-documents-dev
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
ANTHROPIC_API_KEY=your-anthropic-key
```

#### 4. Start Development Environment
```bash
# Start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### **Staging Environment**

#### 1. Create Staging Configuration
```bash
# Create staging environment file
cp .env .env.staging

# Update staging-specific variables
DATABASE_URL=postgresql://user:password@staging-db:5432/brant_staging
DEBUG=false
GOOGLE_CLOUD_STORAGE_BUCKET=brant-documents-staging
```

#### 2. Deploy to Staging
```bash
# Build and deploy
docker-compose -f docker-compose.staging.yml up --build -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Run health checks
curl http://staging-api.brant-roofing.com/api/v1/health
```

### **Production Environment**

#### 1. Kubernetes Deployment

##### Create Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: brant-roofing
  labels:
    name: brant-roofing
```

##### Database Secret
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: brant-secrets
  namespace: brant-roofing
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
  anthropic-api-key: <base64-encoded-api-key>
```

##### API Deployment
```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brant-api
  namespace: brant-roofing
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brant-api
  template:
    metadata:
      labels:
        app: brant-api
    spec:
      containers:
      - name: api
        image: brant-roofing:__IMAGE_TAG__ # This placeholder should be replaced by the CI/CD pipeline
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: brant-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: brant-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

##### Service Configuration
```yaml
# k8s/api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: brant-api-service
  namespace: brant-roofing
spec:
  selector:
    app: brant-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

##### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: brant-ingress
  namespace: brant-roofing
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.brant-roofing.com
    secretName: brant-tls
  rules:
  - host: api.brant-roofing.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: brant-api-service
            port:
              number: 80
```

#### 2. Deploy to Production
```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n brant-roofing
kubectl get services -n brant-roofing
kubectl get ingress -n brant-roofing
```

## 🔧 Database Setup

### **PostgreSQL Configuration**

#### 1. Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE brant_roofing;

-- Create user
CREATE USER brant_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE brant_roofing TO brant_user;
```

#### 2. Run Migrations
```bash
# Install Alembic
pip install alembic

# Initialize migrations (if not already done)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### 3. Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX CONCURRENTLY ix_document_status ON documents(processing_status);
CREATE INDEX CONCURRENTLY ix_document_created ON documents(created_at);
CREATE INDEX CONCURRENTLY ix_measurement_document ON measurements(document_id);

-- Configure connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

## 🔒 Security Configuration

### **SSL/TLS Setup**

#### 1. Generate SSL Certificates
```bash
# Using Let's Encrypt
certbot certonly --standalone -d api.brant-roofing.com

# Or using self-signed certificates for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

#### 2. Configure Nginx
```nginx
# /etc/nginx/sites-available/brant-api
server {
    listen 443 ssl http2;
    server_name api.brant-roofing.com;
    
    ssl_certificate /etc/letsencrypt/live/api.brant-roofing.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.brant-roofing.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Firewall Configuration**
```bash
# UFW configuration
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5432/tcp  # PostgreSQL (if local)
ufw enable
```

## 📊 Monitoring Setup

### **Prometheus Configuration**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'brant-api'
    static_configs:
      - targets: ['api:3001']
    metrics_path: /metrics
    scrape_interval: 5s
```

### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Brant Roofing System",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## 🧪 Health Checks

### **Application Health Check**
```bash
#!/bin/bash
# health-check.sh

API_URL="http://localhost:3001/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "API is healthy"
    exit 0
else
    echo "API is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### **Database Health Check**
```sql
-- Check database connectivity
SELECT 1;

-- Check table existence
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'documents';

-- Check recent activity
SELECT COUNT(*) FROM documents WHERE created_at > NOW() - INTERVAL '1 hour';
```

## 🔄 CI/CD Pipeline

### **GitHub Actions Workflow**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t brant-roofing:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push brant-roofing:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/brant-api api=brant-roofing:${{ github.sha }} -n brant-roofing
        kubectl rollout status deployment/brant-api -n brant-roofing
```

## 🚨 Troubleshooting

### **Common Issues**

#### 1. Database Connection Failed
```bash
# Check database status
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec api python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### 2. Google Cloud Authentication Failed
```bash
# Check credentials
gcloud auth list

# Set application default credentials
gcloud auth application-default login

# Test GCS access
gsutil ls gs://your-bucket-name
```

#### 3. Celery Workers Not Processing
```bash
# Check worker status
docker-compose exec worker celery -A app.workers.celery_app inspect active

# Check Redis connection
docker-compose exec worker celery -A app.workers.celery_app inspect stats

# Restart workers
docker-compose restart worker
```

### **Log Analysis**
```bash
# View API logs
docker-compose logs -f api

# View worker logs
docker-compose logs -f worker

# View database logs
docker-compose logs -f postgres

# Search for errors
docker-compose logs api | grep ERROR
```

## 📈 Performance Optimization

### **Database Optimization**
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM documents WHERE processing_status = 'completed';

-- Update table statistics
ANALYZE documents;
ANALYZE measurements;

-- Vacuum tables
VACUUM ANALYZE documents;
```

### **Application Optimization**
```python
# Configure connection pooling
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Document Owner**: Brant Roofing System Development Team

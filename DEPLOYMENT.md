# BRANT Roofing System - Production Deployment Guide

## Prerequisites

1. **Server Requirements**
   - Ubuntu 20.04 LTS or later (or any Linux distribution with Docker support)
   - Minimum 4GB RAM, 2 CPU cores
   - 20GB+ available storage
   - Docker and Docker Compose installed
   - Open ports: 3001 (API), 5432 (PostgreSQL), 6379 (Redis)

2. **Required Files**
   - `.env` file with production configurations
   - `google-credentials.json` from Google Cloud Console
   - All application source code

## Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repository

```bash
# Clone the repository (or upload via SFTP)
git clone [your-repository-url] brant
cd brant
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables for production
nano .env
```

**Important production settings to update:**
- `DATABASE_URL` - Use a secure PostgreSQL instance
- `ANTHROPIC_API_KEY` - Your Claude API key
- `GOOGLE_CLOUD_PROJECT_ID` - Your Google Cloud project
- `SECRET_KEY` - Generate a new secure key
- `DEBUG=false` - Disable debug mode
- `NODE_ENV=production`

### 4. Upload Google Credentials

```bash
# Upload your service account JSON file
# Make sure it's named google-credentials.json
scp google-credentials.json user@server:/path/to/brant/
```

### 5. Build and Start Services

```bash
# Build containers
docker-compose build

# Start services in detached mode
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Verify Deployment

```bash
# Check API health
curl http://localhost:3001/api/v1/health

# Run container health check
docker-compose exec api python /app/scripts/container_healthcheck.py

# Test PDF processing
curl -X POST http://localhost:3001/api/v1/uploads \
  -F "file=@sample.pdf" \
  -F "metadata={\"type\":\"roofing_estimate\"}"
```

## Container Configuration

### Services Overview

1. **API Container** (`api`)
   - FastAPI application
   - Port: 3001
   - Handles HTTP requests and file uploads

2. **Worker Container** (`worker`)
   - Celery worker for async processing
   - Processes PDFs in background
   - Runs OCR and AI analysis

3. **Database** (`db`)
   - PostgreSQL 15
   - Port: 5432
   - Persistent volume for data

4. **Redis** (`redis`)
   - Message broker for Celery
   - Port: 6379
   - Task queue and caching

5. **Flower** (`flower`)
   - Celery monitoring dashboard
   - Port: 5555
   - Real-time task monitoring

### Environment Variables

All containers share environment variables through `.env` file:

```env
# Database (container networking)
DATABASE_URL=postgresql://ADMIN:password@db:5432/postgres?sslmode=disable

# Redis (container networking)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# File paths (container paths)
GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
UPLOAD_DIR=/app/uploads
LOG_FILE=/app/logs/backend.log
```

### Volume Mounts

- `./app` → `/app/app` - Application code
- `./uploads` → `/app/uploads` - PDF uploads
- `./logs` → `/app/logs` - Application logs
- `./google-credentials.json` → `/app/google-credentials.json` - Google credentials

## Monitoring and Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

### Access Flower Dashboard

Open browser to `http://your-server:5555` to monitor Celery tasks.

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U ADMIN postgres > backup.sql

# Restore database
docker-compose exec -T db psql -U ADMIN postgres < backup.sql
```

### Update Application

```bash
# Stop services
docker-compose down

# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Start services
docker-compose up -d
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs api

# Check disk space
df -h

# Check memory
free -m
```

### PDF processing fails

```bash
# Check worker logs
docker-compose logs worker

# Verify Poppler installation
docker-compose exec api which pdftoppm

# Verify Tesseract
docker-compose exec api tesseract --version
```

### Google APIs not working

```bash
# Check credentials file
docker-compose exec api ls -la /app/google-credentials.json

# Test Google connection
docker-compose exec api python -c "from app.services.google_services import google_service; print(google_service.credentials is not None)"
```

### Database connection issues

```bash
# Test database connection
docker-compose exec db psql -U ADMIN -d postgres -c "SELECT 1"

# Check database logs
docker-compose logs db
```

## Security Recommendations

1. **Use HTTPS** - Set up SSL/TLS with Let's Encrypt
2. **Firewall** - Only expose necessary ports
3. **Secrets Management** - Use Docker secrets for sensitive data
4. **Regular Updates** - Keep Docker and dependencies updated
5. **Monitoring** - Set up logging and alerting
6. **Backups** - Regular database and file backups

## Performance Optimization

1. **Scale Workers** - Increase Celery concurrency for more PDFs
2. **Database Pool** - Adjust connection pool size in `.env`
3. **Redis Memory** - Configure Redis max memory policy
4. **Resource Limits** - Set Docker resource constraints

## Support

For issues or questions:
1. Check container logs: `docker-compose logs`
2. Run health check: `docker-compose exec api python /app/scripts/container_healthcheck.py`
3. Review this guide and troubleshooting section
4. Check application documentation
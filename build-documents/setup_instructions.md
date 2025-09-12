# 🏠 Brant Roofing System - Complete Setup Instructions

## 📋 Step-by-Step Setup Guide

### **Step 1: Move Your Service Account Key** 🔐
```bash
# Create secrets directory
mkdir -p secrets

# Move your Google Cloud service account key to the secrets folder
mv brant-roofing-system-2025-a5b8920b36d5.json secrets/
```

### **Step 2: Replace Your .env File** ⚙️
Replace your current `.env` file with the enhanced version from the artifacts above.

### **Step 3: Create All Required Files** 📁
Create these files in your project root directory using the artifacts provided:

**Root Directory Files:**
- `.env` (Enhanced version - Artifact #2)
- `docker-compose.yml` (Artifact #3) 
- `pyproject.toml` (Artifact #4)
- `backend.Dockerfile` (Artifact #5)
- `worker.Dockerfile` (Artifact #6)
- `quick-start.sh` (Artifact #8)
- `Makefile` (Artifact #9)
- `.gitignore` (Artifact #10)

**Application Code:**
- `app/main.py` (Artifact #7)
- `app/core/config.py` (Artifact #8)

### **Step 4: Run Quick Start** 🚀
```bash
# Make script executable and run setup
chmod +x quick-start.sh
./quick-start.sh
```

**OR use the Makefile:**
```bash
make setup
```

### **Step 5: Verify Everything is Working** ✅
```bash
# Check service status
make status

# Check health
make health

# View logs if needed
make logs
```

---

## 🎯 What This Setup Provides

### **✅ Complete Backend Infrastructure**
- FastAPI application with Google Cloud Document AI integration
- Celery workers for background PDF processing  
- PostgreSQL database with migrations
- Redis for caching and task queues
- Production-ready Docker containers

### **✅ AI-Powered Processing Pipeline**
- Google Document AI for OCR and text extraction
- Anthropic Claude for intelligent analysis
- Computer vision for measurement extraction
- Confidence scoring and validation

### **✅ Developer Experience**
- Hot reloading for development
- Comprehensive logging and monitoring
- Health checks for all services
- Task monitoring with Celery Flower
- Automated testing framework

### **✅ Production Ready**
- Secure configuration management
- Error handling and retry logic
- Database migrations and backups
- CI/CD with Google Cloud Build
- Infrastructure as Code with Terraform

---

## 🌐 Available Services After Setup

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:3001 | Main application API |
| **API Docs** | http://localhost:3001/docs | Interactive API documentation |
| **Health Check** | http://localhost:3001/health | Service health status |
| **Celery Flower** | http://localhost:5555 | Task monitoring dashboard |
| **Database** | localhost:5432 | PostgreSQL database |
| **Redis** | localhost:6379 | Cache and message broker |

---

## 🛠️ Essential Commands

### **Daily Development**
```bash
make dev          # Start development environment
make logs         # View all logs
make health       # Check service health
make stop         # Stop all services
```

### **Database Operations**
```bash
make migrate      # Run database migrations
make db-shell     # Connect to database
make backup       # Create database backup
```

### **Testing & Quality**
```bash
make test         # Run all tests
make test-api     # Run API tests only
make test-coverage # Run tests with coverage
```

### **Maintenance**
```bash
make clean        # Clean up containers
make restart      # Restart all services
make build        # Rebuild containers
```

---

## 🔧 Customization Points

### **Environment Variables** (`.env`)
- Update `ANTHROPIC_API_KEY` with your current key
- Modify `CORS_ORIGINS` for your frontend URLs
- Adjust file processing limits and thresholds
- Configure company-specific settings

### **Business Logic** (`app/services/`)
- Customize measurement extraction algorithms
- Add industry-specific estimation rules
- Implement custom pricing strategies
- Add validation logic for your market

### **API Endpoints** (`app/api/v1/endpoints/`)
- Add custom endpoints for your workflow
- Implement client-specific features
- Add reporting and analytics endpoints

---

## 🚨 Important Notes

### **Security** 🔐
- Never commit `.env` files or service account keys to version control
- Generate strong secrets for production deployment
- Use HTTPS in production with proper SSL certificates
- Implement proper authentication for production use

### **File Paths** 📁
- Service account key MUST be in `secrets/` directory for Docker
- Upload files go to `uploads/` directory
- Processed files stored in `processed/` directory
- Logs written to `logs/` directory

### **Resource Requirements** 💻
- Minimum 4GB RAM for development
- 8GB+ RAM recommended for production
- SSD storage for better performance
- Stable internet for Google Cloud services

---

## 🆘 Troubleshooting

### **Common Issues**

**Services won't start:**
```bash
# Check Docker is running
docker info

# View detailed logs
make logs

# Rebuild containers
make build
```

**Database connection errors:**
```bash
# Check database is ready
make health

# Reset database if needed
make db-reset
```

**Google Cloud errors:**
```bash
# Verify service account key location
ls -la secrets/

# Check credentials in container
make shell-api
ls -la /secrets/
```

**File upload issues:**
```bash
# Check upload directory permissions
ls -la uploads/

# Test with small file first
make upload-test
```

---

## 🎉 Success!

Once setup is complete, you'll have a fully functional AI-powered roofing estimation system that can:

1. **Process PDF blueprints** up to 100MB
2. **Extract measurements** using Google Document AI and OCR
3. **Analyze drawings** with Anthropic Claude
4. **Generate estimates** with customizable pricing
5. **Track projects** with full audit trails
6. **Scale automatically** with cloud infrastructure

Your system is now ready to revolutionize roofing estimation workflows! 🏠✨
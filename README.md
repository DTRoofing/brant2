# 🏠 Brant Roofing System

AI-powered roofing estimation system using Google Document AI and Anthropic Claude.

## 🚀 Quick Start

1. **Prerequisites**:
   - Docker and Docker Compose
   - Google Cloud service account key

2. **Setup**:

   ```bash
   # Place your service account key
   cp your-service-account.json \
     secrets/brant-roofing-system-2025-a5b8920b36d5.json
   
   # Start the system
   docker-compose up --build
   ```

3. **Access**:
   - API: <http://localhost:3001>
   - API Docs: <http://localhost:3001/docs>
   - Health Check: <http://localhost:3001/api/v1/health>

## 📁 Project Structure

```text
brant/
├── app/                    # Main FastAPI application
│   ├── api/               # API routes and endpoints
│   ├── core/              # Configuration and database
│   ├── models/            # SQLAlchemy models
│   ├── services/          # Business logic services
│   └── workers/           # Background task workers
├── frontend_ux/           # Next.js frontend application
├── deployment/            # Deployment configurations
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── archive/               # Archived files and test results
└── secrets/               # Service account keys
```

## 🛠️ Development

### Backend (FastAPI)

- **Location**: `app/`
- **Port**: 3001
- **Database**: PostgreSQL
- **Features**: Document processing, AI integration, file uploads

### Frontend (Next.js)

- **Location**: `frontend_ux/`
- **Port**: 3000
- **Features**: Modern UI, file upload, dashboard

## 📚 Documentation

- [API Documentation](http://localhost:3001/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Strategy](docs/INTEGRATION_TESTING_STRATEGY.md)

## 🔧 Configuration

Environment variables are configured in `.env`:

- Google Cloud credentials
- Database connection
- API keys
- Service settings

## 🧪 Testing

```bash
# Run tests
make test

# Run specific test suites
make test-unit
make test-integration
make test-e2e
```

## 📦 Deployment

```bash
# Deploy to GCP
make deploy-gcp

# Deploy locally
docker-compose up --build
```

## 🤝 Contributing

1. Follow the API validation standards in `.cursor/rules/`
2. Write tests for new features
3. Update documentation
4. Follow the established project structure

## 📄 License

Private project - All rights reserved

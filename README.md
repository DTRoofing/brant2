# 🏠 Brant Roofing System

AI-powered roofing estimation system using Google Document AI and Anthropic Claude.

## 🚀 Quick Start (Local Development)

This project uses a `Makefile` for easy setup and management.

1. **Prerequisites**:
   - Docker and Docker Compose must be running.
   - A Google Cloud service account key file (`.json`).
   - A `.env` file configured for your local environment.

2. **Setup**:
   - Google Cloud authentication is handled via Workload Identity in production.
   - No credentials files are needed for production deployment.
   - Run the automated setup script:

   ```bash
   make setup
   ```
   This will check prerequisites, build containers, and start the services.

3. **Access**:
   - API: <http://localhost:3001>
   - API Docs: <http://localhost:3001/docs>
   - Health Check: <http://localhost:3001/api/v1/health>
   - Celery Monitor: <http://localhost:5555>

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
- [GCP Deployment Guide](docs/GCP_DEPLOYMENT.md)
- [Testing Strategy](docs/INTEGRATION_TESTING_STRATEGY.md)

## 🔧 Configuration

Environment variables are configured in `.env`:

- Google Cloud credentials
- Database and Redis connection strings
- API keys
- Service settings

## 🧪 Testing

Use the `Makefile` to run tests inside the Docker environment:

```bash
# Run all tests
make test

# Run integration tests
make test-integration

# Run end-to-end tests
make test-e2e
```

## 📦 Deployment

Deployment to Google Cloud is automated via a CI/CD pipeline defined in `cloudbuild.yaml`.

1.  **Prerequisites**: Ensure all Google Cloud infrastructure is set up as described in the GCP Deployment Guide.
2.  **Trigger Deployment**: Push your changes to the `main` branch.

    ```bash
    git push origin main
    ```
3.  **Monitor**: Check the build status in the Google Cloud Build console.

## 🤝 Contributing

1. Follow the API validation standards in `.cursor/rules/`
2. Write tests for new features
3. Update documentation
4. Follow the established project structure

## 📄 License

Private project - All rights reserved

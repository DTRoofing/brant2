# 🔧 Comprehensive Codebase Change Rule

## **RULE: Follow Technology Stack Best Practices for ALL Codebase Changes**

### **📋 MANDATORY PROCESS**

When making ANY changes to the codebase (adding, editing, removing, or modifying code), you MUST follow this comprehensive rule that encompasses all technologies in the Brant Roofing System stack.

---

## **🎯 RULE SCOPE**

This rule applies to **ALL** changes affecting:
- Python backend code (FastAPI, services, workers)
- Google Cloud Services integration (Vision AI, Document AI, Cloud Run, etc.)
- Docker containerization
- Frontend TypeScript/React code
- Infrastructure as Code (Terraform)
- CI/CD pipelines (Cloud Build)
- Database schemas and migrations
- Documentation

---

## **📊 PRE-CHANGE REQUIREMENTS**

### **1. Change Assessment**
Before making any changes, you MUST:

#### **Impact Analysis**
- [ ] **Identify affected technologies** (Python, GCP, Docker, etc.)
- [ ] **Assess cross-service impact** (API ↔ Worker ↔ Frontend)
- [ ] **Check dependency chains** (which services depend on your change)
- [ ] **Evaluate environment impact** (dev/staging/prod differences)

#### **Technology-Specific Requirements**
- [ ] **Python**: Ensure async/await patterns, type hints, structured logging
- [ ] **GCP Services**: Check authentication, quotas, regional deployment
- [ ] **AI Services**: Verify confidence scores, fallback mechanisms
- [ ] **Docker**: Confirm multi-stage builds, security, health checks
- [ ] **Cloud Run**: Validate resource limits, networking, scaling

---

## **🐍 PYTHON-SPECIFIC REQUIREMENTS**

### **Code Quality Standards**
When modifying Python code, you MUST:

#### **1. Type Safety & Documentation**
```python
# ✅ REQUIRED: Full type hints and documentation
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class DocumentProcessingRequest(BaseModel):
    """Request model for document processing operations."""
    document_id: str = Field(..., description="Unique document identifier")
    processing_options: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional processing configuration"
    )

    class Config:
        from_attributes = True  # SQLAlchemy compatibility
```

#### **2. Async/Await Patterns**
```python
# ✅ REQUIRED: Proper async implementation
async def process_document(self, document_id: str) -> ProcessingResult:
    """Process document with proper async patterns."""
    try:
        # Database operations
        async with get_db_session() as session:
            document = await session.get(Document, document_id)

        # External API calls with timeouts
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(f"{self.base_url}/process", json=payload) as response:
                result = await response.json()

        return ProcessingResult(success=True, data=result)

    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except ProcessingTimeoutError:
        logger.error("Document processing timeout", document_id=document_id)
        raise HTTPException(status_code=408, detail="Processing timeout")
    except Exception as e:
        logger.error("Unexpected error", error=str(e), document_id=document_id)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### **3. Error Handling Standards**
```python
# ✅ REQUIRED: Specific exception handling, NEVER generic
class DocumentProcessingError(Exception):
    """Base exception for document processing failures."""
    pass

class OCRProcessingError(DocumentProcessingError):
    """OCR-specific processing errors."""
    pass

async def extract_text_with_fallback(self, file_path: str) -> str:
    """Extract text with proper error handling and fallbacks."""
    text = ""

    # Try Document AI first
    try:
        result = await self.document_ai_client.process_document(file_path)
        text = result.document.text
        confidence = result.document.pages[0].confidence

        if confidence < 0.7:
            logger.warning("Low Document AI confidence", confidence=confidence)

    except google.api_core.exceptions.ResourceExhausted:
        logger.warning("Document AI quota exceeded, using OCR fallback")
        raise DocumentAIQuotaExceededError()
    except Exception as e:
        logger.error("Document AI processing failed", error=str(e))

    # Always supplement with OCR fallback
    try:
        ocr_text = await self.perform_ocr(file_path)
        text = text + "\n" + ocr_text if text else ocr_text
    except Exception as e:
        logger.error("OCR processing failed", error=str(e))

    if len(text.strip()) < 50:
        raise InsufficientTextError("Failed to extract sufficient text")

    return text
```

#### **4. Structured Logging**
```python
# ✅ REQUIRED: Correlation IDs and structured logging
import structlog

logger = structlog.get_logger(__name__)

async def process_document_pipeline(self, document_id: str, correlation_id: str):
    """Process document with comprehensive logging."""
    logger.info(
        "Starting document processing",
        document_id=document_id,
        correlation_id=correlation_id,
        stage="initialization"
    )

    try:
        # Processing steps with progress logging
        await self.extract_content(document_id, correlation_id)
        logger.info("Content extraction completed", document_id=document_id)

        await self.perform_ai_analysis(document_id, correlation_id)
        logger.info("AI analysis completed", document_id=document_id)

        await self.generate_estimate(document_id, correlation_id)
        logger.info("Estimate generation completed", document_id=document_id)

        logger.info(
            "Document processing successful",
            document_id=document_id,
            correlation_id=correlation_id,
            total_stages=3
        )

    except Exception as e:
        logger.error(
            "Document processing failed",
            document_id=document_id,
            correlation_id=correlation_id,
            error=str(e),
            stage="error"
        )
        raise
```

---

## **☁️ GOOGLE CLOUD SERVICES REQUIREMENTS**

### **Authentication & Security**
When working with GCP services, you MUST:

#### **1. Workload Identity Configuration**
```python
# ✅ REQUIRED: Proper GCP authentication
from google.auth import default
from google.cloud import documentai_v1, vision_v1

async def initialize_gcp_clients(self):
    """Initialize GCP clients with proper authentication."""
    try:
        # Use workload identity (automatic in Cloud Run)
        credentials, project_id = default()

        # Document AI client
        self.document_ai_client = documentai_v1.DocumentProcessorServiceAsyncClient(
            credentials=credentials
        )

        # Vision AI client
        self.vision_client = vision_v1.ImageAnnotatorAsyncClient(
            credentials=credentials
        )

        logger.info("GCP clients initialized", project_id=project_id)

    except Exception as e:
        logger.error("Failed to initialize GCP clients", error=str(e))
        raise GCPConfigurationError("GCP authentication failed")
```

#### **2. Secret Manager Integration**
```python
# ✅ REQUIRED: Secrets from Secret Manager, never hardcoded
from google.cloud import secretmanager_v1

class SecretsManager:
    """Centralized secrets management."""

    def __init__(self, project_id: str):
        self.client = secretmanager_v1.SecretManagerServiceClient()
        self.project_id = project_id

    async def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Secret Manager."""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = await self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error("Failed to retrieve secret", secret_name=secret_name, error=str(e))
            raise SecretRetrievalError(f"Failed to get secret: {secret_name}")
```

#### **3. Resource Management**
```python
# ✅ REQUIRED: Proper resource cleanup and error handling
class GCPResourceManager:
    """Manage GCP resources with proper cleanup."""

    async def process_with_vision_ai(self, image_data: bytes) -> VisionResult:
        """Process image with Vision AI and proper resource management."""
        try:
            # Create image object
            image = vision_v1.Image(content=image_data)

            # Perform text detection
            response = await self.vision_client.text_detection(image=image)

            if response.error.message:
                raise VisionAPIError(f"Vision API error: {response.error.message}")

            # Process results
            texts = []
            for text_annotation in response.text_annotations:
                texts.append({
                    'text': text_annotation.description,
                    'bounding_box': text_annotation.bounding_poly,
                    'confidence': getattr(text_annotation, 'confidence', None)
                })

            return VisionResult(
                success=True,
                texts=texts,
                full_text=response.full_text_annotation.text if response.full_text_annotation else ""
            )

        except google.api_core.exceptions.ResourceExhausted:
            logger.warning("Vision API quota exceeded")
            raise VisionAPIQuotaExceededError()
        except Exception as e:
            logger.error("Vision API processing failed", error=str(e))
            raise VisionAPIProcessingError(f"Processing failed: {str(e)}")
```

---

## **🐳 DOCKER REQUIREMENTS**

### **Container Best Practices**
When modifying Docker configurations, you MUST:

#### **1. Multi-Stage Builds**
```dockerfile
# ✅ REQUIRED: Multi-stage build pattern
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only=main --no-dev

FROM python:3.11-slim AS runtime

# Security: Non-root user
RUN groupadd --system app && useradd --system --group app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Security: Proper permissions
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### **2. Layer Optimization**
```dockerfile
# ✅ REQUIRED: Optimized layer ordering
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy source code after dependencies
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## **🔨 GOOGLE CLOUD BUILD REQUIREMENTS**

### **CI/CD Pipeline Standards**
When modifying Cloud Build configurations, you MUST:

#### **1. Quality Gates**
```yaml
# ✅ REQUIRED: Comprehensive quality gates
steps:
  # Security scanning
  - name: 'python:3.11'
    id: 'security-scan'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install bandit safety
        bandit -r app/ -f json -o security-report.json
        safety check --json > safety-report.json

  # Testing
  - name: 'python:3.11'
    id: 'unit-tests'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd app
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
        pytest --cov=. --cov-report=xml --cov-report=term

  - name: 'node:18'
    id: 'frontend-tests'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd frontend_ux
        npm install
        npm run test:ci
        npm run lint
        npm run type-check
```

#### **2. Parallel Build Optimization**
```yaml
# ✅ REQUIRED: Parallel processing where possible
steps:
  # Build services in parallel
  - name: 'gcr.io/kaniko-project/executor:latest'
    id: 'build-api'
    waitFor: ['security-scan', 'unit-tests']
    args:
      - '--dockerfile=backend.Dockerfile'
      - '--context=.'
      - '--destination=${_GCR_HOSTNAME}/${PROJECT_ID}/${_REPO_NAME}/api:$COMMIT_SHA'
      - '--cache=true'
      - '--cache-ttl=24h'

  - name: 'gcr.io/kaniko-project/executor:latest'
    id: 'build-worker'
    waitFor: ['security-scan', 'unit-tests']
    args:
      - '--dockerfile=worker.Dockerfile'
      - '--context=.'
      - '--destination=${_GCR_HOSTNAME}/${PROJECT_ID}/${_REPO_NAME}/worker:$COMMIT_SHA'
      - '--cache=true'
      - '--cache-ttl=24h'

  - name: 'gcr.io/kaniko-project/executor:latest'
    id: 'build-frontend'
    waitFor: ['frontend-tests']
    args:
      - '--dockerfile=frontend_ux/Dockerfile'
      - '--context=./frontend_ux'
      - '--destination=${_GCR_HOSTNAME}/${PROJECT_ID}/${_REPO_NAME}/frontend:$COMMIT_SHA'
      - '--cache=true'
      - '--cache-ttl=24h'
```

#### **3. Deployment Configuration**
```yaml
# ✅ REQUIRED: Production-ready deployment settings
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy-api'
    waitFor: ['build-api']
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud run deploy ${_SERVICE_NAME_API} \
          --image=${_GCR_HOSTNAME}/${PROJECT_ID}/${_REPO_NAME}/api:$COMMIT_SHA \
          --region=${_REGION} \
          --platform=managed \
          --service-account=${_SERVICE_ACCOUNT} \
          --vpc-connector=${_VPC_CONNECTOR} \
          --ingress=internal-and-cloud-load-balancing \
          --cpu=2 \
          --memory=2Gi \
          --concurrency=100 \
          --max-instances=10 \
          --min-instances=1 \
          --timeout=300s \
          --set-env-vars="GCP_PROJECT=${PROJECT_ID},ENVIRONMENT=production" \
          --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
          --set-cloudsql-instances="${PROJECT_ID}:${_REGION}:${_DB_INSTANCE_NAME}" \
          --allow-unauthenticated=false

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy-worker'
    waitFor: ['build-worker']
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud run deploy ${_SERVICE_NAME_WORKER} \
          --image=${_GCR_HOSTNAME}/${PROJECT_ID}/${_REPO_NAME}/worker:$COMMIT_SHA \
          --region=${_REGION} \
          --platform=managed \
          --service-account=${_SERVICE_ACCOUNT} \
          --vpc-connector=${_VPC_CONNECTOR} \
          --no-ingress \
          --cpu=1 \
          --memory=1Gi \
          --concurrency=4 \
          --max-instances=5 \
          --min-instances=0 \
          --timeout=900s \
          --set-env-vars="GCP_PROJECT=${PROJECT_ID},ENVIRONMENT=production" \
          --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
          --set-cloudsql-instances="${PROJECT_ID}:${_REGION}:${_DB_INSTANCE_NAME}"
```

---

## **🚀 GOOGLE CLOUD RUN REQUIREMENTS**

### **Service Configuration Standards**
When deploying to Cloud Run, you MUST:

#### **1. Resource Optimization**
```yaml
# ✅ REQUIRED: Proper resource configuration based on workload
# API Service (high-throughput, low-latency)
gcloud run deploy api-service \
  --cpu=2 \
  --memory=2Gi \
  --concurrency=100 \
  --max-instances=10 \
  --min-instances=1 \
  --timeout=300s

# Worker Service (CPU-intensive, batch processing)
gcloud run deploy worker-service \
  --cpu=1 \
  --memory=1Gi \
  --concurrency=4 \
  --max-instances=5 \
  --min-instances=0 \
  --timeout=900s

# Frontend Service (static content, high-throughput)
gcloud run deploy frontend-service \
  --cpu=1 \
  --memory=512Mi \
  --concurrency=80 \
  --max-instances=5 \
  --min-instances=1 \
  --timeout=30s
```

#### **2. Networking & Security**
```yaml
# ✅ REQUIRED: Proper networking configuration
# Internal API service
gcloud run deploy api-service \
  --ingress=internal-and-cloud-load-balancing \
  --vpc-connector=my-vpc-connector \
  --allow-unauthenticated=false

# Worker service (no external access)
gcloud run deploy worker-service \
  --no-ingress \
  --vpc-connector=my-vpc-connector

# Frontend service (public access)
gcloud run deploy frontend-service \
  --ingress=all \
  --allow-unauthenticated=true
```

#### **3. Health Checks & Monitoring**
```yaml
# ✅ REQUIRED: Comprehensive health monitoring
gcloud run deploy api-service \
  --startup-probe-path=/api/v1/health/startup \
  --startup-probe-initial-delay=10s \
  --startup-probe-timeout=5s \
  --startup-probe-period=10s \
  --startup-probe-failure-threshold=3 \
  --liveness-probe-path=/api/v1/health/live \
  --liveness-probe-initial-delay=30s \
  --liveness-probe-timeout=5s \
  --liveness-probe-period=30s \
  --liveness-probe-failure-threshold=3
```

---

## **📋 CHANGE VALIDATION CHECKLIST**

### **Pre-Commit Validation**
Before committing any changes, you MUST verify:

#### **Code Quality**
- [ ] **Type hints** added to all new functions/parameters
- [ ] **Async/await** used for I/O operations
- [ ] **Structured logging** with correlation IDs
- [ ] **Specific exception handling** (no bare `except:`)
- [ ] **No hardcoded credentials** or localhost URLs
- [ ] **Pydantic models** with proper validation
- [ ] **No wildcard imports** (`import *`)

#### **Security & Authentication**
- [ ] **Workload Identity** used for GCP authentication
- [ ] **Secrets in Secret Manager** (not environment variables)
- [ ] **Service accounts** with minimal required permissions
- [ ] **Input validation** on all user inputs
- [ ] **Rate limiting** implemented where appropriate

#### **Container & Deployment**
- [ ] **Multi-stage Docker builds** for all services
- [ ] **Non-root users** in containers
- [ ] **Health checks** implemented
- [ ] **Resource limits** properly configured
- [ ] **Environment variables** used for configuration

#### **Testing & Documentation**
- [ ] **Unit tests** added for new functionality
- [ ] **Integration tests** for cross-service interactions
- [ ] **Type checking** passes (`mypy` or `tsc`)
- [ ] **Documentation updated** for API changes
- [ ] **README updated** for configuration changes

### **Post-Deployment Validation**
After deployment, you MUST verify:

#### **Functional Testing**
- [ ] **API endpoints** respond correctly
- [ ] **Authentication** works as expected
- [ ] **Error handling** provides meaningful messages
- [ ] **Performance** meets requirements (<30s response times)
- [ ] **Resource usage** within limits

#### **Integration Testing**
- [ ] **Service-to-service communication** works
- [ ] **Database connections** established
- [ ] **External API integrations** functional
- [ ] **File processing pipelines** complete successfully
- [ ] **Frontend-backend integration** seamless

---

## **🚨 CRITICAL RULES**

1. **NEVER** make changes without following this comprehensive rule
2. **ALWAYS** test changes across all affected services
3. **NEVER** deploy without proper resource configuration
4. **ALWAYS** use Secret Manager for sensitive data
5. **NEVER** use generic exception handling
6. **ALWAYS** implement proper async patterns
7. **NEVER** hardcode environment-specific values
8. **ALWAYS** include comprehensive logging
9. **NEVER** skip security scanning or testing
10. **ALWAYS** document API and configuration changes

---

## **💡 IMPLEMENTATION EXAMPLES**

### **Adding a New API Endpoint**
```python
# ✅ CORRECT: Following all rules
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.config import settings
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.document_processor import DocumentProcessor

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/documents/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: str,
    processing_options: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    correlation_id: str = None
) -> DocumentResponse:
    """Process a document with comprehensive error handling and logging."""
    logger.info(
        "Processing document request",
        document_id=document_id,
        correlation_id=correlation_id,
        options=processing_options
    )

    try:
        # Validate document exists
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Process document
        processor = DocumentProcessor(db, correlation_id)
        result = await processor.process_document(document, processing_options)

        logger.info(
            "Document processing completed",
            document_id=document_id,
            correlation_id=correlation_id,
            success=True
        )

        return DocumentResponse.from_orm(result)

    except DocumentNotFoundError:
        logger.warning(
            "Document not found",
            document_id=document_id,
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=404, detail="Document not found")

    except ProcessingTimeoutError:
        logger.error(
            "Document processing timeout",
            document_id=document_id,
            correlation_id=correlation_id
        )
        raise HTTPException(status_code=408, detail="Processing timeout")

    except Exception as e:
        logger.error(
            "Unexpected error processing document",
            document_id=document_id,
            correlation_id=correlation_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Internal server error")
```

### **Modifying Database Schema**
```python
# ✅ CORRECT: Following migration best practices
# alembic/versions/001_add_processing_results.py
"""Add processing results table."""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade database schema."""
    # Create processing results table
    op.create_table(
        'processing_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processing_status'), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('processing_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Indexes for performance
        sa.Index('ix_processing_results_document_id', 'document_id'),
        sa.Index('ix_processing_results_status', 'status'),
        sa.Index('ix_processing_results_created_at', 'created_at'),

        # Foreign key constraint
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),

        sa.PrimaryKeyConstraint('id')
    )

    # Add indexes to existing tables if needed
    op.create_index('ix_documents_processing_status', 'documents', ['processing_status'])

def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index('ix_documents_processing_status', table_name='documents')
    op.drop_table('processing_results')
```

---

## **📈 SUCCESS CRITERIA**

A codebase change following this rule is successful when:

- [ ] **All quality gates pass** (security scanning, testing, linting)
- [ ] **No hardcoded values** remain in production code
- [ ] **Proper async patterns** used throughout
- [ ] **Comprehensive error handling** with specific exceptions
- [ ] **Structured logging** with correlation IDs implemented
- [ ] **Resource limits** properly configured for production
- [ ] **Secrets managed** through Secret Manager
- [ ] **Multi-stage builds** used for all containers
- [ ] **Health checks** and monitoring configured
- [ ] **Documentation updated** to reflect changes
- [ ] **All services deploy successfully** without errors
- [ ] **Performance benchmarks** met or exceeded
- [ ] **Security audit** passes without critical issues

---

## **🔄 IMPLEMENTATION WORKFLOW**

1. **Planning Phase**
   - Assess change impact across all technologies
   - Identify required modifications
   - Plan testing strategy

2. **Implementation Phase**
   - Apply technology-specific best practices
   - Implement comprehensive error handling
   - Add structured logging and monitoring

3. **Validation Phase**
   - Run quality gates (security, testing, linting)
   - Perform integration testing
   - Validate resource configuration

4. **Deployment Phase**
   - Deploy with proper Cloud Run configuration
   - Monitor initial performance
   - Validate production functionality

---

## **🎯 CONCLUSION**

This comprehensive rule ensures that **ALL** codebase changes maintain the highest standards of quality, security, performance, and maintainability across the entire Brant Roofing System technology stack. Every change must demonstrate compliance with these standards before being merged or deployed.

**Remember**: Quality is not optional - it's mandatory. Following this rule guarantees that the system remains robust, scalable, and maintainable as it grows.

---

**Last Updated**: $(date)
**Version**: 1.0
**Scope**: All codebase changes
**Enforcement**: Mandatory for all contributors

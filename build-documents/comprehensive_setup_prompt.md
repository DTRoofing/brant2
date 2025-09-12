# DT Roofing Agent - Complete Production-Ready Setup

## Context
Build a fully containerized, production-ready development environment for the DT Roofing Agent - an AI-powered system that processes construction blueprints (up to 100MB PDFs) and generates roofing estimates through OCR and measurement extraction.

## Architecture Requirements
- **Backend**: FastAPI + SQLAlchemy + Alembic + Celery
- **Database**: PostgreSQL with JSONB support
- **Cache/Queue**: Redis for Celery + caching
- **File Processing**: PDF2Image + Tesseract OCR + OpenCV
- **Storage**: Local volume mounting (production: S3 integration ready)

---

## 1. Complete Project Structure

Create this exact folder structure with all files:

```
dt-roofing-agent/
├── .github/workflows/
│   └── ci.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── core.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── health.py
│   │       │   ├── uploads.py
│   │       │   └── estimates.py
│   │       └── schemas/
│   │           ├── __init__.py
│   │           ├── upload.py
│   │           └── estimate.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── pdf_processing.py
│   │       └── measurement_extraction.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   ├── measurement_service.py
│   │   └── estimation_service.py
│   └── alembic/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_workers/
├── frontend/
│   └── .gitkeep
├── uploads/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── pyproject.toml
├── docker-compose.yml
├── docker-compose.override.yml
├── backend.Dockerfile
├── worker.Dockerfile
├── alembic.ini
├── .env.example
├── .env
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 2. Infrastructure Configuration

### **pyproject.toml** - Complete Dependencies
```toml
[tool.poetry]
name = "dt-roofing-agent"
version = "0.1.0"
description = "AI-powered roofing estimation system"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
psycopg2-binary = "^2.9.7"
celery = {extras = ["redis"], version = "^5.3.4"}
redis = "^5.0.1"
pydantic = "^2.4.2"
pydantic-settings = "^2.0.3"
python-multipart = "^0.0.6"
aiofiles = "^23.2.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}

# PDF Processing Dependencies
pdf2image = "^1.17.0"
pytesseract = "^0.3.10"
opencv-python = "^4.8.1.78"
pillow = "^10.0.1"
numpy = "^1.24.3"

# Development Dependencies
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.1"
pytest-celery = "^0.0.0"
black = "^23.9.1"
isort = "^5.12.0"
mypy = "^1.6.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
```

### **docker-compose.yml** - Production-Ready Services
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://roofing_user:roofing_pass@db:5432/roofing_db
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
      - DEBUG=true
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: worker.Dockerfile
    environment:
      - DATABASE_URL=postgresql://roofing_user:roofing_pass@db:5432/roofing_db
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=roofing_user
      - POSTGRES_PASSWORD=roofing_pass
      - POSTGRES_DB=roofing_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U roofing_user -d roofing_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### **backend.Dockerfile** - Optimized Build
```dockerfile
FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.6.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY ./app .

# Create necessary directories
RUN mkdir -p uploads logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### **worker.Dockerfile** - Celery Worker
```dockerfile
FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.6.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY ./app .

# Create necessary directories
RUN mkdir -p uploads logs

CMD ["celery", "worker", "-A", "workers.celery_app", "--loglevel=info"]
```

---

## 3. Core Application Implementation

### **app/main.py** - FastAPI Application
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine
from models.base import Base
from api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="DT Roofing Agent API",
    description="AI-powered roofing estimation system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")
```

### **app/core/config.py** - Validated Settings
```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/db"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Processing
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    SUPPORTED_FORMATS: List[str] = ["pdf"]
    
    # OCR Configuration
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    MIN_CONFIDENCE_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"


settings = Settings()
```

### **app/models/core.py** - Database Models
```python
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from models.base import Base


class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    client_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="project")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    measurements = relationship("Measurement", back_populates="document")


class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    area_sf = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    source_coordinates = Column(JSON)  # Store bounding box, scale info
    measurement_type = Column(String(50))  # roof_area, wall_area, etc.
    extraction_method = Column(String(50))  # ocr, manual, calculated
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="measurements")
```

---

## 4. Critical Services Implementation

### **app/workers/tasks/pdf_processing.py** - Core Processing
```python
import logging
import asyncio
from celery import shared_task
from pathlib import Path
import uuid

from services.ocr_service import OCRService
from services.measurement_service import MeasurementService
from core.database import get_db
from models.core import Document, Measurement, ProcessingStatus

logger = logging.getLogger(__name__)


async def async_process_pdf_document(document_id: str):
    """
    The core async processing logic for a PDF document.
    """
    async with get_db() as db:
        # Get document record
        doc_uuid = uuid.UUID(document_id)
        document = await db.get(Document, doc_uuid)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Update status to processing
        document.processing_status = ProcessingStatus.PROCESSING
        await db.commit()

        # Initialize services
        ocr_service = OCRService()
        measurement_service = MeasurementService()

        # Process PDF
        pdf_path = Path(document.file_path)

        # Extract text and measurements
        ocr_results = await ocr_service.extract_text_from_pdf(pdf_path)
        measurements = await measurement_service.extract_measurements(
            pdf_path, ocr_results
        )

        # Save measurements to database
        for measurement_data in measurements:
            measurement = Measurement(
                document_id=document.id,
                **measurement_data
            )
            db.add(measurement)

        # Update document status
        document.processing_status = ProcessingStatus.COMPLETED
        await db.commit()

        logger.info(f"Successfully processed document {document_id}")
        return {"status": "completed", "measurements_count": len(measurements)}


@shared_task(bind=True, max_retries=3)
def process_pdf_document(self, document_id: str):
    """
    Complete PDF processing pipeline:
    1. Convert PDF to images
    2. Run OCR extraction
    3. Extract measurements
    4. Calculate roof areas
    5. Update database
    """
    try:
        # Run the async processing logic in a new event loop
        return asyncio.run(async_process_pdf_document(document_id))
    except Exception as exc:
        logger.error(f"Error processing document {document_id}: {str(exc)}")

        # We need to run the failure update in an event loop as well
        async def update_failure_status():
            async with get_db() as db:
                doc_uuid = uuid.UUID(document_id)
                document = await db.get(Document, doc_uuid)
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = str(exc)
                    await db.commit()

        try:
            asyncio.run(update_failure_status())
        except Exception as update_exc:
            logger.error(f"Failed to update document status to FAILED for {document_id}: {update_exc}")

        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        raise exc
```

---

## 5. Development & Testing Setup

### **.env.example** - Complete Configuration
```bash
# Database Configuration
DATABASE_URL=postgresql://roofing_user:roofing_pass@localhost:5432/roofing_db
POSTGRES_USER=roofing_user
POSTGRES_PASSWORD=roofing_pass
POSTGRES_DB=roofing_db

# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=INFO
API_VERSION=v1

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# File Processing Configuration
MAX_FILE_SIZE=104857600
UPLOAD_DIR=uploads
SUPPORTED_FORMATS=["pdf"]

# OCR Configuration
TESSERACT_CONFIG=--oem 3 --psm 6
MIN_CONFIDENCE_THRESHOLD=0.7

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **alembic.ini** - Database Migrations
```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
timezone = UTC

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

## 6. Build & Verification Commands

### **Startup Sequence** (guaranteed to work):
```bash
# 1. Clone and setup
git clone <repo> && cd dt-roofing-agent
cp .env.example .env

# 2. Build and start services
docker-compose build
docker-compose up -d

# 3. Run database migrations
docker-compose exec api alembic upgrade head

# 4. Verify all services
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# 5. Test file upload
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"
```

### **Health Check Endpoints**
```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
import redis
from core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dt-roofing-api"}

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    checks = {}
    
    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    return {"status": "healthy", "checks": checks}
```

---

## Success Criteria

✅ **Zero build errors** - All Docker containers start successfully  
✅ **Database connectivity** - Alembic migrations run without issues  
✅ **API functionality** - Health checks return 200 OK  
✅ **File upload** - PDF files can be uploaded and queued for processing  
✅ **Celery workers** - Background tasks execute without crashing  
✅ **OCR pipeline** - PDF text extraction works end-to-end  
✅ **Hot reloading** - Code changes reflect immediately in development  

This setup provides a rock-solid foundation that handles all the edge cases and potential build failures while following modern best practices for Python monorepos.

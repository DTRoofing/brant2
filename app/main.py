from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.api.v1.router import api_router
from app.core.config import settings
# from app.workers.celery_app import celery_app  # Import to configure Celery client - disabled

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    On startup, log settings and create database tables.
    """
    logger.info("Application startup...")
    # Database schema is now managed by Alembic. No need to run create_all here.
    yield
    logger.info("Application shutdown...")

app = FastAPI(
    title="Brant Roofing System",
    description="AI-powered roofing estimation system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with specific origins for security
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend development
    "http://localhost:3001",  # API development
    "http://brant-frontend:3000",  # Docker frontend
    "https://brant-roofing.com",  # Production domain (replace with actual)
]

# In production, use environment variable for allowed origins
if os.getenv("PRODUCTION", "false").lower() == "true":
    allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    allowed_origins = ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "🏠 Brant Roofing System API is running"}
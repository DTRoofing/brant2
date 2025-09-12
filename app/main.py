from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.v1.router import api_router
from workers.celery_app import celery_app  # Import to configure Celery client

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "🏠 Brant Roofing System API is running"}
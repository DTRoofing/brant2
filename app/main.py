from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError
import logging
import os
import time

from app.core.exceptions import BrantAPIException

from app.api.v1.router import api_router
from app.core.config import settings
# from app.api.v1.endpoints import documents # Direct import to fix routing issue
# from app.workers.celery_app import celery_app  # Import to configure Celery client - disabled

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


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

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Add request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses with timing information."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

# Add custom exception handlers
@app.exception_handler(BrantAPIException)
async def brant_api_exception_handler(request: Request, exc: BrantAPIException):
    """Handle custom Brant API exceptions with enhanced error details."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "context": exc.context
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with detailed field information."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with logging."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "🏠 Brant Roofing System API is running"}
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

from app.core.config import settings
from app.api.v1.endpoints import health, uploads, pipeline, claude_processing

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

# Configure CORS. Origins are managed via the `CORS_ORIGINS` environment
# variable in your settings. This provides a single source of truth for configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # It is more secure to specify the exact headers your frontend sends.
    # The wildcard '*' is too permissive.
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add file size validation middleware
@app.middleware("http")
async def limit_upload_size_middleware(request: Request, call_next):
    """
    Check for 'content-length' header and reject request if it exceeds the limit.
    This provides a fast first-pass check for file uploads.
    """
    if "content-length" in request.headers:
        try:
            content_length = int(request.headers["content-length"])
            if content_length > settings.MAX_FILE_SIZE:
                logger.warning(f"Rejected upload: file size {content_length} exceeds limit of {settings.MAX_FILE_SIZE}.")
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes."}
                )
        except (ValueError, TypeError):
            logger.warning(f"Could not parse content-length header: {request.headers['content-length']}")
            # Let it pass to be handled by the endpoint logic if header is malformed
    return await call_next(request)

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


# Include all the API routers with their specific prefixes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(uploads.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(claude_processing.router, prefix="/api/v1/claude", tags=["Claude"])

@app.get("/")
async def root():
    return {"message": "🏠 Brant Roofing System API is running"}
from fastapi import APIRouter
from .endpoints import health, uploads, pipeline

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(uploads.router, prefix="/documents", tags=["Documents"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
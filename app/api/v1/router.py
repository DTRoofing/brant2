from fastapi import APIRouter
from .endpoints import health, uploads

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(uploads.router, prefix="/documents", tags=["Documents"])
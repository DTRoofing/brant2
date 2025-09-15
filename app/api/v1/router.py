from fastapi import APIRouter
from .endpoints import uploads, pipeline, claude_process

api_router = APIRouter()

api_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(claude_process.router, prefix="/pipeline", tags=["Claude Processing"])
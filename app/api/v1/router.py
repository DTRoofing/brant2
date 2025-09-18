from fastapi import APIRouter

from app.api.v1.endpoints import claude_processing, pipeline, uploads, health

api_router = APIRouter()

# FIX: The test report indicates a 404 on `/api/v1/documents/upload`.
# The prefix was incorrectly set to "/uploads", resulting in "/api/v1/uploads/upload".
# This changes the prefix to "/documents" to correctly form the path "/api/v1/documents/upload",
# which is the primary blocker for all 32 failed integration and E2E tests.
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(uploads.router, prefix="/documents", tags=["Documents"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(claude_processing.router, prefix="/pipeline", tags=["Claude Processing"])
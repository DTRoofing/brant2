import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.workers.celery_app import celery_app
from app.db.session import get_db
from app.models.core import Document
from app.schemas.claude_process import ClaudeProcessRequest, TaskResponse
from app.api.v1.endpoints.document_repository import get

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-with-claude", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_with_claude(
    request: ClaudeProcessRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    This endpoint accepts a document ID and triggers the Claude processing task.
    It immediately returns a task ID for the client to poll for status.
    """
    # Use existing document repository
    document = await get(db, str(request.document_id))

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if not document.gcs_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has not been uploaded to GCS. Please complete the upload process first."
        )

    try:
        # Send task to Celery worker
        task = celery_app.send_task(
            "app.workers.tasks.new_pdf_processing.process_pdf_with_pipeline",
            args=[str(document.id)],
            kwargs={"processing_options": {"mode": "claude_only"}},
        )

        # Set the Location header for the status endpoint
        status_url = f"/api/v1/documents/{document.id}/status"
        response.headers["Location"] = status_url

        return TaskResponse(task_id=task.id, status="pending", document_id=str(document.id))

    except Exception as e:
        logger.error(f"Failed to enqueue task for document {request.document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start document processing task.",
        )
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, constr
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.google_services import google_service
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.core import User, Document, ProcessingStatus
from app.schemas.document import DocumentRead
from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline


router = APIRouter()
logger = logging.getLogger(__name__)


class SignedURLRequest(BaseModel):
    file_name: str = Field(..., description="The name of the file to be uploaded.")
    content_type: str = Field(..., description="The MIME type of the file (e.g., 'application/pdf').")
    size: int = Field(..., gt=0, description="The size of the file in bytes.")


class SignedURLResponse(BaseModel):
    upload_url: str
    gcs_object_name: str


class StartProcessingRequest(BaseModel):
    gcs_object_name: str
    original_filename: str
    document_type: constr(to_lower=True)


@router.post(
    "/generate-signed-url",
    response_model=SignedURLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a secure URL for file uploads",
)
async def generate_signed_url(
    request: SignedURLRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generates a short-lived, secure signed URL for uploading a file directly to GCS.

    This endpoint enforces content type and size restrictions to enhance security.
    """
    try:
        # Generate a unique object name to prevent overwrites
        gcs_object_name = f"uploads/{current_user.id}/{uuid.uuid4()}/{request.file_name}"

        upload_url = google_service.generate_upload_signed_url_v4(
            gcs_object_name, request.content_type, request.size
        )
        return SignedURLResponse(upload_url=upload_url, gcs_object_name=gcs_object_name)
    except Exception as e:
        logger.error(f"Failed to generate signed URL for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate upload URL. Please try again later.",
        )


@router.post(
    "/start-processing",
    response_model=DocumentRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Confirm upload and start processing pipeline",
)
async def start_processing(
    request: StartProcessingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a document record in the database after a file has been uploaded
    to GCS, and then enqueues it for processing in the background.
    """
    try:
        # 1. Create a new Document object in the database
        new_document = Document(
            id=uuid.uuid4(),
            filename=request.original_filename,
            gcs_object_name=request.gcs_object_name,
            user_id=current_user.id,
            processing_status=ProcessingStatus.PENDING,
            document_type=request.document_type,
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        # 2. Enqueue the background processing task
        processing_options = {"mode": "standard"}  # Use default options for now
        task = process_pdf_with_pipeline.delay(str(new_document.id), processing_options=processing_options)
        logger.info(f"Enqueued processing for document {new_document.id} (Task ID: {task.id}) from GCS object {request.gcs_object_name}")

        return DocumentRead.model_validate(new_document)

    except Exception as e:
        logger.error(f"Failed to start processing for GCS object {request.gcs_object_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not start document processing. Please try again later.",
        )
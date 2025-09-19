import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.google_services import google_service
from app.api.deps import get_current_active_user
from app.models.core import User

router = APIRouter()
logger = logging.getLogger(__name__)


class SignedURLRequest(BaseModel):
    file_name: str = Field(..., description="The name of the file to be uploaded.")
    content_type: str = Field(..., description="The MIME type of the file (e.g., 'application/pdf').")
    size: int = Field(..., gt=0, description="The size of the file in bytes.")


class SignedURLResponse(BaseModel):
    upload_url: str
    gcs_object_name: str


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
import logging
import uuid
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field, constr
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.google_services import google_service
from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.core import User, Document, ProcessingStatus
from app.schemas.document import DocumentRead
from app.workers.tasks.pdf_processing import process_pdf_document


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


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    message: str


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
    except ValueError as e:
        logger.error(f"Invalid request parameters for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}",
        )
    except PermissionError as e:
        logger.error(f"Permission denied for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to generate upload URL.",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating signed URL for user {current_user.id}: {e}", exc_info=True)
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
        processing_options = {"mode": "standard"}
        from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline
        task = process_pdf_with_pipeline.delay(str(new_document.id), processing_options)
        logger.info(f"Enqueued processing for document {new_document.id} (Task ID: {task.id}) from GCS object {request.gcs_object_name}")

        return DocumentRead.model_validate(new_document)

    except ValueError as e:
        logger.error(f"Invalid request data for GCS object {request.gcs_object_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to start processing for GCS object {request.gcs_object_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not start document processing. Please try again later.",
        )


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload PDF document directly",
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a PDF document directly and start processing.
    This endpoint is for testing and simple uploads.
    """
    try:
        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are allowed"
            )
        
        # Validate file size (100MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 100MB limit"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Empty file not allowed"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = upload_dir / filename
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create document record
        new_document = Document(
            id=uuid.uuid4(),
            filename=file.filename,
            gcs_object_name=f"uploads/{filename}",
            user_id=current_user.id,
            processing_status=ProcessingStatus.PENDING,
            document_type="blueprint",
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)
        
        # Start processing
        processing_options = {"mode": "standard"}
        from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline
        task = process_pdf_with_pipeline.delay(str(new_document.id), processing_options)
        logger.info(f"Enqueued processing for document {new_document.id} (Task ID: {task.id})")
        
        return UploadResponse(
            id=str(new_document.id),
            filename=file.filename,
            status="pending",
            message="Document uploaded successfully and queued for processing"
        )

    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"File system error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File system error. Please try again later."
        )
    except PermissionError as e:
        logger.error(f"Permission error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission error. Please contact support."
        )
    except ValueError as e:
        logger.error(f"Invalid data during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to upload document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document. Please try again later."
        )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get document details",
)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get document details by ID.
    """
    try:
        # Convert string to UUID
        doc_uuid = uuid.UUID(document_id)
        
        # Query document from database
        result = await db.execute(
            "SELECT * FROM documents WHERE id = :id AND user_id = :user_id",
            {"id": doc_uuid, "user_id": current_user.id}
        )
        document = result.fetchone()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Convert to DocumentRead model
        return DocumentRead(
            id=str(document.id),
            filename=document.filename,
            gcs_object_name=document.gcs_object_name,
            user_id=document.user_id,
            processing_status=document.processing_status,
            document_type=document.document_type,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid document ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )
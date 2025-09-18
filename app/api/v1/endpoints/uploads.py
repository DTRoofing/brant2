from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.sync_session import get_sync_db
from app.schemas.upload import GenerateUploadUrlRequest, GenerateUploadUrlResponse, StartProcessingRequest
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.gcs_service import gcs_service
from app.models.core import Document, ProcessingStatus
from app.workers.celery_app import celery_app
from app.core.file_validation import validate_upload, sanitize_filename
from app.core.exceptions import InvalidFileTypeError, FileSizeExceededError
import uuid
import logging
import tempfile
import os
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/generate-url", 
    response_model=GenerateUploadUrlResponse, 
    status_code=status.HTTP_200_OK,
    tags=["Documents"],
    summary="Generate upload URL",
    description="Generates a signed URL for secure file upload to Google Cloud Storage",
    response_description="Upload URL and GCS object name"
)
async def generate_upload_url(
    request: GenerateUploadUrlRequest,
):
    """
    Generates a pre-signed URL for uploading a file directly to Google Cloud Storage.
    """
    # Force initialization of GCS service
    gcs_service._initialize()
    
    if not gcs_service.bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Cloud Storage service is not configured or available."
        )

    # Generate a unique path for the file in GCS to avoid collisions
    gcs_object_name = f"uploads/{uuid.uuid4()}/{request.filename}"

    upload_url = gcs_service.generate_upload_signed_url(
        blob_name=gcs_object_name,
        content_type=request.content_type
    )

    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate upload URL."
        )

    return GenerateUploadUrlResponse(upload_url=upload_url, gcs_object_name=gcs_object_name)


@router.post("/start-processing", response_model=DocumentRead, status_code=status.HTTP_202_ACCEPTED)
async def start_processing(
    request: StartProcessingRequest,
    db: Session = Depends(get_sync_db)
):
    """
    Creates a document record and enqueues it for processing after it has been uploaded to GCS.
    """
    # Here you could add a check to verify the object actually exists in GCS if needed.
    # For now, we trust the client.

    # Create document data with correct field mapping
    document_data = {
        "filename": request.original_filename,
        "file_path": request.gcs_object_name,  # Map gcs_path to file_path
        "processing_status": ProcessingStatus.PENDING,
    }

    db_document = Document(**document_data)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    logger.info(f"Enqueuing document ID {db_document.id} for processing from GCS path: {db_document.file_path}")

    # Enqueue the task for the worker
    celery_app.send_task(
        "app.workers.document_processor.process_document_task",
        args=[db_document.id],
    )

    return db_document


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Direct file upload",
    description="Uploads a PDF file directly and starts processing",
    response_description="Document information and processing status"
)
async def upload_document_direct(
    file: UploadFile = File(...),
    db: Session = Depends(get_sync_db)
):
    """
    Direct file upload endpoint that handles the complete upload and processing flow.
    
    This endpoint:
    1. Validates the uploaded file
    2. Uploads it to Google Cloud Storage
    3. Creates a document record in the database
    4. Starts the processing pipeline
    5. Returns the document information
    """
    # Force initialization of GCS service
    gcs_service._initialize()
    
    if not gcs_service.bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Cloud Storage service is not configured or available."
        )

    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise InvalidFileTypeError(
            file_type=file.filename or "unknown",
            allowed_types=["PDF"]
        )

    # Check file size
    if file.size and file.size > 200 * 1024 * 1024:  # 200MB limit
        raise FileSizeExceededError(
            file_size=file.size,
            max_size=200 * 1024 * 1024
        )

    # Sanitize filename
    sanitized_filename = await sanitize_filename(file.filename)
    
    # Create temporary file for validation
    temp_file_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file_path = Path(temp_file.name)
            
            # Read file content in chunks to handle large files
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Validate the uploaded file
            is_valid, error_message = await validate_upload(
                temp_file_path, 
                sanitized_filename, 
                file.content_type
            )
            
            if not is_valid:
                raise InvalidFileTypeError(
                    file_type=sanitized_filename,
                    allowed_types=["PDF"]
                )

        # Generate unique GCS object name
        gcs_object_name = f"uploads/{uuid.uuid4()}/{sanitized_filename}"
        
        # Upload to Google Cloud Storage
        try:
            blob = gcs_service.bucket.blob(gcs_object_name)
            blob.upload_from_filename(str(temp_file_path), content_type='application/pdf')
            logger.info(f"Successfully uploaded file to GCS: {gcs_object_name}")
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to cloud storage"
            )

        # Create document record
        document_data = {
            "filename": sanitized_filename,
            "file_path": gcs_object_name,
            "processing_status": ProcessingStatus.PENDING,
        }

        db_document = Document(**document_data)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        logger.info(f"Created document record with ID: {db_document.id}")

        # Start processing
        try:
            celery_app.send_task(
                "app.workers.document_processor.process_document_task",
                args=[db_document.id],
            )
            logger.info(f"Enqueued document {db_document.id} for processing")
        except Exception as e:
            logger.error(f"Failed to enqueue document for processing: {e}")
            # Don't fail the upload if processing enqueue fails
            # The document is still uploaded and can be processed manually

        return db_document

    except (InvalidFileTypeError, FileSizeExceededError):
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file upload"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and temp_file_path.exists():
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
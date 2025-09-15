import uuid
import aiofiles
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.core import Document, ProcessingStatus
from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline
from ..schemas.upload import DocumentCreateResponse, DocumentDetailResponse

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    """
    Uploads a PDF document, saves it, creates a database record,
    and queues it for background processing.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported.",
        )
    
    # Check file size before processing
    # First check Content-Length header if available
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_id = uuid.uuid4()
    safe_filename = f"{unique_id}.pdf"
    file_path = upload_dir / safe_filename

    try:
        # Stream file to disk with size validation
        total_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        async with aiofiles.open(file_path, "wb") as out_file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                total_size += len(chunk)
                
                # Check size during streaming
                if total_size > settings.MAX_FILE_SIZE:
                    # Delete partial file
                    await out_file.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
                    )
                
                await out_file.write(chunk)
        
        file_size = total_size
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error uploading the file: {e}",
        )

    # Use transaction for database operations
    from app.core.transactions import async_transaction
    
    try:
        async with async_transaction(db) as session:
            new_document = Document(
                id=unique_id, 
                filename=file.filename, 
                file_path=str(file_path), 
                file_size=file_size
            )
            session.add(new_document)
            # Transaction commits automatically on success
        
        # Queue background processing only after successful commit
        process_pdf_with_pipeline.delay(document_id=str(unique_id))
    except Exception as e:
        # Clean up uploaded file if database operation fails
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document record: {e}"
        )
    
    # Return document data without refresh
    return {
        "id": str(unique_id),
        "filename": file.filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "processing_status": "PENDING",
        "message": "Document uploaded and processing started"
    }


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document_details(
    document_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the full details and processing status of a document.
    """
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return document
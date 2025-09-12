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

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_id = uuid.uuid4()
    safe_filename = f"{unique_id}.pdf"
    file_path = upload_dir / safe_filename

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        file_size = file_path.stat().st_size
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error uploading the file: {e}",
        )

    new_document = Document(
        id=unique_id, filename=file.filename, file_path=str(file_path), file_size=file_size
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    process_pdf_with_pipeline.delay(document_id=str(new_document.id))

    return new_document


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
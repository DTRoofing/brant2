import logging
import asyncio
from celery import shared_task
from pathlib import Path
import uuid
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

# from app.services.ocr_service import OCRService
# from app.services.measurement_service import MeasurementService
from app.core.database import AsyncSessionFactory
from app.models.core import Document, Measurement, ProcessingStatus

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2 and OCR as fallback.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Extracted text from the PDF
    """
    text = ""
    
    try:
        # First try to extract text directly using PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If no text was extracted, use OCR
        if len(text.strip()) < 10:
            logger.info("No text found with PyPDF2, using OCR...")
            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                # Extract text from each image using OCR
                for i, image in enumerate(images):
                    logger.info(f"Processing page {i+1} with OCR...")
                    page_text = pytesseract.image_to_string(image)
                    text += f"--- Page {i+1} ---\n{page_text}\n"
            except Exception as ocr_error:
                logger.error(f"OCR extraction failed: {ocr_error}")
                
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise
    
    return text


async def async_process_pdf_document(document_id: str):
    """
    The core async processing logic for a PDF document.
    This is currently stubbed out to prevent startup crashes.
    """
    async with AsyncSessionFactory() as db:
        # Get document record
        doc_uuid = uuid.UUID(document_id)
        document = await db.get(Document, doc_uuid)
        if not document:
            logger.error(f"Document {document_id} not found in worker.")
            return {"status": "error", "detail": "Document not found"}

        # Update status to processing
        document.processing_status = ProcessingStatus.PROCESSING
        await db.commit()

        try:
            # Extract text from PDF
            pdf_path = Path(document.file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            extracted_text = extract_text_from_pdf(str(pdf_path))
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            
            # TODO: Add measurement extraction logic here
            # For now, just mark as completed
            
            document.processing_status = ProcessingStatus.COMPLETED
            await db.commit()
            
            return {
                "status": "success",
                "document_id": str(document_id),
                "extracted_text_length": len(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            document.processing_status = ProcessingStatus.FAILED
            document.processing_error = str(e)
            await db.commit()
            
            return {
                "status": "error",
                "document_id": str(document_id),
                "error": str(e)
            }


@shared_task
def process_pdf_document(document_id: str):
    """
    Celery task wrapper that calls the async processing function.
    """
    logger.info(f"Starting PDF processing for document {document_id}")
    
    # Run the async function in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(async_process_pdf_document(document_id))
        return result
    finally:
        loop.close()
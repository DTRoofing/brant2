"""
PDF Processing utilities - wrapper functions for testing compatibility.
"""
import asyncio
from typing import Dict, Any
from app.services.processing_stages.content_extractor import ContentExtractor
from app.workers.tasks.pdf_processing import process_pdf_document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Synchronous wrapper for PDF text extraction.
    For testing compatibility with existing test functions.
    """
    async def _extract():
        extractor = ContentExtractor()
        text, method = await extractor.extract_text_from_pdf(file_path)
        return text
    
    return asyncio.run(_extract())


async def async_process_pdf_document(document_id: str) -> Dict[str, Any]:
    """
    Async wrapper for PDF document processing.
    For testing compatibility with existing test functions.
    """
    try:
        # Import here to avoid circular imports
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        # For testing, we'll call the task synchronously
        # In production, this would be handled by Celery workers
        result = process_pdf_document(str(document_id))
        
        return {
            "status": "success",
            "extracted_text_length": 0,
            "detail": "Processing completed",
            "task_id": result.id if hasattr(result, 'id') else None
        }
    except Exception as e:
        return {
            "status": "error",
            "extracted_text_length": 0,
            "detail": f"Processing failed: {str(e)}",
            "error": str(e)
        }

import logging
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document, ProcessingStatus
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=2)
def analyze_text_task(self, document_id: str):
    """A background task to analyze extracted text using an AI model."""
    logger.info(f"Starting text analysis for document_id: {document_id}")
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document or not document.extracted_text:
            logger.warning(f"Document {document_id} not found or has no extracted text. Skipping analysis.")
            return

        document.status_message = "Analyzing text with AI model..."
        db.commit()

        analysis_result = claude_service.analyze_text_for_estimate(document.extracted_text)

        document.analysis_result = analysis_result
        document.status = ProcessingStatus.SUCCESS
        document.status_message = "AI analysis complete."
        db.commit()

        logger.info(f"Successfully analyzed text for document_id: {document_id}")
        return {'status': 'Analysis Complete', 'document_id': document_id, 'analysis_keys': list(analysis_result.keys())}

    except Exception as exc:
        logger.error(f"Failed to analyze text for document_id {document_id}: {exc}", exc_info=True)
        # Update status and retry
        countdown = 120 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
    finally:
        db.close()
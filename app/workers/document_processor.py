"""
Document processor module for Brant Roofing System
Handles document processing tasks via Celery workers
"""

import logging
import uuid
from celery import Task

from app.workers.celery_app import celery_app
from app.db.sync_session import SessionLocal
from app.models.core import Document

logger = logging.getLogger(__name__)


def _validate_and_get_uuid(document_id: str | uuid.UUID) -> uuid.UUID:
    """Validate string and convert to UUID object."""
    if isinstance(document_id, uuid.UUID):
        return document_id
    try:
        return uuid.UUID(document_id)
    except ValueError as e:
        logger.error(f"Invalid document ID format: {document_id}")
        raise ValueError(f"Invalid document ID format: {document_id}") from e


class DocumentProcessorTask(Task):
    """Task with enhanced error handling for document processing"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logger.error(f"Document processing task {task_id} failed: {exc}", exc_info=exc)
        # The error handling is already implemented in the PipelineTask base class
        # in new_pdf_processing.py, so we don't need to duplicate it here


@celery_app.task(base=DocumentProcessorTask, bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """
    This task acts as a dispatcher. It validates the document ID and
    queues the main processing task, ensuring the correct task context
    (e.g., failure handlers) is used.
    
    Args:
        document_id: UUID of the document to process
        
    Returns:
        A dictionary with the queued task's ID.
    """
    logger.info(f"Dispatching document for processing: {document_id}")
    document_uuid = _validate_and_get_uuid(document_id)

    try:
        # Import the target task to be queued
        from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline

        # Enqueue the main processing task. This is the correct "link".
        task = process_pdf_with_pipeline.delay(document_id=str(document_uuid))
        
        logger.info(f"Successfully queued document {document_id} for processing. Task ID: {task.id}")
        return {"status": "queued", "task_id": task.id}

    except Exception as e:
        logger.error(f"Failed to dispatch document {document_id} for processing: {e}", exc_info=True)
        # Retry the dispatch attempt with a short countdown
        countdown = 10 * (2**self.request.retries)
        raise self.retry(exc=e, countdown=countdown)

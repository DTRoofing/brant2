import asyncio
import json
import logging
import uuid
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from celery import Task, signals
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

try:
    from google.cloud import storage
    from google.api_core.exceptions import GoogleAPICallError, RetryError
    HAS_GOOGLE_CLOUD = True
except ImportError as import_err:
    import logging
    logging.warning("google.cloud.storage module is not installed. Please install the required dependency. Error: %s", import_err)
    storage = None
    GoogleAPICallError = Exception
    RetryError = Exception
    HAS_GOOGLE_CLOUD = False

# Type stubs for Google Cloud libraries
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from google.cloud.storage import Client as StorageClient
else:
    StorageClient = None

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.core import Document, ProcessingStatus
from app.models.results import ProcessingResults
from app.services.pdf_pipeline import pdf_pipeline

from sqlalchemy.engine.url import make_url
logger = logging.getLogger(__name__)

# Global variables for database connection
# These will be initialized per worker process
engine: Optional[Any] = None
SessionLocal: Optional[Any] = None

@signals.worker_process_init.connect
def init_worker(**kwargs):
    """
    Initialize database engine, session, and GCS client for each worker process.
    This prevents issues with forked connections from the parent process.
    """
    global engine, SessionLocal
    logger.info("Initializing connections for worker process...")
    
    # Create a robust synchronous database engine for Celery workers.
    # This logic mirrors the async setup, preventing inconsistencies.
    db_url = make_url(str(settings.DATABASE_URL))

    # Ensure the driver is synchronous for psycopg2
    if db_url.drivername.startswith("postgresql+asyncpg"):
        db_url = db_url.set(drivername="postgresql")
    
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600, # Recycle connections every hour to prevent stale connections
        echo=False  # Set to True for debugging
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Initialize all Google Cloud service clients for this worker process
    # This ensures that the singleton `google_service` has process-safe clients.
    from app.services.google_services import google_service
    google_service.initialize_clients()


@signals.worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """
    Dispose of the database engine when a worker process shuts down.
    """
    global engine
    if engine:
        logger.info("Disposing of database engine in worker process.")
        engine.dispose()


class PipelineTask(Task):
    """Task with enhanced error handling and progress tracking"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logger.error(f"Pipeline task {task_id} failed: {exc}")
        document_id = args[0] if args else kwargs.get('document_id')
        if document_id and SessionLocal:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == uuid.UUID(document_id)).with_for_update().first()
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = str(exc)
                    db.commit()


def _set_document_processing_status(document_id: str) -> Optional[str]:
    """Helper to set a document's status to PROCESSING and return its file path."""
    if not SessionLocal:
        raise RuntimeError("Database session not initialized")
    with SessionLocal() as db:
        doc_uuid = uuid.UUID(document_id)
        document = db.query(Document).filter(Document.id == doc_uuid).with_for_update().first()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        if document.processing_status in [ProcessingStatus.PROCESSING, ProcessingStatus.COMPLETED]:
            logger.warning(f"Document {document_id} already {document.processing_status.value}, skipping.")
            return None  # Indicate skipping

        document.processing_status = ProcessingStatus.PROCESSING
        document.processing_error = None
        file_path_str = document.file_path
        db.commit()
        return file_path_str


def _save_pipeline_results(document_id: str, result: Any):
    """Helper to save the results from a pipeline run to the database."""
    if not SessionLocal:
        raise RuntimeError("Database session not initialized")
    with SessionLocal() as db:
        doc_uuid = uuid.UUID(document_id)
        
        document = db.query(Document).filter(Document.id == doc_uuid).with_for_update().first()
        if not document:
            logger.error(f"Document {document_id} disappeared during processing.")
            return

        processing_results = db.query(ProcessingResults).filter(ProcessingResults.document_id == doc_uuid).first()
        if not processing_results:
            processing_results = ProcessingResults(document_id=doc_uuid)
            db.add(processing_results)
        
        # --- Complete data mapping from pipeline result to database model ---
        if result.final_estimate: # Check if final_estimate exists
            if result.final_estimate.processing_metadata:
                processing_results.project_metadata = result.final_estimate.processing_metadata
            if result.final_estimate.labor_estimate:
                processing_results.labor_estimate = result.final_estimate.labor_estimate.dict()

        if result.validated_data: # Check if validated_data exists
            cost_estimates = result.validated_data.cost_estimates or {}
            processing_results.roof_area_sqft = cost_estimates.get('total_area_sqft')
            processing_results.estimated_cost = cost_estimates.get('final_estimated_cost')
            processing_results.confidence_score = result.validated_data.quality_score
            processing_results.recommendations = result.validated_data.material_recommendations
            processing_results.warnings = result.validated_data.warnings
            processing_results.errors = result.validated_data.errors

        if result.ai_interpretation: # Check if ai_interpretation exists
            processing_results.materials = result.ai_interpretation.materials
            processing_results.roof_features = result.ai_interpretation.roof_features
            processing_results.complexity_factors = result.ai_interpretation.complexity_factors
            if result.ai_interpretation.metadata:
                processing_results.ai_interpretation = json.dumps(result.ai_interpretation.metadata)
            else:  # Fallback for older data or simpler interpretations
                interpretation_data = {
                    "roof_pitch": result.ai_interpretation.roof_pitch,
                    "confidence": result.ai_interpretation.confidence,
                    "materials": result.ai_interpretation.materials,
                    "special_requirements": result.ai_interpretation.special_requirements,
                    "damage_assessment": result.ai_interpretation.damage_assessment
                }
                processing_results.ai_interpretation = json.dumps(interpretation_data)

        if result.extracted_content: # Check if extracted_content exists
            processing_results.extraction_method = result.extracted_content.extraction_method

        processing_results.processing_time_seconds = result.processing_time_seconds
        processing_results.stages_completed = [stage.value for stage in result.stages_completed]

        # Ensure type safety by converting the pipeline's stage enum to the database's status enum.
        # This prevents potential TypeError if the enums are defined in different modules.
        document.processing_status = ProcessingStatus(result.current_stage.value)

        document.processing_error = "; ".join(result.errors) if result.errors else None
        db.commit()
        logger.info(f"Results for document {document_id} saved successfully.")

        # Add verification logging
        verify_result = db.query(ProcessingResults).filter(ProcessingResults.document_id == doc_uuid).first()
        if verify_result:
            logger.info(f"Verified: ProcessingResults saved with ID {verify_result.id}")
            logger.info(f"  - Roof area: {verify_result.roof_area_sqft}")
            logger.info(f"  - Cost: {verify_result.estimated_cost}")
            logger.info(f"  - Confidence: {verify_result.confidence_score}")
        else:
            logger.error(f"Verification failed: ProcessingResults not found after commit!")


def _cleanup_temporary_gcs_files(original_gcs_uri: str, pipeline_result: Any):
    """Deletes temporary GCS files created during selective page extraction."""
    if not pipeline_result or not pipeline_result.analysis or not pipeline_result.analysis.metadata:
        return

    processing_uri = pipeline_result.analysis.metadata.get('processing_file_path')

    # Check if a temporary file was used and needs cleanup.
    # The temporary file will be in the 'extracted/' folder.
    if processing_uri and processing_uri != original_gcs_uri and 'extracted/' in processing_uri:
        logger.info(f"Cleaning up temporary GCS file: {processing_uri}")
        from app.services.google_services import google_service
        if not google_service.storage_client:
            logger.warning("GCS client not available for cleanup, skipping.")
            return
        try:
            bucket = google_service.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
            
            # Extract object name from gs:// URI
            if processing_uri.startswith(f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/"):
                object_name = processing_uri[len(f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/"):]
                blob = bucket.blob(object_name)
                if blob.exists():
                    blob.delete()
                    logger.info(f"Successfully deleted temporary GCS object: {object_name}")
                else:
                    logger.warning(f"Temporary GCS object for deletion not found: {object_name}")
            else:
                 logger.warning(f"Processing URI {processing_uri} is not a valid GCS URI for this bucket.")

        except Exception as e:
            # Log as a warning because the main task succeeded.
            logger.warning(f"Failed to delete temporary GCS file {processing_uri}: {e}", exc_info=True)


def _execute_pipeline_task(task_instance: Task, document_id: str, gcs_object_name: str, processing_mode: str):
    """
    A generic, reusable function to execute the full processing pipeline for a document.
    This encapsulates the three main stages: setting status, running the pipeline, and saving results.

    Args:
        task_instance: The Celery task instance.
        document_id: The UUID of the document.
        gcs_object_name: The path to the document in GCS.
        processing_mode: The processing mode (e.g., 'standard', 'claude_only').
    """
    # --- Stage 1: Set status to PROCESSING ---
    try:
        # This function sets status to PROCESSING and prevents reprocessing.
        status_set_result = _set_document_processing_status(document_id)
        if not status_set_result:
            return {"status": "skipped", "message": "Document already processed or in progress."}
    except Exception as e:
        logger.error(f"Failed to start processing for {document_id}: {e}")
        raise task_instance.retry(exc=e, countdown=5)

    # --- Stage 2: Run the long-running pipeline ---
    try:
        # Construct the GCS URI, which is the standard for Google Cloud services.
        gcs_uri = f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/{gcs_object_name}"
        logger.info(f"Processing {gcs_uri} with mode: {processing_mode}")
        
        # Pass the GCS URI directly to the pipeline.
        # The underlying services (Document AI, Vision AI) will read from GCS.
        result = asyncio.run(pdf_pipeline.process_document(gcs_uri, document_id, processing_mode=processing_mode))
    except Exception as e:
        logger.error(f"Pipeline execution failed for {document_id} with mode {processing_mode}: {e}")
        raise task_instance.retry(exc=e, countdown=2 ** task_instance.request.retries)

    # --- Stage 3: Save results and final status with a lock ---
    try:
        logger.info(f"Starting database save for document {document_id}")
        _save_pipeline_results(document_id, result)
    except Exception as e:
        logger.error(f"Failed to save results for {document_id}: {e}")
        raise task_instance.retry(exc=e, countdown=2 ** task_instance.request.retries)

    # --- Stage 4: Cleanup temporary files ---
    # This is a best-effort cleanup. We don't want the task to fail if cleanup fails.
    try:
        _cleanup_temporary_gcs_files(gcs_uri, result)
    except Exception as e:
        logger.warning(f"An unexpected error occurred during GCS cleanup for doc {document_id}: {e}", exc_info=True)

    return {
        "document_id": document_id,
        "status": "completed",
        "stages_completed": [stage.value for stage in result.stages_completed],
        "final_estimate": result.final_estimate.dict() if result.final_estimate else None,
        "processing_time_seconds": result.processing_time_seconds,
        "errors": result.errors
    }


@celery_app.task(base=PipelineTask, bind=True, max_retries=3)
def process_pdf_with_pipeline(self, document_id: str, processing_options: Optional[Dict[str, Any]] = None):
    """
    Process a PDF document using the new multi-stage pipeline
    
    Args:
        document_id: UUID of the document to process
        processing_options: Optional processing options including mode
        
    Returns:
        ProcessingResult with all stage results
    """
    logger.info(f"Starting new pipeline processing for document {document_id}")
    processing_mode = processing_options.get("mode", "standard") if processing_options else "standard"

    # Fetch the GCS object name from the database to maintain a consistent API.
    if not SessionLocal:
        raise RuntimeError("Database session not initialized")
    with SessionLocal() as db:
        doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found for pipeline.")
        gcs_object_name = doc.file_path
    return _execute_pipeline_task(self, document_id, gcs_object_name, processing_mode)


@celery_app.task
def cleanup_failed_documents():
    """
    Clean up documents that have been in failed state for too long
    """
    if not SessionLocal:
        logger.error("Database session not initialized for cleanup_failed_documents")
        return
    with SessionLocal() as db:
        # Find documents that have been failed for more than 24 hours
        cleanup_hours = settings.FAILED_DOC_CLEANUP_HOURS
        cutoff_date = datetime.utcnow() - timedelta(hours=cleanup_hours)
        
        failed_documents = db.query(Document).filter(
            Document.processing_status == ProcessingStatus.FAILED,
            Document.updated_at < cutoff_date
        ).all()
        
        from app.services.google_services import google_service
        if not google_service.storage_client:
            logger.warning("GCS client not available for cleanup_failed_documents, aborting.")
            return

        bucket = google_service.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
        for doc in failed_documents:
            if doc.file_path:
                try:
                    # Use the shared client and bucket
                    blob = bucket.blob(doc.file_path)
                    if blob.exists():
                        blob.delete()
                        logger.info(f"Deleted GCS object {doc.file_path} for failed document {doc.id}")
                except Exception as e:
                    logger.error(f"Failed to delete GCS object {doc.file_path} for doc {doc.id}: {e}")

            # Delete from database
            db.delete(doc)
        
        db.commit()
        logger.info(f"Cleaned up {len(failed_documents)} documents that failed more than {cleanup_hours} hours ago.")


@celery_app.task
def generate_processing_report():
    """
    Generate a report of processing statistics
    """
    if not SessionLocal:
        logger.error("Database session not initialized for generate_processing_report")
        return {"error": "Database not initialized"}
    with SessionLocal() as db:
        
        # Get processing statistics
        stats = db.query(
            Document.processing_status,
            func.count(Document.id).label('count')
        ).group_by(Document.processing_status).all()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status_counts": {status.value: count for status, count in stats},
            "total_documents": sum(count for _, count in stats)
        }
        
        logger.info(f"Processing report: {report}")
        return report


@celery_app.task(base=PipelineTask, bind=True, max_retries=3)
def process_document_with_claude_direct(self, document_id: str):
    """
    Process a document directly with Claude AI (bypassing Google Document AI)
    
    Args:
        document_id: UUID of the document to process
        
    Returns:
        ProcessingResult with Claude AI interpretation
    """
    logger.info(f"Starting direct Claude processing for document {document_id}")

    # Fetch the GCS object name from the database to maintain a consistent API.
    if not SessionLocal:
        raise RuntimeError("Database session not initialized")
    with SessionLocal() as db:
        doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found for claude_only pipeline.")
        gcs_object_name = doc.file_path
    return _execute_pipeline_task(self, document_id, gcs_object_name, processing_mode="claude_only")
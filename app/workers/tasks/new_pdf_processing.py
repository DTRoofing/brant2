import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.core import Document, ProcessingStatus
from app.services.pdf_pipeline import pdf_pipeline

logger = logging.getLogger(__name__)

# Create synchronous database engine for Celery workers
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PipelineTask(Task):
    """Task with enhanced error handling and progress tracking"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure"""
        logger.error(f"Pipeline task {task_id} failed: {exc}")
        document_id = kwargs.get('document_id')
        if document_id:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = str(exc)
                    db.commit()
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on task success"""
        logger.info(f"Pipeline task {task_id} completed successfully")
        document_id = kwargs.get('document_id')
        if document_id:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.processing_status = ProcessingStatus.COMPLETED
                    document.processing_error = None
                    db.commit()


@celery_app.task(base=PipelineTask, bind=True, max_retries=3)
def process_pdf_with_pipeline(self, document_id: str):
    """
    Process a PDF document using the new multi-stage pipeline
    
    Args:
        document_id: UUID of the document to process
        
    Returns:
        ProcessingResult with all stage results
    """
    logger.info(f"Starting new pipeline processing for document {document_id}")
    
    with SessionLocal() as db:
        try:
            # Get document from database with lock to prevent race conditions
            document = db.query(Document).filter(
                Document.id == uuid.UUID(document_id)
            ).with_for_update().first()
            
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Check if already processing or completed to prevent duplicate processing
            if document.processing_status in [ProcessingStatus.PROCESSING, ProcessingStatus.COMPLETED]:
                logger.warning(f"Document {document_id} already {document.processing_status.value}, skipping")
                return {
                    "document_id": document_id,
                    "status": document.processing_status.value,
                    "message": f"Document already {document.processing_status.value}"
                }
            
            # Update status to processing
            document.processing_status = ProcessingStatus.PROCESSING
            db.commit()
            
            # Check if file exists
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Process with new pipeline using asyncio.run()
            logger.info(f"Processing {file_path} with new pipeline")
            result = asyncio.run(pdf_pipeline.process_document(str(file_path), document_id))
            
            # Store results in database
            from app.models.results import ProcessingResults
            
            logger.info(f"Pipeline completed for document {document_id}")
            logger.info(f"Stages completed: {result.stages_completed}")
            logger.info(f"Final estimate: {result.final_estimate}")
            
            # Create or update processing results
            existing_results = db.query(ProcessingResults).filter(
                ProcessingResults.document_id == uuid.UUID(document_id)
            ).first()
            
            if existing_results:
                # Update existing results
                processing_results = existing_results
            else:
                # Create new results
                processing_results = ProcessingResults(document_id=uuid.UUID(document_id))
                db.add(processing_results)
            
            # Populate results from pipeline
            if result.final_estimate:
                processing_results.roof_area_sqft = result.final_estimate.total_area_sqft
                processing_results.estimated_cost = result.final_estimate.estimated_cost
                processing_results.confidence_score = result.final_estimate.confidence_score
                processing_results.materials = [m.dict() for m in result.final_estimate.materials_needed] if result.final_estimate.materials_needed else []
                processing_results.processing_time_seconds = result.processing_time_seconds
                processing_results.stages_completed = [stage.value for stage in result.stages_completed]
                processing_results.extraction_method = 'hybrid'  # or detect from result
                
                # Store metadata
                if hasattr(result.final_estimate, 'processing_metadata'):
                    metadata = result.final_estimate.processing_metadata
                    processing_results.warnings = metadata.get('warnings', [])
                    processing_results.errors = metadata.get('errors', [])
            
            # Update document status
            if result.current_stage == ProcessingStatus.COMPLETED:
                document.processing_status = ProcessingStatus.COMPLETED
            else:
                document.processing_status = ProcessingStatus.FAILED
                document.processing_error = "; ".join(result.errors)
            
            db.commit()
            
            return {
                "document_id": document_id,
                "status": "completed",
                "stages_completed": [stage.value for stage in result.stages_completed],
                "final_estimate": result.final_estimate.dict() if result.final_estimate else None,
                "processing_time_seconds": result.processing_time_seconds,
                "errors": result.errors
            }
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for document {document_id}: {e}")
            
            # Update document with error (with lock)
            document = db.query(Document).filter(
                Document.id == uuid.UUID(document_id)
            ).with_for_update().first()
            
            if document:
                document.processing_status = ProcessingStatus.FAILED
                document.processing_error = str(e)
                db.commit()
            
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task
def process_document_stage(stage_name: str, document_id: str, stage_data: Dict[str, Any]):
    """
    Process a single stage of the pipeline (for debugging or manual processing)
    
    Args:
        stage_name: Name of the stage to process
        document_id: UUID of the document
        stage_data: Data from previous stages
    """
    logger.info(f"Processing stage {stage_name} for document {document_id}")
    
    try:
        # This would be used for individual stage processing
        # Useful for debugging or manual stage execution
        pass
        
    except Exception as e:
        logger.error(f"Stage {stage_name} failed for document {document_id}: {e}")
        raise


@celery_app.task
def cleanup_failed_documents():
    """
    Clean up documents that have been in failed state for too long
    """
    with SessionLocal() as db:
        # Find documents that have been failed for more than 24 hours
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        
        failed_documents = db.query(Document).filter(
            Document.processing_status == ProcessingStatus.FAILED,
            Document.updated_at < cutoff_date
        ).all()
        
        for doc in failed_documents:
            # Delete file from disk
            file_path = Path(doc.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            db.delete(doc)
        
        db.commit()
        logger.info(f"Cleaned up {len(failed_documents)} failed documents")


@celery_app.task
def generate_processing_report():
    """
    Generate a report of processing statistics
    """
    from sqlalchemy import func
    
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

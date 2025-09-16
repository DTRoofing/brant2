import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

from celery import Task, signals
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.core import Document, ProcessingStatus
from app.services.pdf_pipeline import pdf_pipeline

logger = logging.getLogger(__name__)

# Global variables for database connection
# These will be initialized per worker process
engine = None
SessionLocal = None

@signals.worker_process_init.connect
def init_worker(**kwargs):
    """
    Initialize database engine and session for each worker process.
    This prevents issues with forked connections from the parent process.
    """
    global engine, SessionLocal
    logger.info("Initializing database connection for worker process...")
    
    # Create synchronous database engine for Celery workers with proper SSL
    # Convert async URL to sync URL and ensure SSL is enabled
    database_url = str(settings.DATABASE_URL)
    if "postgresql://" not in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    if "sslmode=" not in database_url:
        database_url += ("&" if "?" in database_url else "?") + "sslmode=require"
    
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,
        max_overflow=10,
        echo=False  # Set to True for debugging
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection for worker process initialized.")

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
        if document_id:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == uuid.UUID(document_id)).with_for_update().first()
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = str(exc)
                    db.commit()


@celery_app.task(base=PipelineTask, bind=True, max_retries=3)
def process_pdf_with_pipeline(self, document_id: str, processing_options: Dict[str, Any] = None):
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
    logger.info(f"Processing mode: {processing_mode}")
    
    # --- Stage 1: Set status to PROCESSING ---
    try:
        with SessionLocal() as db:
            doc_uuid = uuid.UUID(document_id)
            document = db.query(Document).filter(Document.id == doc_uuid).with_for_update().first()

            if not document:
                raise ValueError(f"Document {document_id} not found")

            if document.processing_status in [ProcessingStatus.PROCESSING, ProcessingStatus.COMPLETED]:
                logger.warning(f"Document {document_id} already {document.processing_status.value}, skipping.")
                return {"status": "skipped", "message": f"Document already {document.processing_status.value}"}

            document.processing_status = ProcessingStatus.PROCESSING
            document.processing_error = None
            file_path_str = document.file_path
            db.commit()
    except Exception as e:
        logger.error(f"Failed to start processing for {document_id}: {e}")
        raise self.retry(exc=e, countdown=5)

    # --- Stage 2: Run the long-running pipeline ---
    try:
        file_path = Path(file_path_str)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info(f"Processing {file_path} with new pipeline")
        
        # Check if we should use the Claude/YOLO processor
        if processing_mode == "claude_yolo":
            logger.info(f"Using Claude/YOLO processor for document {document_id}")
            from app.services.processing_stages.claude_yolo_processor import ClaudeYOLOProcessor
            
            # Read PDF content
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            # Process with Claude/YOLO
            processor = ClaudeYOLOProcessor()
            result = asyncio.run(processor.process_schematic_pdf(
                pdf_content,
                document_id,
                document_type="schematic",
                processing_options=processing_options
            ))
        else:
            # Use standard pipeline
            result = asyncio.run(pdf_pipeline.process_document(str(file_path), document_id))
    except Exception as e:
        logger.error(f"Pipeline execution failed for {document_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

    # --- Stage 3: Save results and final status with a lock ---
    try:
        logger.info(f"Starting database save for document {document_id}")
        with SessionLocal() as db:
            from app.models.results import ProcessingResults
            doc_uuid = uuid.UUID(document_id)
            
            # Test database connection
            try:
                db.execute(text("SELECT 1"))
                logger.info("Database connection verified")
            except Exception as e:
                logger.error(f"Database connection test failed: {e}")
                raise
            
            # Lock the document row before final update
            document = db.query(Document).filter(Document.id == doc_uuid).with_for_update().first()
            if not document:
                logger.error(f"Document {document_id} disappeared during processing.")
                return

            # Create or update processing results
            processing_results = db.query(ProcessingResults).filter(ProcessingResults.document_id == doc_uuid).first()
            if not processing_results:
                logger.info(f"Creating new ProcessingResults for document {document_id}")
                processing_results = ProcessingResults(document_id=doc_uuid)
                db.add(processing_results)
            else:
                logger.info(f"Updating existing ProcessingResults for document {document_id}")
            
            # Handle Claude/YOLO results differently
            if processing_mode == "claude_yolo" and hasattr(result, 'result'):
                # Extract data from Claude/YOLO result format
                claude_yolo_data = result.result
                
                # Roof analysis data
                if "roofing_analysis" in claude_yolo_data:
                    analysis = claude_yolo_data["roofing_analysis"]
                    chars = analysis.get("roof_characteristics", {})
                    processing_results.roof_area_sqft = chars.get("total_area", 0)
                    
                    # Materials from analysis
                    material_analysis = analysis.get("material_analysis", {})
                    materials = []
                    for rec in material_analysis.get("recommendations", []):
                        materials.append({
                            "type": rec.get("category", ""),
                            "name": rec.get("recommendation", ""),
                            "details": rec.get("details", {})
                        })
                    processing_results.materials = materials
                    
                    # Features
                    processing_results.roof_features = [
                        {"type": k, "count": v} 
                        for k, v in analysis.get("feature_summary", {}).items()
                    ]
                    
                    # Complexity factors
                    complexity = chars.get("complexity", "medium")
                    processing_results.complexity_factors = [
                        f"Complexity: {complexity}",
                        f"Roof Type: {chars.get('type', 'unknown')}",
                        f"Primary Pitch: {chars.get('primary_pitch', 'unknown')}"
                    ]
                    
                    # Special considerations as recommendations
                    processing_results.recommendations = analysis.get("special_considerations", [])
                
                # Store full Claude/YOLO data as AI interpretation
                import json
                processing_results.ai_interpretation = json.dumps(claude_yolo_data)
                
                # Confidence and processing time
                processing_results.confidence_score = result.confidence_score
                processing_results.processing_time_seconds = result.processing_time_seconds
                processing_results.extraction_method = "claude_yolo"
                
                # Calculate estimated cost based on area and complexity
                if processing_results.roof_area_sqft:
                    base_cost_per_sqft = 5.50  # Base rate
                    complexity_multiplier = {"low": 1.0, "medium": 1.15, "high": 1.3}.get(complexity, 1.15)
                    processing_results.estimated_cost = processing_results.roof_area_sqft * base_cost_per_sqft * complexity_multiplier
            else:
                # Populate results from standard pipeline
                if result.final_estimate:
                    # Core measurements
                    processing_results.roof_area_sqft = result.final_estimate.total_area_sqft
                    processing_results.estimated_cost = result.final_estimate.estimated_cost
                    processing_results.confidence_score = result.final_estimate.confidence_score
                    
                    # Materials and labor
                    processing_results.materials = result.final_estimate.materials_needed
                    
                    # Timeline and metadata from final estimate
                    if hasattr(result.final_estimate, 'processing_metadata'):
                        processing_results.processing_time_seconds = result.processing_time_seconds
                
                # AI interpretation data
                if result.ai_interpretation:
                    processing_results.roof_features = result.ai_interpretation.roof_features
                    processing_results.complexity_factors = result.ai_interpretation.complexity_factors
                    # FIX: Preserve the full AI interpretation for downstream analysis (e.g., McDonald's detection)
                    # Store the complete interpretation data as JSON instead of just a summary string
                    if hasattr(result.ai_interpretation, 'metadata') and result.ai_interpretation.metadata:
                        import json
                        processing_results.ai_interpretation = json.dumps(result.ai_interpretation.metadata)
                    else:
                        # Fallback to structured data if no metadata
                        interpretation_data = {
                            "roof_pitch": result.ai_interpretation.roof_pitch,
                            "confidence": result.ai_interpretation.confidence,
                            "materials": result.ai_interpretation.materials,
                            "special_requirements": result.ai_interpretation.special_requirements,
                            "damage_assessment": result.ai_interpretation.damage_assessment
                        }
                        import json
                        processing_results.ai_interpretation = json.dumps(interpretation_data)
                
                # Extraction method and processing metadata
                if result.extracted_content:
                    processing_results.extraction_method = result.extracted_content.extraction_method
                
                # Validation results and recommendations
                if result.validated_data:
                    processing_results.recommendations = result.validated_data.material_recommendations
                    processing_results.warnings = result.validated_data.warnings
                    processing_results.errors = result.validated_data.errors
                
                # Processing timeline and stages
                processing_results.processing_time_seconds = result.processing_time_seconds
                processing_results.stages_completed = [stage.value for stage in result.stages_completed]

            # Update final document status
            if processing_mode == "claude_yolo":
                # For Claude/YOLO, check status field
                if result.status == "completed":
                    document.processing_status = ProcessingStatus.COMPLETED
                    document.processing_error = None
                else:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = "; ".join(result.errors) if result.errors else "Processing failed"
            else:
                # Standard pipeline status
                if result.current_stage == ProcessingStatus.COMPLETED:
                    document.processing_status = ProcessingStatus.COMPLETED
                    document.processing_error = None
                else:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = "; ".join(result.errors)

            # Explicitly commit the transaction with logging
            logger.info(f"Committing transaction for document {document_id}")
            db.commit()
            logger.info(f"Transaction committed successfully for document {document_id}")
            
            # Verify the data was saved
            verify_result = db.query(ProcessingResults).filter(ProcessingResults.document_id == doc_uuid).first()
            if verify_result:
                logger.info(f"Verified: ProcessingResults saved with ID {verify_result.id}")
                logger.info(f"  - Roof area: {verify_result.roof_area_sqft}")
                logger.info(f"  - Cost: {verify_result.estimated_cost}")
                logger.info(f"  - Confidence: {verify_result.confidence_score}")
            else:
                logger.error(f"Verification failed: ProcessingResults not found after commit!")

    except Exception as e:
        logger.error(f"Failed to save results for {document_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

    if processing_mode == "claude_yolo":
        return {
            "document_id": document_id,
            "status": result.status,
            "processing_mode": "claude_yolo",
            "stages_completed": result.result.get("processing_stages", []),
            "processing_time_seconds": result.processing_time_seconds,
            "errors": result.errors
        }
    else:
        return {
            "document_id": document_id,
            "status": "completed",
            "stages_completed": [stage.value for stage in result.stages_completed],
            "final_estimate": result.final_estimate.dict() if result.final_estimate else None,
            "processing_time_seconds": result.processing_time_seconds,
            "errors": result.errors
        }



@celery_app.task
def cleanup_failed_documents():
    """
    Clean up documents that have been in failed state for too long
    """
    with SessionLocal() as db:
        # Find documents that have been failed for more than 24 hours
        cleanup_hours = settings.FAILED_DOC_CLEANUP_HOURS
        cutoff_date = datetime.utcnow() - timedelta(hours=cleanup_hours)
        
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
        logger.info(f"Cleaned up {len(failed_documents)} documents that failed more than {cleanup_hours} hours ago.")


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

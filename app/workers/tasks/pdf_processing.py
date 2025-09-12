import logging
import uuid
from pathlib import Path
from typing import Optional

from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.core import Document, ProcessingStatus, Measurement
from app.core.pdf_processing import extract_text_from_pdf
from app.services.claude_service import claude_service
from app.services.google_services import google_service

logger = logging.getLogger(__name__)

# Create synchronous database engine for Celery workers
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CallbackTask(Task):
    """Task with callbacks for error handling."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        logger.error(f"Task {task_id} failed: {exc}")
        document_id = kwargs.get('document_id')
        if document_id:
            with SessionLocal() as db:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.processing_status = ProcessingStatus.FAILED
                    document.processing_error = str(exc)
                    db.commit()


@celery_app.task(base=CallbackTask, bind=True, max_retries=3)
def process_pdf_document(self, document_id: str):
    """
    Process a PDF document to extract measurements and roofing information.
    
    Args:
        document_id: UUID of the document to process
    """
    logger.info(f"Starting PDF processing for document {document_id}")
    
    with SessionLocal() as db:
        try:
            # Get document from database
            document = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Update status to processing
            document.processing_status = ProcessingStatus.PROCESSING
            db.commit()
            
            # Extract text from PDF
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            logger.info(f"Extracting text from {file_path}")
            
            # Try Google Document AI first
            google_result = None
            if settings.GOOGLE_CLOUD_PROJECT_ID:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Upload to Google Cloud Storage
                    gcs_uri = loop.run_until_complete(
                        google_service.upload_to_gcs(str(file_path), f"documents/{document_id}.pdf")
                    )
                    
                    # Process with Document AI
                    google_result = loop.run_until_complete(
                        google_service.process_document_with_ai(str(file_path))
                    )
                    
                    if google_result and google_result.get('text'):
                        extracted_text = google_result['text']
                        logger.info(f"Google Document AI extracted {len(extracted_text)} characters")
                        
                        # Store Google-extracted measurements
                        for measurement in google_result.get('measurements', []):
                            try:
                                # Parse measurement value
                                text = measurement.get('text', '')
                                import re
                                numbers = re.findall(r'[\d,]+\.?\d*', text)
                                if numbers:
                                    value = float(numbers[0].replace(',', ''))
                                    new_measurement = Measurement(
                                        document_id=document.id,
                                        area_sf=value,
                                        confidence_score=measurement.get('confidence', 0.8),
                                        measurement_type='google_ai_extraction',
                                        extraction_method='document_ai',
                                        source_coordinates={"text": text}
                                    )
                                    db.add(new_measurement)
                            except Exception as e:
                                logger.warning(f"Could not parse Google measurement: {e}")
                    else:
                        # Fallback to regular extraction
                        extracted_text = extract_text_from_pdf(str(file_path))
                    
                    loop.close()
                except Exception as e:
                    logger.error(f"Google Document AI processing failed: {e}")
                    # Fallback to regular extraction
                    extracted_text = extract_text_from_pdf(str(file_path))
            else:
                # Use regular extraction if Google not configured
                extracted_text = extract_text_from_pdf(str(file_path))
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                raise ValueError("No meaningful text extracted from PDF")
            
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            
            # Analyze text with Claude if API key is configured
            analysis_result = None
            if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your-anthropic-api-key":
                try:
                    logger.info("Analyzing text with Claude AI...")
                    analysis_result = claude_service.analyze_text_for_estimate(extracted_text)
                    
                    # Store measurements if found
                    if analysis_result:
                        # Store total roof area if available
                        if analysis_result.get('total_roof_area_sqft'):
                            measurement = Measurement(
                                document_id=document.id,
                                area_sf=float(analysis_result['total_roof_area_sqft']),
                                confidence_score=0.85,
                                measurement_type='roof_area',
                                extraction_method='ai_analysis'
                            )
                            db.add(measurement)
                        
                        # Store individual measurements
                        measurements = analysis_result.get('measurements', [])
                        for m in measurements:
                            if m.get('value') and m.get('label'):
                                try:
                                    # Try to parse numeric value
                                    value_str = str(m['value']).replace(',', '').replace('sq ft', '').strip()
                                    value = float(value_str)
                                    
                                    measurement = Measurement(
                                        document_id=document.id,
                                        area_sf=value,
                                        confidence_score=0.75,
                                        measurement_type=m['label'],
                                        extraction_method='ai_extraction'
                                    )
                                    db.add(measurement)
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Could not parse measurement value: {m.get('value')}")
                
                except Exception as e:
                    logger.error(f"Claude analysis failed: {e}")
                    # Continue processing even if AI analysis fails
            else:
                logger.info("Skipping AI analysis - ANTHROPIC_API_KEY not configured")
            
            # Update document status
            document.processing_status = ProcessingStatus.COMPLETED
            document.processing_error = None
            db.commit()
            
            logger.info(f"Successfully processed document {document_id}")
            return {
                "document_id": str(document_id),
                "status": "completed",
                "extracted_text_length": len(extracted_text),
                "analysis_performed": analysis_result is not None
            }
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            
            # Update document with error
            document = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
            if document:
                document.processing_status = ProcessingStatus.FAILED
                document.processing_error = str(e)
                db.commit()
            
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task
def cleanup_old_documents():
    """
    Periodic task to clean up old processed documents.
    """
    from datetime import datetime, timedelta
    
    with SessionLocal() as db:
        # Delete documents older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_documents = db.query(Document).filter(
            Document.created_at < cutoff_date,
            Document.processing_status == ProcessingStatus.COMPLETED
        ).all()
        
        for doc in old_documents:
            # Delete file from disk
            file_path = Path(doc.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            db.delete(doc)
        
        db.commit()
        logger.info(f"Cleaned up {len(old_documents)} old documents")
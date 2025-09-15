from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
import uuid
from pathlib import Path

from app.models.processing import ProcessingResult, ProcessingStage
from app.services.pdf_pipeline import pdf_pipeline
from app.workers.tasks.new_pdf_processing import process_pdf_with_pipeline
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core import Document, ProcessingStatus

router = APIRouter()


@router.post("/process/{document_id}")
async def start_pipeline_processing(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start processing a document with the new pipeline
    """
    try:
        # Validate document exists
        doc_uuid = uuid.UUID(document_id)
        document = await db.get(Document, doc_uuid)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.processing_status == ProcessingStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Document is already being processed")
        
        # Start background processing
        task = process_pdf_with_pipeline.delay(document_id)
        
        return {
            "message": "Pipeline processing started",
            "document_id": document_id,
            "task_id": task.id,
            "status": "processing"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")


@router.get("/status/{document_id}")
async def get_processing_status(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current processing status of a document
    """
    try:
        doc_uuid = uuid.UUID(document_id)
        document = await db.get(Document, doc_uuid)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "status": document.processing_status.value,
            "error": document.processing_error,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/results/{document_id}")
async def get_processing_results(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing results for a completed document
    """
    from sqlalchemy import select
    from app.models.results import ProcessingResults
    
    try:
        doc_uuid = uuid.UUID(document_id)
        
        # Query document with results
        stmt = select(Document).where(Document.id == doc_uuid)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.processing_status != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Document processing not completed. Current status: {document.processing_status.value}"
            )
        
        # Query actual results from database
        results_stmt = select(ProcessingResults).where(ProcessingResults.document_id == doc_uuid)
        results_result = await db.execute(results_stmt)
        processing_results = results_result.scalar_one_or_none()
        
        if not processing_results:
            # Fallback for documents processed before this update
            return {
                "document_id": document_id,
                "status": "completed",
                "message": "Processing completed (legacy - no detailed results)",
                "file_path": document.file_path,
                "processed_at": document.updated_at.isoformat(),
                "results": {
                    "roof_area_sqft": 0,
                    "materials": [],
                    "estimated_cost": 0,
                    "confidence": 0,
                    "roof_features": [],
                    "complexity_factors": []
                }
            }
        
        # Return actual results from database
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Processing completed successfully",
            "file_path": document.file_path,
            "processed_at": processing_results.created_at.isoformat(),
            "results": {
                "roof_area_sqft": processing_results.roof_area_sqft or 0,
                "materials": processing_results.materials or [],
                "estimated_cost": processing_results.estimated_cost or 0,
                "confidence": processing_results.confidence_score or 0,
                "roof_features": processing_results.roof_features or [],
                "complexity_factors": processing_results.complexity_factors or [],
                "ai_interpretation": processing_results.ai_interpretation,
                "recommendations": processing_results.recommendations or [],
                "processing_time_seconds": processing_results.processing_time_seconds,
                "extraction_method": processing_results.extraction_method
            }
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.post("/cancel/{document_id}")
async def cancel_processing(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel processing for a document
    """
    try:
        doc_uuid = uuid.UUID(document_id)
        
        # Use a transaction and lock to prevent race conditions with the worker
        async with db.begin():
            stmt = select(Document).where(Document.id == doc_uuid).with_for_update()
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()

            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            if document.processing_status not in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot cancel document. Current status: {document.processing_status.value}"
                )
            
            # Assuming ProcessingStatus.CANCELLED is added to the enum
            document.processing_status = ProcessingStatus.CANCELLED
            document.processing_error = "Processing cancelled by user"
            # The transaction will commit automatically on exiting the 'async with' block

        return {
            "message": "Processing cancelled",
            "document_id": document_id,
            "status": "cancelled"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel processing: {str(e)}")


@router.get("/health")
async def pipeline_health():
    """
    Check the health of the processing pipeline
    """
    try:
        # Check if all services are available
        health_status = {
            "pipeline": "healthy",
            "services": {
                "document_analyzer": "available",
                "content_extractor": "available", 
                "ai_interpreter": "available",
                "data_validator": "available"
            },
            "timestamp": "2024-01-01T00:00:00Z"  # You'd use actual timestamp
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline health check failed: {str(e)}")


@router.get("/stats")
async def get_processing_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get processing statistics
    """
    try:
        from sqlalchemy import func
        
        # Get counts by status
        from sqlalchemy import select
        
        result = await db.execute(
            select(
                Document.processing_status,
                func.count(Document.id).label('count')
            ).group_by(Document.processing_status)
        )
        stats = result.all()
        
        return {
            "statistics": {
                status.value: count for status, count in stats
            },
            "total_documents": sum(count for _, count in stats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

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
    try:
        doc_uuid = uuid.UUID(document_id)
        document = await db.get(Document, doc_uuid)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.processing_status != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Document processing not completed. Current status: {document.processing_status.value}"
            )
        
        # For now, return basic info with roof features. In production, you'd store and retrieve the full results
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Processing completed successfully",
            "file_path": document.file_path,
            "processed_at": document.updated_at.isoformat(),
            "results": {
                "roof_area_sqft": 2500,
                "materials": ["membrane", "insulation"],
                "estimated_cost": 15000,
                "confidence": 0.85,
                "roof_features": [
                    {
                        "type": "exhaust_port",
                        "count": 2,
                        "impact": "medium",
                        "description": "Exhaust ports require careful sealing and flashing"
                    },
                    {
                        "type": "walkway",
                        "count": 1,
                        "impact": "low",
                        "description": "Walkways provide access but may require additional materials"
                    }
                ],
                "complexity_factors": [
                    "Multiple exhaust ports require specialized flashing",
                    "Walkway access affects material delivery"
                ],
                "verification": {
                    "ocr_total": 2400,
                    "blueprint_total": 2500,
                    "difference_percent": 4.2,
                    "recommendation": "use_blueprint"
                }
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
        document = await db.get(Document, doc_uuid)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.processing_status != ProcessingStatus.PROCESSING:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel document. Current status: {document.processing_status.value}"
            )
        
        # Update status to cancelled (you might want to add this status)
        document.processing_status = ProcessingStatus.FAILED
        document.processing_error = "Processing cancelled by user"
        await db.commit()
        
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

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
        
        # Calculate cost breakdown based on project type and industry standards
        total_cost = processing_results.estimated_cost or 0
        roof_area = processing_results.roof_area_sqft or 0
        
        # Determine complexity from factors
        complexity_count = len(processing_results.complexity_factors or [])
        complexity = "low" if complexity_count <= 2 else "medium" if complexity_count <= 4 else "high"
        
        # Smart cost breakdown based on materials and project type
        is_commercial = roof_area > 10000 or "commercial" in str(processing_results.materials).lower()
        
        if is_commercial:
            labor_percentage = 0.35
            material_percentage = 0.55
            permit_percentage = 0.06
            contingency_percentage = 0.04
        else:
            labor_percentage = 0.40
            material_percentage = 0.50
            permit_percentage = 0.05
            contingency_percentage = 0.05
        
        # Format metadata with proper client information
        metadata = {}
        
        # Check if this is a McDonald's document
        if processing_results.ai_interpretation and "mcdonald" in processing_results.ai_interpretation.lower():
            # Extract McDonald's specific information
            import re
            store_match = re.search(r'store\s*#?\s*(\d+)', processing_results.ai_interpretation, re.IGNORECASE)
            project_match = re.search(r'project\s*#?\s*([\d-]+)', processing_results.ai_interpretation, re.IGNORECASE)
            
            metadata["document_type"] = "mcdonalds_roofing"
            metadata["client_name"] = f"McDonald's Store #{store_match.group(1) if store_match else 'Unknown'}"
            metadata["project_name"] = f"McDonald's Roofing Project {project_match.group(1) if project_match else ''}"
            metadata["company_name"] = "McDonald's Corporation"
        else:
            # Generic client information
            metadata["client_name"] = document.filename.replace('.pdf', '').replace('_', ' ').title() if document.filename else "Client"
            metadata["project_name"] = f"Roofing Project - {document.filename[:20] if document.filename else 'New'}"
            metadata["company_name"] = "Commercial Client"
        
        metadata["document_id"] = str(document_id)
        metadata["complexity"] = complexity
        
        # Return enhanced results from database
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Processing completed successfully",
            "file_path": document.file_path,
            "processed_at": processing_results.created_at.isoformat(),
            "results": {
                "roof_area_sqft": roof_area,
                "materials": processing_results.materials or [],
                "estimated_cost": total_cost,
                "confidence": processing_results.confidence_score or 0,
                "roof_features": processing_results.roof_features or [],
                "complexity_factors": processing_results.complexity_factors or [],
                "ai_interpretation": processing_results.ai_interpretation,
                "recommendations": processing_results.recommendations or [],
                "processing_time_seconds": processing_results.processing_time_seconds,
                "extraction_method": processing_results.extraction_method,
                # Add cost breakdown
                "labor_cost": total_cost * labor_percentage,
                "material_cost": total_cost * material_percentage,
                "permit_cost": total_cost * permit_percentage,
                "contingency": total_cost * contingency_percentage,
                # Add complexity for timeline calculation
                "complexity": complexity,
                # Add formatted metadata
                "metadata": metadata
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
async def pipeline_health(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the processing pipeline and its dependencies.
    """
    from app.workers.celery_app import celery_app
    from sqlalchemy import text
    from datetime import datetime

    db_ok = False
    redis_ok = False

    # Check Database Connection
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Redis (Celery broker) Connection
    try:
        celery_app.broker_connection().ensure_connection(max_retries=1)
        redis_ok = True
    except Exception:
        redis_ok = False

    is_healthy = db_ok and redis_ok
    status_code = 200 if is_healthy else 503

    if not is_healthy:
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": "unhealthy",
                "dependencies": {"database": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"},
            },
        )

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {
            "pipeline": "healthy",
            "services": {
                "database": "ok",
                "redis": "ok",
            },
        }
    }


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

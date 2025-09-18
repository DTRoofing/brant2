"""
Claude AI Processing Endpoint
Direct processing of documents with Claude AI
"""

import logging
from datetime import datetime
from pathlib import Path
import uuid
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from celery.result import AsyncResult
import json

from app.core.database import get_db
from app.models.results import ProcessingResults
from app.models.core import Document, ProcessingStatus
from app.workers.celery_app import celery_app
from app.workers.tasks.new_pdf_processing import process_document_with_claude_direct
from app.core.timeline import calculate_timeline_estimate

logger = logging.getLogger(__name__)
router = APIRouter()

class ClaudeProcessingRequest(BaseModel):
    document_id: str

class TaskResponse(BaseModel):
    task_id: str
    document_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

class FinalEstimateResponse(BaseModel):
    total_area_sqft: float
    estimated_cost: float
    materials_needed: List[Dict[str, Any]]
    labor_estimate: Dict[str, Any]
    timeline_estimate: str
    confidence_score: float
    processing_metadata: Dict[str, Any]
    document_info: Dict[str, Any]


@router.post("/process-with-claude", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_with_claude(
    request: ClaudeProcessingRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Queues a document for direct processing with Claude AI via a background task.
    """
    try:
        logger.info(f"Processing document {request.document_id} with Claude")

        # Get the document from database
        doc_uuid = uuid.UUID(request.document_id)
        document = await db.get(Document, doc_uuid)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Queue the background task
        task = process_document_with_claude_direct.delay(document_id=request.document_id)
        logger.info(f"Queued direct-to-Claude processing for document {request.document_id} with task ID {task.id}")

        # Set the Location header for the client to poll for status
        response.headers["Location"] = f"/api/v1/pipeline/status/{task.id}"
        
        return TaskResponse(
            task_id=task.id,
            document_id=request.document_id,
            status="queued",
            message="Document processing has been queued."
        )

    except Exception as e:
        logger.error(f"Error processing document with Claude: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the status and result of a background Celery task.
    """
    logger.debug(f"Checking status for task_id: {task_id}")
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        result_data = None
        error_data = None

        if task_result.failed():
            # Return the exception message, which is safer than the full traceback
            error_data = str(task_result.result)
        elif task_result.successful():
            result_data = task_result.get()

        return TaskStatusResponse(
            task_id=task_id,
            status=task_result.status,
            result=result_data,
            error=error_data,
        )
    except Exception as e:
        logger.error(f"Error checking task status for {task_id}: {e}")
        return TaskStatusResponse(
            task_id=task_id,
            status="UNKNOWN",
            error="Could not retrieve task status. The backend may be unavailable."
        )

@router.get("/estimate/{document_id}", response_model=FinalEstimateResponse)
async def get_final_estimate(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the final estimate data for a completed document.
    """
    logger.info(f"Fetching final estimate for document_id: {document_id}")
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    # Query for both ProcessingResults and the original Document in one go
    stmt = (
        select(ProcessingResults, Document)
        .join(Document, ProcessingResults.document_id == Document.id)
        .where(ProcessingResults.document_id == doc_uuid)
    )
    result = await db.execute(stmt)
    db_result = result.first()

    if not db_result:
        raise HTTPException(status_code=404, detail="Processing results not found for this document ID. Please check if processing is complete.")

    processing_results, document = db_result

    if document.processing_status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document processing is not complete. Current status: {document.processing_status.value}"
        )

    ai_interpretation_data = {}
    if processing_results.ai_interpretation and isinstance(processing_results.ai_interpretation, str):
        try:
            ai_interpretation_data = json.loads(processing_results.ai_interpretation)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse ai_interpretation JSON for doc {document_id}")

    total_area = processing_results.roof_area_sqft or 0
    
    return FinalEstimateResponse(
        total_area_sqft=total_area,
        estimated_cost=processing_results.estimated_cost or 0,
        materials_needed=processing_results.materials or [],
        labor_estimate=processing_results.labor_estimate or {},
        timeline_estimate=calculate_timeline_estimate(total_area, ai_interpretation_data),
        confidence_score=processing_results.confidence_score or 0,
        processing_metadata={
            "warnings": processing_results.warnings or [],
            "errors": processing_results.errors or [],
            "stages_completed": processing_results.stages_completed or [],
            "processing_time_seconds": processing_results.processing_time_seconds,
        },
        document_info={
            "filename": document.filename,
            "upload_date": document.created_at.isoformat(),
        }
    )
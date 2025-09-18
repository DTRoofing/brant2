import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.results import ProcessingResult
from app.models.processing import AIInterpretation

logger = logging.getLogger(__name__)

async def create_or_update_from_interpretation(db: AsyncSession, document_id: str, interpretation: AIInterpretation):
    """
    Asynchronously creates or updates a processing result from an AIInterpretation object.
    This is a simplified version for the direct-to-Claude flow.
    """
    logger.info(f"Saving interpretation results for document_id: {document_id}")
    
    result = await db.execute(select(ProcessingResult).filter(ProcessingResult.document_id == document_id))
    existing_result = result.scalars().first()

    if existing_result:
        # Update existing record
        existing_result.ai_interpretation = interpretation.model_dump()
        existing_result.confidence_score = interpretation.confidence
        logger.info(f"Updated processing result for document_id: {document_id}")
    else:
        # Create new record
        new_result = ProcessingResult(document_id=document_id, ai_interpretation=interpretation.model_dump(), confidence_score=interpretation.confidence)
        db.add(new_result)
        logger.info(f"Created new processing result for document_id: {document_id}")
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pathlib import Path

from app.models.core import Document

logger = logging.getLogger(__name__)

async def get(db: AsyncSession, id: str) -> Optional[Document]:
    """
    Asynchronously retrieves a document by its ID.
    """
    logger.debug(f"Fetching document with id: {id}")
    result = await db.execute(select(Document).filter(Document.id == id))
    document = result.scalars().first()
    if document and document.file_path:
        document.file_path = Path(document.file_path) # Ensure it's a Path object
    return document
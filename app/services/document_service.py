"""
Document Service for managing document operations.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.core import Document, User, ProcessingStatus
from app.schemas.document import DocumentRead, DocumentCreate


class DocumentService:
    """
    Service class for document operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_document(self, document_data: DocumentCreate, user_id: UUID) -> Document:
        """
        Create a new document record.
        """
        document = Document(
            filename=document_data.filename,
            file_path=document_data.gcs_path,
            document_type=document_data.document_type,
            processing_status=document_data.processing_status,
            user_id=user_id
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def get_document(self, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """
        Get a document by ID for a specific user.
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.id == document_id)
            .where(Document.user_id == user_id)
            .options(selectinload(Document.user))
        )
        return result.scalar_one_or_none()
    
    async def get_user_documents(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Document]:
        """
        Get all documents for a user with pagination.
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(Document.user))
        )
        return result.scalars().all()
    
    async def update_document_status(self, document_id: UUID, status: ProcessingStatus, error_message: Optional[str] = None) -> bool:
        """
        Update document processing status.
        """
        update_data = {"processing_status": status}
        if error_message:
            update_data["processing_error"] = error_message
            
        result = await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """
        Delete a document (soft delete by updating status).
        """
        result = await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .where(Document.user_id == user_id)
            .values(processing_status=ProcessingStatus.FAILED)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_documents_by_status(self, status: ProcessingStatus, limit: int = 100) -> List[Document]:
        """
        Get documents by processing status.
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.processing_status == status)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .options(selectinload(Document.user))
        )
        return result.scalars().all()


# Global service instance
document_service = DocumentService

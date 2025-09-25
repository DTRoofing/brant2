from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.core import ProcessingStatus

class DocumentCreate(BaseModel):
    filename: str
    gcs_path: str
    document_type: str = "standard"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING

class DocumentRead(BaseModel):
    id: UUID
    project_id: Optional[UUID] = None
    user_id: UUID
    filename: str
    file_path: str
    gcs_object_name: Optional[str] = None
    file_size: Optional[float] = None
    document_type: Optional[str] = None
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

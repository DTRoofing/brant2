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
    filename: str
    file_path: str
    file_size: Optional[float] = None
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

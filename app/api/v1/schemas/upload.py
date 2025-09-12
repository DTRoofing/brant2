from pydantic import BaseModel
import uuid
from datetime import datetime
from models.core import ProcessingStatus
from typing import Optional


class DocumentCreateResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_size: float
    processing_status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_size: float
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
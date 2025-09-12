from pydantic import BaseModel
import uuid
from datetime import datetime
from models.core import ProcessingStatus


class DocumentCreateResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_size: float
    processing_status: ProcessingStatus
    created_at: datetime

    class Config:
        from_attributes = True
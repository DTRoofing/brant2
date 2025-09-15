import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
from .base import Base


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    ANALYZING = "ANALYZING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(255), unique=True, index=True, nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    status = Column(SAEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False)
    status_message = Column(String(255))
    error_details = Column(Text)
    extracted_text = Column(Text, nullable=True)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
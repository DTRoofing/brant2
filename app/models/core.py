from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Enum, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_id = Column(String(255), unique=True, nullable=True, index=True)  # For Google OAuth
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        Index('ix_user_email', 'email'),
        Index('ix_user_username', 'username'),
        Index('ix_user_active', 'is_active'),
        Index('ix_user_google_id', 'google_id'),
    )
    
    # Relationships
    documents = relationship("Document", back_populates="user")


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    client_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="project")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    gcs_uri = Column(String(500), nullable=False)  # Always use GCS URI format gs://bucket/path
    file_size = Column(Float)
    document_type = Column(String(50), nullable=True)  # For document type classification
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        Index('ix_document_status', 'processing_status'),
        Index('ix_document_created', 'created_at'),
        Index('ix_document_project', 'project_id'),
        Index('ix_document_user', 'user_id'),
        Index('ix_document_filename', 'filename'),
    )
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    user = relationship("User", back_populates="documents")
    measurements = relationship("Measurement", back_populates="document")
    processing_results = relationship("ProcessingResults", back_populates="document", uselist=False)


class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    area_sf = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    source_coordinates = Column(JSON)  # Store bounding box, scale info
    measurement_type = Column(String(50))  # roof_area, wall_area, etc.
    extraction_method = Column(String(50))  # ocr, manual, calculated
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        Index('ix_measurement_document', 'document_id'),
        Index('ix_measurement_type', 'measurement_type'),
        Index('ix_measurement_confidence', 'confidence_score'),
    )
    
    # Relationships
    document = relationship("Document", back_populates="measurements")
"""
Processing Results Model
Stores the actual results from PDF processing pipeline
"""
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base


class ProcessingResults(Base):
    """
    Stores processing results from the PDF pipeline
    """
    __tablename__ = "processing_results"
    
    # Primary key - linked to document
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Core measurements
    roof_area_sqft = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Materials and features as JSON
    materials = Column(JSON, nullable=True)
    roof_features = Column(JSON, nullable=True)
    complexity_factors = Column(JSON, nullable=True)
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    stages_completed = Column(JSON, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # 'text', 'ocr', 'hybrid'
    
    # AI analysis results
    ai_interpretation = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Error tracking
    warnings = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship back to document
    document = relationship("Document", back_populates="processing_results")
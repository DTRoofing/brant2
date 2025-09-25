"""
Configuration models for the application.
"""
from sqlalchemy import Column, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class CostConfiguration(Base):
    """
    Model for storing cost configuration data.
    """
    __tablename__ = "cost_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Cost parameters
    base_cost_per_sqft = Column(Float, nullable=False, default=0.0)
    material_cost_multiplier = Column(Float, nullable=False, default=1.0)
    labor_cost_multiplier = Column(Float, nullable=False, default=1.0)
    overhead_multiplier = Column(Float, nullable=False, default=1.0)
    
    # Regional adjustments
    regional_multiplier = Column(Float, nullable=False, default=1.0)
    complexity_factor = Column(Float, nullable=False, default=1.0)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CostConfiguration(name='{self.name}', base_cost={self.base_cost_per_sqft})>"

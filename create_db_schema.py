#!/usr/bin/env python3
"""Create database schema for BRANT system"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    client_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    area_sf = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    source_coordinates = Column(JSON)
    measurement_type = Column(String(50))
    extraction_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    content_type = Column(String(100))
    status = Column(String(50), default="pending")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

class ProcessingResult(Base):
    __tablename__ = "processing_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    result_type = Column(String(50))
    result_data = Column(JSON)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all tables in the database"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    print(f"Connecting to database...")
    print(f"Database URL: {database_url.split('@')[1]}")  # Hide password
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Connection successful!")
            
            # Drop existing tables if requested (be careful!)
            # Uncomment the next line only if you want to reset the database
            # Base.metadata.drop_all(engine)
            
            # Create all tables
            print("\nCreating tables...")
            Base.metadata.create_all(engine)
            
            # Verify tables were created
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('projects', 'documents', 'measurements', 'uploads', 'processing_results')
                ORDER BY table_name
            """))
            
            created_tables = result.fetchall()
            print(f"\nCreated {len(created_tables)} tables:")
            for table in created_tables:
                print(f"  - {table[0]}")
            
            # Check total tables in public schema
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            total_tables = result.scalar()
            print(f"\nTotal tables in public schema: {total_tables}")
            
            print("\nDatabase schema created successfully!")
            return True
            
    except Exception as e:
        print(f"\nERROR: Failed to create tables")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    exit(0 if success else 1)
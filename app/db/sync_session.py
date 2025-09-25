"""
Synchronous database session for legacy code compatibility.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create synchronous engine
engine = create_engine(settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_sync_db():
    """
    Dependency to get synchronous database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
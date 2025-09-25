"""
Synchronous database session management for Celery workers and sync operations
"""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        try:
            # Create engine with appropriate SSL settings
            engine_kwargs = {
                "echo": settings.DEBUG,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
            
            # Add SSL configuration for PostgreSQL
            if settings.DB_SSL_MODE == "require":
                engine_kwargs["connect_args"] = {"sslmode": "require"}
            elif settings.DB_SSL_MODE == "disable":
                engine_kwargs["connect_args"] = {"sslmode": "disable"}
            
            _engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Session factory created successfully")
    return _SessionLocal


def get_sync_session() -> Generator[Session, None, None]:
    """
    Dependency to get a synchronous database session.
    Use this for Celery workers and other sync operations.
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def get_sync_session_direct() -> Session:
    """
    Get a synchronous database session directly.
    Use this when you need to manage the session lifecycle manually.
    """
    session_factory = get_session_factory()
    return session_factory()


# For backward compatibility
SessionLocal = get_sync_session_direct


def close_all_sessions():
    """Close all database connections and clean up resources."""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
        _engine = None
    _SessionLocal = None
    logger.info("All database sessions closed")


def test_connection() -> bool:
    """Test database connection."""
    try:
        session = get_sync_session_direct()
        session.execute("SELECT 1")
        session.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_session_info() -> dict:
    """Get information about the current database session configuration."""
    try:
        engine = get_engine()
        return {
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "hidden",
            "ssl_mode": settings.DB_SSL_MODE,
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        return {"error": str(e)}

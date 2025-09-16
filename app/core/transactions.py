"""
Database transaction management utilities
"""
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import TypeVar, Callable, Any
import logging
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


@asynccontextmanager
async def async_transaction(db: AsyncSession):
    """
    Async context manager for database transactions with automatic rollback on error
    
    Usage:
        async with async_transaction(db) as session:
            # Do database operations
            session.add(new_item)
            # Commits automatically on success, rolls back on exception
    """
    try:
        yield db
        await db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        logger.error(f"Transaction failed, rolling back: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


@contextmanager
def sync_transaction(db: Session):
    """
    Sync context manager for database transactions with automatic rollback on error
    
    Usage:
        with sync_transaction(db) as session:
            # Do database operations
            session.add(new_item)
            # Commits automatically on success, rolls back on exception
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        logger.error(f"Transaction failed, rolling back: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def transactional(func: Callable) -> Callable:
    """
    Decorator for wrapping async functions in a transaction
    
    Usage:
        @transactional
        async def create_user(db: AsyncSession, user_data: dict):
            user = User(**user_data)
            db.add(user)
            # Automatically commits or rolls back
    """
    @wraps(func)
    async def wrapper(*args, db: AsyncSession = None, **kwargs):
        if db is None:
            raise ValueError("Database session is required for transactional operations")
        
        try:
            result = await func(*args, db=db, **kwargs)
            await db.commit()
            logger.debug(f"Transaction in {func.__name__} committed successfully")
            return result
        except Exception as e:
            logger.error(f"Transaction in {func.__name__} failed, rolling back: {e}")
            await db.rollback()
            raise
    
    return wrapper


def sync_transactional(func: Callable) -> Callable:
    """
    Decorator for wrapping sync functions in a transaction
    
    Usage:
        @sync_transactional
        def create_user(db: Session, user_data: dict):
            user = User(**user_data)
            db.add(user)
            # Automatically commits or rolls back
    """
    @wraps(func)
    def wrapper(*args, db: Session = None, **kwargs):
        if db is None:
            raise ValueError("Database session is required for transactional operations")
        
        try:
            result = func(*args, db=db, **kwargs)
            db.commit()
            logger.debug(f"Transaction in {func.__name__} committed successfully")
            return result
        except Exception as e:
            logger.error(f"Transaction in {func.__name__} failed, rolling back: {e}")
            db.rollback()
            raise
    
    return wrapper


class TransactionManager:
    """
    Unit of Work pattern implementation for complex transactions
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
        
    async def __aenter__(self):
        self.session = self.session_factory()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()
        
    async def commit(self):
        if self.session:
            await self.session.commit()
            logger.debug("Transaction manager committed")
            
    async def rollback(self):
        if self.session:
            await self.session.rollback()
            logger.debug("Transaction manager rolled back")
            
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
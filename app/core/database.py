from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from .config import settings

# Create an async engine
# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
# asyncpg uses 'ssl' parameter instead of 'sslmode'
if "sslmode=require" in database_url:
    database_url = database_url.replace("sslmode=require", "ssl=require")
elif "sslmode=" not in database_url and "ssl=" not in database_url:
    # Add SSL if not present
    database_url += ("&" if "?" in database_url else "?") + "ssl=require"

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create a session maker that can be used to create sessions
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    """
    async with AsyncSessionFactory() as session:
        yield session
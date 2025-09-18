from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal

# NOTE: This file is being deprecated in favor of app/db/session.py and app/api/dependencies.py
# for better separation of concerns. The engine and session factory are now centralized in app/db/session.py.
# This get_db function is maintained for backward compatibility but should be replaced
# with the dependency from app.api.dependencies.

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
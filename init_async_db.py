import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
from app.core.config import settings

async def init_db():
    # Convert to async URL
    database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Async database tables created successfully!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
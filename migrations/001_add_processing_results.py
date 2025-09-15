"""
Database migration to add ProcessingResults table
Run this script to update your database schema
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.models.base import Base
from app.models.results import ProcessingResults
from app.models.core import Document  # Ensure relationship is loaded
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_processing_results_table():
    """
    Create the processing_results table in the database
    """
    # Convert to async URL
    database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if table exists
            result = await conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'processing_results'
                    )
                """)
            )
            table_exists = result.scalar()
            
            if table_exists:
                logger.info("Table 'processing_results' already exists")
                return
            
            # Create the table
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Successfully created 'processing_results' table")
            
            # Add index for better query performance
            await conn.execute(
                text("""
                    CREATE INDEX IF NOT EXISTS idx_processing_results_document_id 
                    ON processing_results(document_id)
                """)
            )
            logger.info("Created index on document_id")
            
    except Exception as e:
        logger.error(f"Failed to create table: {e}")
        raise
    finally:
        await engine.dispose()


async def verify_migration():
    """
    Verify the migration was successful
    """
    database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            # Check table structure
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'processing_results'
                    ORDER BY ordinal_position
                """)
            )
            
            columns = result.fetchall()
            logger.info("Table structure:")
            for col_name, col_type in columns:
                logger.info(f"  - {col_name}: {col_type}")
                
    finally:
        await engine.dispose()


def main():
    """
    Run the migration
    """
    logger.info("Starting database migration...")
    asyncio.run(create_processing_results_table())
    asyncio.run(verify_migration())
    logger.info("Migration completed successfully!")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Fix the processing_results table schema to match the application model
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://ADMIN:Brant01!@34.63.109.196:5432/postgres?ssl=require"


async def fix_schema():
    """
    Drop the old processing_results table and create the new one with proper columns
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Drop the old table
            logger.info("Dropping old processing_results table...")
            await conn.execute(text("DROP TABLE IF EXISTS processing_results CASCADE"))
            
            # Create the new table with proper schema
            logger.info("Creating new processing_results table with proper schema...")
            await conn.execute(text("""
                CREATE TABLE processing_results (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
                    
                    -- Core measurements
                    roof_area_sqft FLOAT,
                    estimated_cost FLOAT,
                    confidence_score FLOAT,
                    
                    -- Materials and features as JSON
                    materials JSONB,
                    roof_features JSONB,
                    complexity_factors JSONB,
                    
                    -- Processing metadata
                    processing_time_seconds FLOAT,
                    stages_completed JSONB,
                    extraction_method VARCHAR(50),
                    
                    -- AI analysis results
                    ai_interpretation TEXT,
                    recommendations JSONB,
                    
                    -- Error tracking
                    warnings JSONB,
                    errors JSONB,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Create index for better performance
            logger.info("Creating index on document_id...")
            await conn.execute(text("""
                CREATE INDEX idx_processing_results_document_id 
                ON processing_results(document_id)
            """))
            
            logger.info("Schema fixed successfully!")
            
    except Exception as e:
        logger.error(f"Failed to fix schema: {e}")
        raise
    finally:
        await engine.dispose()


async def verify_schema():
    """
    Verify the new schema
    """
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'processing_results'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            logger.info("\nNew table structure:")
            for col_name, col_type in columns:
                logger.info(f"  - {col_name}: {col_type}")
                
            # Check if the columns we need exist
            column_names = [col[0] for col in columns]
            required_columns = [
                'roof_area_sqft', 'estimated_cost', 'confidence_score',
                'materials', 'extraction_method', 'stages_completed'
            ]
            
            missing = [col for col in required_columns if col not in column_names]
            if missing:
                logger.error(f"Missing columns: {missing}")
                return False
            else:
                logger.info("[OK] All required columns present!")
                return True
                
    finally:
        await engine.dispose()


def main():
    """
    Run the schema fix
    """
    logger.info("=" * 60)
    logger.info("FIXING PROCESSING_RESULTS TABLE SCHEMA")
    logger.info("=" * 60)
    
    asyncio.run(fix_schema())
    success = asyncio.run(verify_schema())
    
    if success:
        logger.info("=" * 60)
        logger.info("[OK] Schema fix completed successfully!")
        logger.info("The processing_results table now matches the application model.")
        logger.info("=" * 60)
    else:
        logger.error("Schema fix may have issues - please check the errors above")


if __name__ == "__main__":
    main()
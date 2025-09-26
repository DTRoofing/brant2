"""
Configuration repository for cost estimation and processing parameters
"""

import logging
from typing import Dict, Any
from sqlalchemy import table, column, String, JSON, select

from app.db.session import get_db

logger = logging.getLogger(__name__)

# Default cost configuration
DEFAULT_COST_CONFIG = {
    "material_costs_per_sqft": {
        "asphalt_shingles": 8.0,
        "metal_roofing": 12.0,
        "slate_tiles": 20.0,
        "clay_tiles": 15.0,
        "wood_shakes": 18.0,
        "unknown": 8.0
    },
    "labor_costs_per_sqft": {
        "asphalt_shingles": 4.5,
        "metal_roofing": 6.0,
        "slate_tiles": 10.0,
        "clay_tiles": 8.0,
        "wood_shakes": 9.0,
        "unknown": 4.5
    },
    "overhead_percent": 15.0,
    "profit_margin_percent": 10.0,
    "contingency_percent": 5.0,
    "minimum_job_cost": 5000.0,
    "maximum_job_cost": 500000.0
}

async def get_cost_configuration() -> Dict[str, Any]:
    """
    Get the cost configuration for estimates from the database.
    Falls back to a hardcoded default if the database is unavailable or the config is missing.
    """
    try:
        # Get database session
        db_session = get_db()
        async for session in db_session:
            cost_configurations_table = table(
                'cost_configurations',
                column('key', String),
                column('config_data', JSON)
            )
            stmt = select(cost_configurations_table.c.config_data).where(cost_configurations_table.c.key == 'default')
            result = await session.execute(stmt)
            config_data = result.scalar_one_or_none()

            if config_data:
                logger.info("Loaded cost configuration from database.")
                return config_data
            else:
                logger.warning("No 'default' cost configuration found in database. Using hardcoded default.")
                return DEFAULT_COST_CONFIG.copy()
    except Exception as e:
        logger.error(f"Failed to load cost configuration from DB, falling back to default: {e}", exc_info=True)
        return DEFAULT_COST_CONFIG.copy()

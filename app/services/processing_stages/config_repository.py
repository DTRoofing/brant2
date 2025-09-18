"""
Configuration repository for cost estimation and processing parameters
"""

import logging
from typing import Dict, Any

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

def get_cost_configuration() -> Dict[str, Any]:
    """
    Get the cost configuration for estimates
    
    Returns:
        Dict containing cost parameters for material and labor calculations
    """
    try:
        # In a real implementation, this could load from a database or external config
        # For now, return the default configuration
        return DEFAULT_COST_CONFIG.copy()
    except Exception as e:
        logger.error(f"Failed to load cost configuration: {e}")
        return DEFAULT_COST_CONFIG.copy()

def update_cost_configuration(new_config: Dict[str, Any]) -> bool:
    """
    Update the cost configuration
    
    Args:
        new_config: New configuration values to merge
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # In a real implementation, this would save to database or external config
        # For now, just log the update
        logger.info(f"Cost configuration updated: {new_config}")
        return True
    except Exception as e:
        logger.error(f"Failed to update cost configuration: {e}")
        return False

def get_material_cost(material_type: str) -> float:
    """
    Get the cost per square foot for a specific material
    
    Args:
        material_type: Type of roofing material
        
    Returns:
        float: Cost per square foot
    """
    config = get_cost_configuration()
    material_costs = config.get("material_costs_per_sqft", {})
    return material_costs.get(material_type, material_costs.get("unknown", 8.0))

def get_labor_cost(material_type: str) -> float:
    """
    Get the labor cost per square foot for a specific material
    
    Args:
        material_type: Type of roofing material
        
    Returns:
        float: Labor cost per square foot
    """
    config = get_cost_configuration()
    labor_costs = config.get("labor_costs_per_sqft", {})
    return labor_costs.get(material_type, labor_costs.get("unknown", 4.5))

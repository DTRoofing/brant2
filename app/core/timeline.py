"""
Timeline calculation utilities for processing estimates.
"""
from typing import Dict, Any
from datetime import datetime, timedelta


def calculate_timeline_estimate(
    document_type: str,
    file_size: int,
    complexity_factors: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calculate processing timeline estimate based on document characteristics.
    
    Args:
        document_type: Type of document (e.g., 'roof_plan', 'blueprint')
        file_size: Size of the file in bytes
        complexity_factors: Additional complexity factors
        
    Returns:
        Dictionary with timeline estimates
    """
    if complexity_factors is None:
        complexity_factors = {}
    
    # Base processing times (in minutes)
    base_times = {
        'roof_plan': 15,
        'blueprint': 20,
        'photo': 10,
        'pdf': 25,
        'default': 15
    }
    
    # File size adjustments
    size_multiplier = 1.0
    if file_size > 10 * 1024 * 1024:  # > 10MB
        size_multiplier = 1.5
    elif file_size > 5 * 1024 * 1024:  # > 5MB
        size_multiplier = 1.2
    
    # Complexity adjustments
    complexity_multiplier = 1.0
    if complexity_factors.get('has_text', False):
        complexity_multiplier += 0.3
    if complexity_factors.get('has_images', False):
        complexity_multiplier += 0.2
    if complexity_factors.get('is_handwritten', False):
        complexity_multiplier += 0.4
    
    # Calculate estimated processing time
    base_time = base_times.get(document_type, base_times['default'])
    estimated_minutes = int(base_time * size_multiplier * complexity_multiplier)
    
    # Calculate estimated completion time
    start_time = datetime.utcnow()
    estimated_completion = start_time + timedelta(minutes=estimated_minutes)
    
    return {
        'estimated_processing_time_minutes': estimated_minutes,
        'estimated_completion_time': estimated_completion.isoformat(),
        'complexity_score': complexity_multiplier,
        'size_impact': size_multiplier,
        'document_type': document_type,
        'file_size_bytes': file_size
    }


def get_processing_stages() -> Dict[str, int]:
    """
    Get standard processing stages with their estimated durations.
    
    Returns:
        Dictionary mapping stage names to estimated minutes
    """
    return {
        'document_analysis': 5,
        'content_extraction': 10,
        'ai_interpretation': 15,
        'data_validation': 5,
        'result_generation': 10
    }
import logging
from typing import Dict, Any, List
import re

from app.models.processing import ValidatedData, AIInterpretation, ExtractedContent

logger = logging.getLogger(__name__)


class DataValidator:
    """Stage 4: Validate and enhance extracted data"""
    
    def __init__(self):
        # Roofing material costs (per sqft) - these would come from a database in production
        self.material_costs = {
            'asphalt_shingles': 3.50,
            'metal_roofing': 8.00,
            'tile': 12.00,
            'slate': 15.00,
            'wood_shakes': 10.00,
            'membrane': 6.00
        }
        
        # Labor costs (per sqft)
        self.labor_costs = {
            'asphalt_shingles': 2.50,
            'metal_roofing': 4.00,
            'tile': 5.00,
            'slate': 8.00,
            'wood_shakes': 6.00,
            'membrane': 3.00
        }
    
    async def validate_data(self, interpretation: AIInterpretation, content: ExtractedContent) -> ValidatedData:
        """
        Validate and enhance the AI interpretation
        
        Args:
            interpretation: AI interpretation results
            content: Original extracted content
            
        Returns:
            ValidatedData with validated measurements and cost estimates
        """
        logger.info("Validating and enhancing data")
        
        try:
            # Validate measurements
            validated_measurements = self._validate_measurements(interpretation.measurements)
            
            # Calculate cost estimates
            cost_estimates = self._calculate_cost_estimates(interpretation, validated_measurements)
            
            # Generate material recommendations
            material_recommendations = self._generate_material_recommendations(interpretation)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(interpretation, content)
            
            # Generate warnings and errors
            warnings, errors = self._generate_warnings_and_errors(interpretation, validated_measurements)
            
            return ValidatedData(
                validated_measurements=validated_measurements,
                cost_estimates=cost_estimates,
                material_recommendations=material_recommendations,
                quality_score=quality_score,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return ValidatedData(
                validated_measurements=[],
                cost_estimates={},
                material_recommendations=[],
                quality_score=0.0,
                warnings=[],
                errors=[f"Validation failed: {str(e)}"]
            )
    
    def _validate_measurements(self, measurements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean up measurements"""
        validated = []
        
        for measurement in measurements:
            try:
                value = measurement.get('value', 0)
                label = measurement.get('label', 'unknown')
                unit = measurement.get('unit', 'sqft')
                
                # Basic validation
                if not isinstance(value, (int, float)) or value <= 0:
                    continue
                
                # Reasonable range check for roof areas
                if 'area' in label.lower() and unit == 'sqft':
                    if value < 100:  # Too small for a roof
                        continue
                    if value > 100000:  # Unreasonably large
                        continue
                
                # Convert to standard units if needed
                if unit in ['sqm', 'square_meters']:
                    value = value * 10.764  # Convert to sqft
                    unit = 'sqft'
                
                validated.append({
                    'label': label,
                    'value': round(value, 2),
                    'unit': unit,
                    'confidence': measurement.get('confidence', 0.8),
                    'validated': True
                })
                
            except Exception as e:
                logger.warning(f"Could not validate measurement: {e}")
                continue
        
        return validated
    
    def _calculate_cost_estimates(self, interpretation: AIInterpretation, measurements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate cost estimates based on materials and measurements"""
        costs = {}
        
        # Find total roof area
        total_area = interpretation.roof_area_sqft
        if not total_area:
            # Try to calculate from measurements
            area_measurements = [m for m in measurements if 'area' in m.get('label', '').lower()]
            if area_measurements:
                total_area = sum(m['value'] for m in area_measurements)
        
        if not total_area:
            return {"error": "No roof area found for cost calculation"}
        
        # Determine primary material
        primary_material = self._determine_primary_material(interpretation.materials)
        
        if primary_material in self.material_costs:
            material_cost_per_sqft = self.material_costs[primary_material]
            labor_cost_per_sqft = self.labor_costs[primary_material]
            
            costs = {
                'total_area_sqft': total_area,
                'material_cost_per_sqft': material_cost_per_sqft,
                'labor_cost_per_sqft': labor_cost_per_sqft,
                'total_material_cost': total_area * material_cost_per_sqft,
                'total_labor_cost': total_area * labor_cost_per_sqft,
                'total_cost': total_area * (material_cost_per_sqft + labor_cost_per_sqft),
                'primary_material': primary_material
            }
        else:
            # Use average costs if material not identified
            avg_material_cost = sum(self.material_costs.values()) / len(self.material_costs)
            avg_labor_cost = sum(self.labor_costs.values()) / len(self.labor_costs)
            
            costs = {
                'total_area_sqft': total_area,
                'material_cost_per_sqft': avg_material_cost,
                'labor_cost_per_sqft': avg_labor_cost,
                'total_material_cost': total_area * avg_material_cost,
                'total_labor_cost': total_area * avg_labor_cost,
                'total_cost': total_area * (avg_material_cost + avg_labor_cost),
                'primary_material': 'unknown'
            }
        
        return costs
    
    def _determine_primary_material(self, materials: List[Dict[str, Any]]) -> str:
        """Determine the primary roofing material"""
        if not materials:
            return 'asphalt_shingles'  # Default
        
        # Look for materials with highest confidence or most common
        material_counts = {}
        for material in materials:
            material_type = material.get('type', 'unknown')
            material_counts[material_type] = material_counts.get(material_type, 0) + 1
        
        if material_counts:
            return max(material_counts, key=material_counts.get)
        
        return 'asphalt_shingles'
    
    def _generate_material_recommendations(self, interpretation: AIInterpretation) -> List[Dict[str, Any]]:
        """Generate material recommendations based on interpretation"""
        recommendations = []
        
        # Basic recommendations based on roof area and pitch
        if interpretation.roof_area_sqft:
            if interpretation.roof_area_sqft < 2000:
                recommendations.append({
                    'material': 'asphalt_shingles',
                    'reason': 'Small roof area - cost effective option',
                    'estimated_cost_per_sqft': self.material_costs['asphalt_shingles']
                })
            elif interpretation.roof_area_sqft > 5000:
                recommendations.append({
                    'material': 'metal_roofing',
                    'reason': 'Large roof area - durable long-term option',
                    'estimated_cost_per_sqft': self.material_costs['metal_roofing']
                })
        
        # Recommendations based on damage assessment
        if interpretation.damage_assessment:
            severity = interpretation.damage_assessment.get('severity', 'low')
            if severity == 'high':
                recommendations.append({
                    'material': 'metal_roofing',
                    'reason': 'High damage severity - need durable material',
                    'estimated_cost_per_sqft': self.material_costs['metal_roofing']
                })
        
        return recommendations
    
    def _calculate_quality_score(self, interpretation: AIInterpretation, content: ExtractedContent) -> float:
        """Calculate a quality score for the interpretation"""
        score = 0.0
        max_score = 10.0
        
        # Base score from confidence
        score += interpretation.confidence * 3.0
        
        # Score for having roof area
        if interpretation.roof_area_sqft:
            score += 2.0
        
        # Score for having materials identified
        if interpretation.materials:
            score += 1.0
        
        # Score for having measurements
        if interpretation.measurements:
            score += 1.0
        
        # Score for extraction method quality
        if content.extraction_method == 'google_document_ai':
            score += 2.0
        elif content.extraction_method == 'google_vision_api':
            score += 1.5
        else:
            score += 0.5
        
        # Score for interpretation method
        if interpretation.interpretation_method == 'claude_ai':
            score += 1.0
        else:
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    def _generate_warnings_and_errors(self, interpretation: AIInterpretation, measurements: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
        """Generate warnings and errors based on the data"""
        warnings = []
        errors = []
        
        # Check for missing critical data
        if not interpretation.roof_area_sqft and not measurements:
            errors.append("No roof area measurements found")
        
        if not interpretation.materials:
            warnings.append("No roofing materials identified")
        
        # Check for unreasonable values
        if interpretation.roof_area_sqft:
            if interpretation.roof_area_sqft < 100:
                warnings.append("Roof area seems unusually small")
            elif interpretation.roof_area_sqft > 50000:
                warnings.append("Roof area seems unusually large")
        
        # Check confidence levels
        if interpretation.confidence < 0.5:
            warnings.append("Low confidence in AI interpretation")
        
        # Check for damage that needs attention
        if interpretation.damage_assessment:
            severity = interpretation.damage_assessment.get('severity', 'low')
            if severity == 'high':
                warnings.append("High damage severity detected - immediate attention recommended")
        
        return warnings, errors

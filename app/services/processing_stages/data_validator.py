import logging
from typing import Dict, Any, List

from app.models.processing import ValidatedData, AIInterpretation, ExtractedContent
from app.services.processing_stages.config_repository import get_cost_configuration

logger = logging.getLogger(__name__)


class DataValidator:
    """Stage 4: Validate and enhance extracted data"""
    
    def validate_data(self, interpretation: AIInterpretation, content: ExtractedContent) -> ValidatedData:
        """Validate and enhance the AI interpretation data"""
        try:
            # Get cost configuration
            cost_config = get_cost_configuration()
            
            # Validate measurements
            validated_measurements = self._validate_measurements(interpretation.measurements)
            
            # Calculate cost estimates
            cost_estimates = self._calculate_cost_estimates(cost_config, interpretation, validated_measurements)
            
            # Generate material recommendations
            material_recommendations = self._generate_material_recommendations(cost_config, interpretation)
            
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
    
    def _calculate_cost_estimates(self, cost_config: Dict, interpretation: AIInterpretation, measurements: List[Dict[str, Any]]) -> Dict[str, float]:
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
        
        material_costs = cost_config.get('material_costs_per_sqft', {})
        labor_costs = cost_config.get('labor_costs_per_sqft', {})

        material_cost_per_sqft = material_costs.get(primary_material, material_costs.get('unknown', 8.0))
        labor_cost_per_sqft = labor_costs.get(primary_material, labor_costs.get('unknown', 4.5))
        
        base_material_cost = total_area * material_cost_per_sqft
        base_labor_cost = total_area * labor_cost_per_sqft
        base_cost = base_material_cost + base_labor_cost

        # Apply business logic (overhead, profit, contingency)
        overhead_percent = cost_config.get('overhead_percent', 15.0)
        profit_margin_percent = cost_config.get('profit_margin_percent', 10.0)
        contingency_percent = cost_config.get('contingency_percent', 5.0)

        overhead_cost = base_cost * (overhead_percent / 100)
        subtotal = base_cost + overhead_cost
        profit_cost = subtotal * (profit_margin_percent / 100)
        contingency_cost = subtotal * (contingency_percent / 100)
        
        final_estimated_cost = subtotal + profit_cost + contingency_cost
            
        return {
            'total_area_sqft': total_area,
            'primary_material': primary_material,
            'material_cost_per_sqft': material_cost_per_sqft,
            'labor_cost_per_sqft': labor_cost_per_sqft,
            'base_material_cost': base_material_cost,
            'base_labor_cost': base_labor_cost,
            'overhead_cost': overhead_cost,
            'profit_cost': profit_cost,
            'contingency_cost': contingency_cost,
            'final_estimated_cost': final_estimated_cost
        }
    
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
    
    def _generate_material_recommendations(self, cost_config: Dict, interpretation: AIInterpretation) -> List[Dict[str, Any]]:
        """Generate material recommendations based on interpretation"""
        recommendations = []
        
        # Basic recommendations based on roof area and pitch
        if interpretation.roof_area_sqft:
            if interpretation.roof_area_sqft < 2000:
                recommendations.append({
                    'type': 'asphalt_shingles',
                    'reason': 'Small roof area - cost effective option',
                    'estimated_cost_per_sqft': cost_config.get('material_costs_per_sqft', {}).get('asphalt_shingles', 8.0)
                })
            elif interpretation.roof_area_sqft < 5000:
                recommendations.append({
                    'type': 'metal_roofing',
                    'reason': 'Medium roof area - good balance of cost and durability',
                    'estimated_cost_per_sqft': cost_config.get('material_costs_per_sqft', {}).get('metal_roofing', 12.0)
                })
            else:
                recommendations.append({
                    'type': 'slate_tiles',
                    'reason': 'Large roof area - premium option for long-term value',
                    'estimated_cost_per_sqft': cost_config.get('material_costs_per_sqft', {}).get('slate_tiles', 20.0)
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
            score += 1.5
        else:
            score += 0.5
        
        # Score for interpretation method
        if interpretation.interpretation_method == 'claude_ai':
            score += 1.0
        else:
            score += 0.5
        
        return min(score, max_score)
    
    def _generate_warnings_and_errors(self, interpretation: AIInterpretation, measurements: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
        """Generate warnings and errors based on the data"""
        warnings = []
        errors = []
        
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
import logging
from typing import Dict, Any, List, Optional
import json
import os

from app.models.processing import AIInterpretation, ExtractedContent, DocumentType
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)


class AIInterpreter:
    """Stage 3: Use AI to interpret extracted content for roofing estimates"""
    
    def __init__(self):
        self.claude_service = claude_service
        self.roofing_prompt = self._load_roofing_prompt()
    
    def _load_roofing_prompt(self) -> str:
        """Load the roofing estimation prompt from file"""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'roofing_estimation_prompt.txt')
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Roofing prompt file not found at {prompt_path}, using default prompt")
            return ""
    
    async def interpret_content(self, content: ExtractedContent, document_type: DocumentType) -> AIInterpretation:
        """
        Use AI to interpret extracted content for roofing estimates with roof features
        
        Args:
            content: Extracted content from previous stage
            document_type: Type of document being processed
            
        Returns:
            AIInterpretation with structured roofing data including roof features
        """
        logger.info(f"Interpreting {document_type} content with AI and roof features")

        # Extract project metadata from content (from index page analysis)
        project_metadata = {}
        if hasattr(content, 'project_metadata') and content.project_metadata:
            project_metadata = content.project_metadata
            logger.info(f"Using project metadata from index page: {project_metadata}")

        # Check if this is a McDonald's document
        is_mcdonalds = False
        mcdonalds_data = {}
        if hasattr(content, 'metadata') and content.metadata:
            if content.metadata.get('document_type') == 'mcdonalds_roofing':
                is_mcdonalds = True
                mcdonalds_data = content.metadata
        elif project_metadata.get('client') == "McDonald's" or 'mcdonald' in str(project_metadata).lower():
            is_mcdonalds = True
            mcdonalds_data = project_metadata

        if is_mcdonalds:
            logger.info(f"McDonald's document detected with comprehensive data: {mcdonalds_data}")
        
        try:
            if not self.claude_service.client:
                return self._interpret_with_rules(content, document_type, mcdonalds_data)
            
            # Create specialized prompt including roof features
            if is_mcdonalds:
                prompt = self._create_mcdonalds_interpretation_prompt(content, mcdonalds_data)
            else:
                prompt = self._create_interpretation_prompt_with_features(content, document_type)
            
            # Get AI interpretation
            response = self.claude_service.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            import re
            response_text = response.content[0].text
            
            # Try to extract JSON from the response
            try:
                # Look for JSON pattern in the response
                # This regex handles nested JSON objects
                json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', response_text, re.DOTALL)
                if json_match:
                    interpretation_data = json.loads(json_match.group())
                else:
                    # Try to parse the entire response as JSON
                    interpretation_data = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Claude response as JSON: {response_text}")
                # Use default values
                interpretation_data = {
                    "roof_area_sqft": 0,
                    "confidence": 0.5,
                    "materials": [],
                    "measurements": []
                }
            
            # Process roof features
            roof_features = self._process_roof_features(content.roof_features if hasattr(content, 'roof_features') else [])
            
            # Merge all metadata from index page and AI interpretation
            metadata = {
                # Project Information
                'project_name': interpretation_data.get('project_name', project_metadata.get('project_name', f"McDonald's #{mcdonalds_data.get('store_number', '')}" if is_mcdonalds else '')),
                'project_number': interpretation_data.get('project_number', project_metadata.get('project_number', mcdonalds_data.get('project_number', ''))),
                'site_id': project_metadata.get('site_id', ''),

                # Building Information
                'address': project_metadata.get('address', mcdonalds_data.get('location', '')),
                'building_height': project_metadata.get('building_height', ''),
                'structural_makeup': project_metadata.get('structural_makeup', ''),
                'gross_building_area': project_metadata.get('square_footage', interpretation_data.get('roof_area_sqft', 0)),

                # Contact Information
                'project_manager': project_metadata.get('project_manager', ''),
                'pm_email': project_metadata.get('pm_email', ''),
                'pm_phone': project_metadata.get('pm_phone', ''),

                # Design Team
                'designer_of_record': project_metadata.get('designer_of_record', ''),
                'engineer': project_metadata.get('engineer', ''),

                # Dates
                'issue_date': project_metadata.get('issue_date', ''),
                'review_date': project_metadata.get('review_date', ''),
                'reviewed_by': project_metadata.get('reviewed_by', ''),

                # Materials
                'roof_materials': project_metadata.get('roof_materials', interpretation_data.get('materials', [])),

                # McDonald's specific if applicable
                'client': project_metadata.get('client', 'McDonald\'s' if is_mcdonalds else ''),
                'store_number': project_metadata.get('store_number', mcdonalds_data.get('store_number', '')),
                'document_type': 'mcdonalds_roofing' if is_mcdonalds else 'standard_roofing'
            }

            # Clean up empty values
            metadata = {k: v for k, v in metadata.items() if v}
            
            return AIInterpretation(
                roof_area_sqft=interpretation_data.get('roof_area_sqft'),
                roof_pitch=interpretation_data.get('roof_pitch'),
                materials=interpretation_data.get('materials', []),
                measurements=interpretation_data.get('measurements', []),
                damage_assessment=interpretation_data.get('damage_assessment'),
                special_requirements=interpretation_data.get('special_requirements', []),
                roof_features=roof_features,
                confidence=interpretation_data.get('confidence', 0.8),
                interpretation_method='claude_ai_with_features',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"AI interpretation failed: {e}")
            return self._interpret_with_rules(content, document_type)
    
    def _create_interpretation_prompt(self, content: ExtractedContent, document_type: DocumentType) -> str:
        """Create specialized prompt based on document type"""
        
        base_prompt = f"""
        You are an expert roofing contractor analyzing a {document_type} document to create a roofing estimate.
        
        Extracted content:
        Text: {content.text[:3000]}...
        
        Tables: {json.dumps(content.tables[:2], indent=2)}
        Measurements: {json.dumps(content.measurements, indent=2)}
        """
        
        if document_type == DocumentType.BLUEPRINT:
            return base_prompt + """
            
            For this BLUEPRINT, extract:
            1. Total roof area in square feet
            2. Roof pitch/slope
            3. Roof sections and their areas
            4. Materials mentioned
            5. Special architectural features
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "roof_pitch": "string",
                "materials": [{"type": "string", "quantity": number}],
                "measurements": [{"label": "string", "value": number, "unit": "string"}],
                "special_requirements": ["string"],
                "confidence": 0.0-1.0
            }
            """
        
        elif document_type == DocumentType.INSPECTION_REPORT:
            return base_prompt + """
            
            For this INSPECTION REPORT, extract:
            1. Current roof area
            2. Damage assessment and severity
            3. Materials that need replacement
            4. Repair vs replacement recommendations
            5. Urgency level
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "damage_assessment": {
                    "severity": "low|medium|high",
                    "damage_types": ["string"],
                    "affected_area_percent": number
                },
                "materials": [{"type": "string", "condition": "string"}],
                "special_requirements": ["string"],
                "confidence": 0.0-1.0
            }
            """
        
        elif document_type == DocumentType.PHOTO:
            return base_prompt + """
            
            For this PHOTO, analyze:
            1. Visible roof area (estimate)
            2. Roof material type
            3. Visible damage or wear
            4. Roof pitch estimation
            5. Special features visible
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "roof_pitch": "string",
                "materials": [{"type": "string", "condition": "string"}],
                "damage_assessment": {
                    "visible_damage": ["string"],
                    "severity": "low|medium|high"
                },
                "special_requirements": ["string"],
                "confidence": 0.0-1.0
            }
            """
        
        else:  # ESTIMATE or UNKNOWN
            return base_prompt + """
            
            For this document, extract any roofing-related information:
            1. Roof area mentioned
            2. Materials listed
            3. Costs or pricing
            4. Measurements
            5. Special requirements
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "materials": [{"type": "string", "quantity": number}],
                "measurements": [{"label": "string", "value": number}],
                "special_requirements": ["string"],
                "confidence": 0.0-1.0
            }
            """
    
    def _create_mcdonalds_interpretation_prompt(self, content: ExtractedContent, mcdonalds_data: Dict[str, Any]) -> str:
        """Create specialized prompt for McDonald's documents"""
        
        prompt = f"""
        You are analyzing a McDonald's restaurant roofing document.
        
        McDonald's Information Detected:
        - Project Number: {mcdonalds_data.get('project_number', 'Not found')}
        - Store Number: {mcdonalds_data.get('store_number', 'Not found')}
        - Location: {mcdonalds_data.get('location', 'Not found')}
        - Address: {mcdonalds_data.get('address', 'Not found')}
        
        Extracted content:
        Text: {content.text[:4000]}...
        
        Measurements found: {json.dumps(content.measurements, indent=2)}
        
        For this McDonald's roofing document, extract:
        1. Total roof area in square feet (McDonald's restaurants typically 3,000-5,000 sq ft)
        2. Roof sections (dining area, kitchen, storage)
        3. Roofing materials (typically commercial membrane - TPO, EPDM, or modified bitumen)
        4. Special requirements for McDonald's facilities
        5. Any equipment on roof (HVAC, exhaust fans, grease vents)
        
        Respond with JSON:
        {{
            "project_name": "McDonald's #{mcdonalds_data.get('store_number', 'Unknown')} - {mcdonalds_data.get('location', 'Unknown')}",
            "project_number": "{mcdonalds_data.get('project_number', '')}",
            "store_number": "{mcdonalds_data.get('store_number', '')}",
            "location": "{mcdonalds_data.get('location', '')}",
            "roof_area_sqft": number,
            "roof_pitch": "string",
            "materials": [{{"type": "string", "quantity": number}}],
            "measurements": [{{"label": "string", "value": number, "unit": "string"}}],
            "special_requirements": ["McDonald's corporate standards", "Grease vent protection", "etc"],
            "confidence": 0.0-1.0
        }}
        """
        
        return prompt
    
    def _interpret_with_rules(self, content: ExtractedContent, document_type: DocumentType, mcdonalds_data: Dict[str, Any] = None) -> AIInterpretation:
        """Fallback rule-based interpretation"""
        logger.info("Using rule-based interpretation")
        
        # Extract basic measurements from text
        measurements = self._extract_measurements_from_text(content.text)
        
        # Try to find roof area
        roof_area = self._find_roof_area(measurements)
        
        # Extract materials mentioned
        materials = self._extract_materials_from_text(content.text)
        
        return AIInterpretation(
            roof_area_sqft=roof_area,
            roof_pitch=None,
            materials=materials,
            measurements=measurements,
            damage_assessment=None,
            special_requirements=[],
            confidence=0.5,
            interpretation_method='rule_based'
        )
    
    def _extract_measurements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract measurements using regex patterns"""
        import re
        
        measurements = []
        
        # Area patterns
        area_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|square\s+feet|sf|sqft)',
            r'area[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'roof[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
        ]
        
        for pattern in area_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1).replace(',', ''))
                    measurements.append({
                        'label': 'roof_area',
                        'value': value,
                        'unit': 'sqft'
                    })
                except ValueError:
                    continue
        
        return measurements
    
    def _find_roof_area(self, measurements: List[Dict[str, Any]]) -> Optional[float]:
        """Find the most likely roof area from measurements"""
        for measurement in measurements:
            if measurement.get('label') == 'roof_area':
                return measurement.get('value')
        
        # Look for largest area measurement
        area_values = [m.get('value', 0) for m in measurements if m.get('unit') == 'sqft']
        if area_values:
            return max(area_values)
        
        return None
    
    def _extract_materials_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract roofing materials mentioned in text"""
        import re
        
        materials = []
        text_lower = text.lower()
        
        # Common roofing materials
        material_patterns = {
            'asphalt_shingles': r'asphalt|shingle',
            'metal_roofing': r'metal|steel|aluminum',
            'tile': r'tile|clay|concrete',
            'slate': r'slate',
            'wood_shakes': r'wood|shake|cedar',
            'membrane': r'membrane|epdm|tpo'
        }
        
        for material_type, pattern in material_patterns.items():
            if re.search(pattern, text_lower):
                materials.append({
                    'type': material_type,
                    'condition': 'unknown'
                })
        
        return materials
    
    def _create_interpretation_prompt_with_features(self, content: ExtractedContent, document_type: DocumentType) -> str:
        """Create specialized prompt including roof features"""
        
        # Use the comprehensive roofing prompt if available
        if self.roofing_prompt:
            base_prompt = f"""
        {self.roofing_prompt}
        
        Document Type: {document_type}
        
        Extracted content:
        Text: {content.text[:3000]}...
        
        Tables: {json.dumps(content.tables[:2], indent=2)}
        Measurements: {json.dumps(content.measurements, indent=2)}
        """
        else:
            base_prompt = f"""
        You are an expert roofing contractor analyzing a {document_type} document to create a roofing estimate.
        
        Extracted content:
        Text: {content.text[:3000]}...
        
        Tables: {json.dumps(content.tables[:2], indent=2)}
        Measurements: {json.dumps(content.measurements, indent=2)}
        """
        
        # Add roof features information
        roof_features = content.roof_features if hasattr(content, 'roof_features') else []
        if roof_features:
            base_prompt += f"""
        
        Roof Features Detected:
        {json.dumps(roof_features, indent=2)}
        """
        
        # Add verification results
        verification_result = content.verification_result if hasattr(content, 'verification_result') else {}
        if verification_result:
            base_prompt += f"""
        
        Measurement Verification:
        OCR Total: {verification_result.get('ocr_total', 0)} sqft
        Blueprint Total: {verification_result.get('blueprint_total', 0)} sqft
        Difference: {verification_result.get('difference_percent', 0):.1f}%
        Recommendation: {verification_result.get('recommendation', 'manual_review')}
        """
        
        if document_type == DocumentType.BLUEPRINT:
            return base_prompt + """
            
            For this BLUEPRINT, extract:
            1. Total roof area in square feet (use verified measurements)
            2. Roof pitch/slope
            3. Roof sections and their areas
            4. Materials mentioned
            5. Special architectural features
            6. Roof features (exhaust ports, walkways, equipment, etc.)
            7. Impact of features on installation complexity
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "roof_pitch": "string",
                "materials": [{"type": "string", "quantity": number}],
                "measurements": [{"label": "string", "value": number, "unit": "string"}],
                "roof_features": [{"type": "string", "count": number, "impact": "string"}],
                "special_requirements": ["string"],
                "complexity_factors": ["string"],
                "confidence": 0.0-1.0
            }
            """
        else:
            return base_prompt + """
            
            For this document, extract any roofing-related information including roof features:
            1. Roof area mentioned
            2. Materials listed
            3. Costs or pricing
            4. Measurements
            5. Roof features and their impact
            6. Special requirements
            
            Respond with JSON:
            {
                "roof_area_sqft": number,
                "materials": [{"type": "string", "quantity": number}],
                "measurements": [{"label": "string", "value": number}],
                "roof_features": [{"type": "string", "count": number, "impact": "string"}],
                "special_requirements": ["string"],
                "confidence": 0.0-1.0
            }
            """
    
    def _process_roof_features(self, roof_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and categorize roof features"""
        processed_features = []
        
        # Group features by type
        feature_counts = {}
        for feature in roof_features:
            feature_type = feature.get('type', 'unknown')
            if feature_type not in feature_counts:
                feature_counts[feature_type] = 0
            feature_counts[feature_type] += 1
        
        # Create processed features with impact assessment
        for feature_type, count in feature_counts.items():
            impact = self._assess_feature_impact(feature_type, count)
            processed_features.append({
                'type': feature_type,
                'count': count,
                'impact': impact,
                'description': self._get_feature_description(feature_type)
            })
        
        return processed_features
    
    def _assess_feature_impact(self, feature_type: str, count: int) -> str:
        """Assess the impact of roof features on installation complexity"""
        impact_map = {
            'exhaust_port': 'medium' if count <= 3 else 'high',
            'walkway': 'low',
            'equipment': 'high',
            'drain': 'low',
            'penetration': 'medium',
            'equipment_pad': 'medium'
        }
        
        return impact_map.get(feature_type, 'medium')
    
    def _get_feature_description(self, feature_type: str) -> str:
        """Get description for roof feature type"""
        descriptions = {
            'exhaust_port': 'Exhaust ports require careful sealing and flashing',
            'walkway': 'Walkways provide access but may require additional materials',
            'equipment': 'HVAC equipment requires structural considerations',
            'drain': 'Roof drains need proper installation and waterproofing',
            'penetration': 'Penetrations require specialized flashing',
            'equipment_pad': 'Equipment pads may need reinforcement'
        }
        
        return descriptions.get(feature_type, 'Additional roof feature requiring attention')

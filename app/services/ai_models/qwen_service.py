"""
Qwen model service for advanced text extraction and understanding from technical documents.
"""

import logging
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass
from datetime import datetime
import httpx
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

@dataclass
class QwenExtractionResult:
    """Result from Qwen text extraction"""
    text_content: str
    technical_terms: List[Dict[str, Any]]
    measurements: List[Dict[str, Any]]
    specifications: List[Dict[str, Any]]
    annotations: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]


class QwenService:
    """Service for interacting with Qwen model for technical document analysis"""
    
    def __init__(self, api_key: Optional[str] = None, api_endpoint: Optional[str] = None):
        """
        Initialize Qwen service.
        
        Args:
            api_key: API key for Qwen service
            api_endpoint: Custom API endpoint (optional)
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint or "https://api.qwen.ai/v1"
        self.client = httpx.AsyncClient(timeout=120.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    async def extract_text_from_document(
        self,
        document_content: bytes,
        document_type: str = "blueprint",
        extract_measurements: bool = True,
        extract_specifications: bool = True,
        extract_annotations: bool = True
    ) -> QwenExtractionResult:
        """
        Extract text and structured data from technical documents using Qwen.
        
        Args:
            document_content: PDF content as bytes
            document_type: Type of document (blueprint, schematic, etc.)
            extract_measurements: Whether to extract measurements
            extract_specifications: Whether to extract specifications
            extract_annotations: Whether to extract annotations
            
        Returns:
            QwenExtractionResult with extracted data
        """
        start_time = datetime.now()
        
        try:
            # Prepare the request for Qwen API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create the prompt for technical document analysis
            system_prompt = self._create_technical_analysis_prompt(
                document_type,
                extract_measurements,
                extract_specifications,
                extract_annotations
            )
            
            # For now, we'll simulate the API call
            # In production, this would be replaced with actual Qwen API integration
            logger.info(f"Processing {document_type} document with Qwen model")
            
            # Simulate processing delay
            await asyncio.sleep(2.0)
            
            # Mock extracted data structure
            result = QwenExtractionResult(
                text_content=self._extract_text_content(document_content),
                technical_terms=self._extract_technical_terms(),
                measurements=self._extract_measurements() if extract_measurements else [],
                specifications=self._extract_specifications() if extract_specifications else [],
                annotations=self._extract_annotations() if extract_annotations else [],
                confidence_score=0.95,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    "model_version": "qwen-technical-v1",
                    "document_type": document_type,
                    "extraction_timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Qwen extraction completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error during Qwen extraction: {str(e)}")
            raise
    
    def _create_technical_analysis_prompt(
        self,
        document_type: str,
        extract_measurements: bool,
        extract_specifications: bool,
        extract_annotations: bool
    ) -> str:
        """Create specialized prompt for technical document analysis"""
        
        base_prompt = f"""
        Analyze this {document_type} document and extract structured information.
        Focus on technical details relevant to roofing construction.
        """
        
        tasks = []
        if extract_measurements:
            tasks.append("""
            - Extract all measurements including:
              * Roof dimensions (length, width, height)
              * Slope angles and pitch ratios
              * Area calculations
              * Component sizes
            """)
            
        if extract_specifications:
            tasks.append("""
            - Extract material specifications:
              * Material types and grades
              * Thickness and weight specifications
              * Installation requirements
              * Compliance standards
            """)
            
        if extract_annotations:
            tasks.append("""
            - Extract annotations and notes:
              * Construction notes
              * Special instructions
              * Reference markers
              * Revision information
            """)
        
        return base_prompt + "\n".join(tasks)
    
    def _extract_text_content(self, document_content: bytes) -> str:
        """Extract raw text content (mock implementation)"""
        # In production, this would use actual OCR/text extraction
        return """
        ROOF FRAMING PLAN
        Scale: 1/4" = 1'-0"
        
        Main Roof Area: 2,456 sq ft
        Pitch: 6:12
        Ridge Height: 24'-6"
        
        Materials:
        - Architectural shingles, 30-year warranty
        - Ice & water shield at eaves and valleys
        - Synthetic underlayment
        - Aluminum drip edge
        """
    
    def _extract_technical_terms(self) -> List[Dict[str, Any]]:
        """Extract technical terms and their contexts"""
        return [
            {
                "term": "Hip Roof",
                "context": "Main roof structure type",
                "location": "Drawing title block",
                "confidence": 0.98
            },
            {
                "term": "Valley Flashing",
                "context": "W-type valley construction",
                "location": "Detail A",
                "confidence": 0.95
            },
            {
                "term": "Ridge Vent",
                "context": "Continuous ridge ventilation system",
                "location": "Section B-B",
                "confidence": 0.93
            }
        ]
    
    def _extract_measurements(self) -> List[Dict[str, Any]]:
        """Extract measurements from document"""
        return [
            {
                "type": "area",
                "value": 2456,
                "unit": "sq ft",
                "description": "Total roof area",
                "confidence": 0.97
            },
            {
                "type": "dimension",
                "value": 48,
                "unit": "ft",
                "description": "Ridge length",
                "confidence": 0.95
            },
            {
                "type": "slope",
                "value": "6:12",
                "unit": "pitch",
                "description": "Main roof pitch",
                "confidence": 0.98
            },
            {
                "type": "height",
                "value": 24.5,
                "unit": "ft",
                "description": "Ridge height from eave",
                "confidence": 0.94
            }
        ]
    
    def _extract_specifications(self) -> List[Dict[str, Any]]:
        """Extract material and construction specifications"""
        return [
            {
                "category": "shingles",
                "specification": "Architectural asphalt shingles",
                "details": {
                    "warranty": "30 years",
                    "wind_rating": "110 mph",
                    "fire_rating": "Class A",
                    "weight": "240 lbs/square"
                },
                "confidence": 0.96
            },
            {
                "category": "underlayment",
                "specification": "Synthetic roofing underlayment",
                "details": {
                    "type": "Non-woven synthetic",
                    "weight": "48 lbs/roll",
                    "coverage": "10 squares/roll",
                    "slip_resistance": "Yes"
                },
                "confidence": 0.94
            },
            {
                "category": "flashing",
                "specification": "Aluminum step flashing",
                "details": {
                    "thickness": "0.019 inches",
                    "width": "5 inches",
                    "length": "7 inches",
                    "color": "Mill finish"
                },
                "confidence": 0.93
            }
        ]
    
    def _extract_annotations(self) -> List[Dict[str, Any]]:
        """Extract annotations and notes from document"""
        return [
            {
                "type": "construction_note",
                "text": "Install ice barrier min. 24\" from exterior wall",
                "location": "Eave detail",
                "importance": "high",
                "confidence": 0.95
            },
            {
                "type": "revision",
                "text": "Rev. A - Updated valley detail per engineer",
                "date": "2024-03-15",
                "author": "JDS",
                "confidence": 0.97
            },
            {
                "type": "specification_note",
                "text": "All fasteners to be corrosion-resistant",
                "applies_to": "Entire roof system",
                "confidence": 0.96
            }
        ]
    
    async def analyze_roof_system(
        self,
        extraction_result: QwenExtractionResult
    ) -> Dict[str, Any]:
        """
        Analyze extracted data to understand the complete roof system.
        
        Args:
            extraction_result: Result from text extraction
            
        Returns:
            Comprehensive roof system analysis
        """
        measurements = extraction_result.measurements
        specifications = extraction_result.specifications
        
        # Calculate derived measurements
        total_area = sum(m["value"] for m in measurements if m["type"] == "area")
        
        # Identify roof type and complexity
        roof_type = self._identify_roof_type(extraction_result.technical_terms)
        complexity = self._assess_complexity(measurements, extraction_result.technical_terms)
        
        # Material requirements
        material_requirements = self._calculate_material_requirements(
            total_area,
            specifications
        )
        
        return {
            "roof_system": {
                "type": roof_type,
                "complexity": complexity,
                "total_area": total_area,
                "measurements": measurements,
                "specifications": specifications
            },
            "material_requirements": material_requirements,
            "special_considerations": self._extract_special_considerations(
                extraction_result.annotations
            ),
            "confidence_score": extraction_result.confidence_score
        }
    
    def _identify_roof_type(self, technical_terms: List[Dict[str, Any]]) -> str:
        """Identify roof type from technical terms"""
        roof_types = {
            "hip": "Hip Roof",
            "gable": "Gable Roof",
            "mansard": "Mansard Roof",
            "flat": "Flat Roof",
            "shed": "Shed Roof"
        }
        
        for term in technical_terms:
            term_lower = term["term"].lower()
            for key, roof_type in roof_types.items():
                if key in term_lower:
                    return roof_type
        
        return "Complex/Mixed"
    
    def _assess_complexity(
        self,
        measurements: List[Dict[str, Any]],
        technical_terms: List[Dict[str, Any]]
    ) -> str:
        """Assess roof complexity based on extracted data"""
        complexity_factors = 0
        
        # Check for multiple roof areas
        area_count = len([m for m in measurements if m["type"] == "area"])
        if area_count > 2:
            complexity_factors += 2
        elif area_count > 1:
            complexity_factors += 1
        
        # Check for complex features
        complex_features = ["valley", "dormer", "cricket", "turret"]
        for term in technical_terms:
            if any(feature in term["term"].lower() for feature in complex_features):
                complexity_factors += 1
        
        # Determine complexity level
        if complexity_factors >= 3:
            return "high"
        elif complexity_factors >= 1:
            return "medium"
        else:
            return "low"
    
    def _calculate_material_requirements(
        self,
        total_area: float,
        specifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate material requirements based on area and specifications"""
        # Add 10% waste factor
        area_with_waste = total_area * 1.1
        
        # Calculate squares (100 sq ft = 1 square)
        squares = area_with_waste / 100
        
        # Shingle bundles (typically 3 bundles per square)
        shingle_bundles = int(squares * 3) + 1
        
        # Underlayment rolls (typically 10 squares per roll)
        underlayment_rolls = int(squares / 10) + 1
        
        # Ridge cap (linear feet - estimate based on area)
        ridge_cap_lf = int(total_area ** 0.5 * 2)  # Rough estimate
        
        return {
            "shingles": {
                "squares": round(squares, 1),
                "bundles": shingle_bundles,
                "specification": next(
                    (s for s in specifications if s["category"] == "shingles"),
                    None
                )
            },
            "underlayment": {
                "rolls": underlayment_rolls,
                "coverage_sqft": underlayment_rolls * 1000,
                "specification": next(
                    (s for s in specifications if s["category"] == "underlayment"),
                    None
                )
            },
            "ridge_cap": {
                "linear_feet": ridge_cap_lf,
                "pieces": int(ridge_cap_lf / 3) + 1  # 3 ft pieces
            },
            "accessories": {
                "drip_edge_lf": int(total_area ** 0.5 * 4 * 1.1),
                "valley_flashing_lf": 0,  # Would be calculated from valley detection
                "step_flashing_pieces": 0  # Would be calculated from wall intersections
            }
        }
    
    def _extract_special_considerations(
        self,
        annotations: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract special considerations from annotations"""
        considerations = []
        
        high_importance = [a for a in annotations if a.get("importance") == "high"]
        for annotation in high_importance:
            considerations.append(annotation["text"])
        
        # Add construction notes
        construction_notes = [
            a for a in annotations 
            if a.get("type") == "construction_note"
        ]
        for note in construction_notes:
            if note["text"] not in considerations:
                considerations.append(note["text"])
        
        return considerations
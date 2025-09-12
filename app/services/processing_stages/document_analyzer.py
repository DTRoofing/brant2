import logging
from typing import Dict, Any
from pathlib import Path
import re

from app.models.processing import DocumentAnalysis, DocumentType
from app.services.google_services import google_service
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Stage 1: Analyze document type and determine processing strategy"""
    
    def __init__(self):
        self.google_service = google_service
        self.claude_service = claude_service
    
    async def analyze_document(self, file_path: str) -> DocumentAnalysis:
        """
        Analyze a document to determine its type and processing strategy
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            DocumentAnalysis with type, confidence, and strategy
        """
        logger.info(f"Analyzing document: {file_path}")
        
        try:
            # First, try to get basic text for analysis
            basic_text = await self._extract_basic_text(file_path)
            
            # Use Claude AI to classify the document
            classification = await self._classify_with_ai(basic_text, file_path)
            
            # Determine processing strategy based on type
            strategy = self._determine_processing_strategy(classification['type'])
            
            return DocumentAnalysis(
                document_type=DocumentType(classification['type']),
                confidence=classification['confidence'],
                processing_strategy=strategy,
                metadata={
                    'file_size': Path(file_path).stat().st_size,
                    'file_extension': Path(file_path).suffix,
                    'analysis_method': 'ai_classification'
                }
            )
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            # Fallback to unknown type
            return DocumentAnalysis(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                processing_strategy="basic_extraction",
                metadata={'error': str(e)}
            )
    
    async def _extract_basic_text(self, file_path: str) -> str:
        """Extract basic text for document classification"""
        try:
            # Try Google Document AI first for better text extraction
            if self.google_service.document_ai_client:
                result = await self.google_service.process_document_with_ai(file_path)
                if result.get('text'):
                    return result['text'][:5000]  # Limit for classification
            
            # Fallback to basic PDF text extraction
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages[:3]:  # First 3 pages only
                    text += page.extract_text() + "\n"
                return text[:5000]
                
        except Exception as e:
            logger.warning(f"Basic text extraction failed: {e}")
            return ""
    
    async def _classify_with_ai(self, text: str, file_path: str) -> Dict[str, Any]:
        """Use Claude AI to classify the document type"""
        try:
            if not self.claude_service.client:
                return self._classify_with_rules(text, file_path)
            
            prompt = f"""
            Analyze this document and classify it as one of these types:
            - blueprint: Architectural drawings, plans, blueprints
            - inspection_report: Roof inspection reports, damage assessments
            - photo: Photographs of roofs, damage, or construction
            - estimate: Existing roofing estimates or quotes
            - unknown: Cannot determine type
            
            Document text (first 5000 chars):
            {text}
            
            File path: {file_path}
            
            Respond with JSON:
            {{
                "type": "blueprint|inspection_report|photo|estimate|unknown",
                "confidence": 0.0-1.0,
                "reasoning": "Why you classified it this way"
            }}
            """
            
            response = self.claude_service.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            # Extract JSON from Claude's response
            response_text = response.content[0].text
            
            # Try to extract JSON from the response
            # Claude might include additional text before/after JSON
            try:
                # Look for JSON pattern in the response
                json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Try to parse the entire response as JSON
                    result = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, use a default response
                logger.warning(f"Failed to parse Claude response as JSON: {response_text}")
                return {"type": "unknown", "confidence": 0.5, "reasoning": "JSON parsing failed"}
            
            return result
            
        except Exception as e:
            logger.warning(f"AI classification failed: {e}")
            return self._classify_with_rules(text, file_path)
    
    def _classify_with_rules(self, text: str, file_path: str) -> Dict[str, Any]:
        """Fallback rule-based classification"""
        text_lower = text.lower()
        file_lower = file_path.lower()
        
        # Rule-based classification
        if any(word in text_lower for word in ['blueprint', 'plan', 'drawing', 'architectural', 'dimensions']):
            return {"type": "blueprint", "confidence": 0.7, "reasoning": "Contains blueprint keywords"}
        elif any(word in text_lower for word in ['inspection', 'damage', 'assessment', 'condition']):
            return {"type": "inspection_report", "confidence": 0.7, "reasoning": "Contains inspection keywords"}
        elif any(word in file_lower for word in ['.jpg', '.jpeg', '.png', 'photo', 'image']):
            return {"type": "photo", "confidence": 0.8, "reasoning": "Image file detected"}
        elif any(word in text_lower for word in ['estimate', 'quote', 'proposal', 'cost', 'price']):
            return {"type": "estimate", "confidence": 0.7, "reasoning": "Contains estimate keywords"}
        else:
            return {"type": "unknown", "confidence": 0.3, "reasoning": "No clear indicators found"}
    
    def _determine_processing_strategy(self, doc_type: str) -> str:
        """Determine the best processing strategy for the document type"""
        strategies = {
            "blueprint": "google_document_ai + claude_interpretation + measurement_extraction",
            "inspection_report": "google_document_ai + claude_analysis + damage_assessment",
            "photo": "google_vision_api + claude_analysis + visual_measurement",
            "estimate": "google_document_ai + claude_extraction + cost_analysis",
            "unknown": "basic_extraction + claude_analysis"
        }
        return strategies.get(doc_type, "basic_extraction")

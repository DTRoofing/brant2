import logging
from typing import Dict, Any, Optional
from pathlib import Path
import re

from app.models.processing import DocumentAnalysis, DocumentType
from app.services.google_services import google_service
from app.services.claude_service import claude_service
from app.services.processing_stages.index_page_analyzer import IndexPageAnalyzer
from app.services.processing_stages.selective_page_extractor import selective_page_extractor
from app.core.config import settings

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    pypdf = None
    HAS_PYPDF = False

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Stage 1: Analyze document type and determine processing strategy"""
    
    def __init__(self):
        self.google_service = google_service
        self.claude_service = claude_service
        self.index_analyzer = IndexPageAnalyzer()
    
    async def _extract_basic_text(self, file_path: str, specific_pages=None) -> str:
        """Extract basic text for document classification

        Args:
            file_path: Path or GCS URI to the PDF file
            specific_pages: List of specific page numbers to extract (1-indexed), or None for first 3 pages
        """
        try:
            # Google Document AI is the preferred method as it handles both local and GCS URIs.
            if self.google_service.document_ai_client:
                result = await self.google_service.process_document_with_ai(file_path)
                if result and result.get('text'):
                    return result['text'][:5000]  # Limit for classification

            # Fallback to basic PDF text extraction ONLY for local files.
            if not file_path.startswith("gs://") and HAS_PYPDF:
                logger.warning("Falling back to pypdf for local file text extraction.")
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    text = ""
                    if specific_pages:
                        for page_num in specific_pages:
                            if 0 <= page_num - 1 < len(pdf_reader.pages):
                                text += pdf_reader.pages[page_num - 1].extract_text() + "\n"
                    else:
                        for page in pdf_reader.pages[:3]:
                            text += page.extract_text() + "\n"
                    return text[:5000]
            elif not file_path.startswith("gs://") and not HAS_PYPDF:
                logger.warning("pypdf not available for local file text extraction.")
            
            logger.warning(f"Could not extract text from {file_path} using any available method.")
            return ""
                
        except Exception as e:
            logger.warning(f"Basic text extraction failed for {file_path}: {e}")
            return ""
    
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
            # First, analyze the index page to extract metadata and identify relevant pages
            index_analysis = await self.index_analyzer.analyze_index_page(file_path)

            # Get basic text for document classification (but only from relevant pages if found)
            relevant_pages = index_analysis.get('roof_pages', [])
            basic_text = await self._extract_basic_text(file_path, relevant_pages[:3] if relevant_pages else None)

            # Use Claude AI to classify the document
            classification = await self._classify_with_ai(basic_text, file_path)

            # Determine processing strategy based on type
            strategy = self._determine_processing_strategy(classification['type'])

            # Check if we should use selective extraction for this document
            processing_file_path = file_path
            if selective_page_extractor.should_use_extraction(file_path, relevant_pages):
                if file_path.startswith("gs://"):
                    # Handle selective extraction for GCS files
                    downloaded_temp_path = None
                    extracted_temp_path = None
                    try:
                        gcs_object_name = file_path[len(f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/"):]
                        downloaded_temp_path = self.google_service.download_gcs_to_temp(gcs_object_name)
                        
                        extracted_temp_path = selective_page_extractor.extract_pages(downloaded_temp_path, relevant_pages)
                        
                        if extracted_temp_path:
                            new_gcs_object_name = self.google_service.upload_temp_to_gcs(extracted_temp_path, gcs_object_name)
                            processing_file_path = f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/{new_gcs_object_name}"
                            logger.info(f"Using selectively extracted GCS file for processing: {processing_file_path}")
                        else:
                            logger.warning("Selective page extraction for GCS file did not produce a result. Using original file.")
                    except Exception as e:
                        logger.error(f"Selective page extraction for GCS file {file_path} failed: {e}. Using original file.", exc_info=True)
                        processing_file_path = file_path # Fallback
                    finally:
                        # Cleanup local temporary files
                        for p in [downloaded_temp_path, extracted_temp_path]:
                            if p and Path(p).exists():
                                try:
                                    Path(p).unlink()
                                    logger.debug(f"Cleaned up temp file: {p}")
                                except OSError as e:
                                    logger.warning(f"Failed to cleanup temp file {p}: {e}")
                else: # It's a local file
                    # Extract only relevant pages to a temporary PDF
                    extracted_pdf = selective_page_extractor.extract_pages(file_path, relevant_pages)
                    if extracted_pdf:
                        processing_file_path = extracted_pdf
                        logger.info(f"Using extracted PDF with {len(relevant_pages)} pages instead of full document")

            # Get file metadata safely for local or GCS paths
            file_size = 0
            file_extension = ""
            if file_path.startswith("gs://"):
                gcs_object_name = file_path[len(f"gs://{settings.GOOGLE_CLOUD_STORAGE_BUCKET}/"):]
                blob = self.google_service.get_gcs_blob_metadata(gcs_object_name)
                if blob:
                    file_size = blob.size
                    file_extension = Path(blob.name).suffix
            elif not file_path.startswith("gs://"):
                path_obj = Path(file_path)
                if path_obj.exists():
                    file_size = path_obj.stat().st_size
                    file_extension = path_obj.suffix

            # Merge metadata from index analysis
            metadata = {
                'file_size': file_size,
                'file_extension': file_extension,
                'analysis_method': 'ai_classification',
                'index_analysis': index_analysis,
                'relevant_pages': relevant_pages,
                'project_metadata': index_analysis.get('metadata', {}),
                'processing_file_path': processing_file_path  # Store the path we'll actually process
            }

            return DocumentAnalysis(
                document_type=DocumentType(classification['type']),
                confidence=max(classification['confidence'], index_analysis.get('confidence', 0)),
                processing_strategy=strategy,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Document analysis failed catastrophically: {e}", exc_info=True)
            raise # Re-raise the exception to allow the pipeline orchestrator to handle it.
    
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
            - mcdonalds_roofing: Specific blueprints or reports for McDonald's properties
            - unknown: Cannot determine type
            
            Document text (first 5000 chars):
            {text}
            
            The file path is {file_path}. If the path contains "mcdonalds", it is very likely a mcdonalds_roofing document.
            
            Respond with JSON:
            {{
                "type": "blueprint|inspection_report|photo|estimate|mcdonalds_roofing|unknown",
                "confidence": 0.0-1.0,
                "reasoning": "Why you classified it this way"
            }}
            """
            
            response = self.claude_service.client.messages.create(
                model="claude-3-5-sonnet-20240620",
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
        
        # Add a specific rule for McDonald's documents based on filename
        if 'mcdonalds' in file_lower:
            return {"type": "mcdonalds_roofing", "confidence": 0.9, "reasoning": "Filename contains 'mcdonalds'"}

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
            "mcdonalds_roofing": "google_document_ai + mcdonalds_interpretation + measurement_extraction",
            "photo": "google_vision_api + claude_analysis + visual_measurement",
            "estimate": "google_document_ai + claude_extraction + cost_analysis",
            "unknown": "basic_extraction + claude_analysis"
        }
        return strategies.get(doc_type, "basic_extraction")

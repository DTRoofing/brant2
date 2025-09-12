import logging
from typing import Dict, Any, List
from pathlib import Path
import PyPDF2
from pdf2image import convert_from_path
import pytesseract

from app.models.processing import ExtractedContent, DocumentType, DocumentAnalysis
from app.services.google_services import google_service

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Stage 2: Extract content based on document type and analysis"""
    
    def __init__(self):
        self.google_service = google_service
    
    async def extract_content(self, file_path: str, analysis: DocumentAnalysis) -> ExtractedContent:
        """
        Extract content from document based on its type and analysis
        
        Args:
            file_path: Path to the PDF file
            analysis: Document analysis results
            
        Returns:
            ExtractedContent with text, images, measurements, etc.
        """
        logger.info(f"Extracting content for {analysis.document_type} document: {file_path}")
        
        try:
            if analysis.document_type == DocumentType.BLUEPRINT:
                return await self._extract_blueprint_content(file_path)
            elif analysis.document_type == DocumentType.INSPECTION_REPORT:
                return await self._extract_inspection_content(file_path)
            elif analysis.document_type == DocumentType.PHOTO:
                return await self._extract_photo_content(file_path)
            elif analysis.document_type == DocumentType.ESTIMATE:
                return await self._extract_estimate_content(file_path)
            else:
                return await self._extract_generic_content(file_path)
                
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            # Fallback to basic extraction
            return await self._extract_generic_content(file_path)
    
    async def _extract_blueprint_content(self, file_path: str) -> ExtractedContent:
        """Extract content from architectural blueprints with hybrid roof measurement"""
        logger.info("Extracting blueprint content with hybrid roof measurement")
        
        # Use Google Document AI for structured extraction
        google_result = await self.google_service.process_document_with_ai(file_path)
        
        # Get hybrid roof measurements
        from app.services.processing_stages.roof_measurement import roof_measurement_service
        roof_measurement_result = await roof_measurement_service.measure_roof_hybrid(file_path)
        
        # Extract OCR measurements
        ocr_measurements = self._extract_measurements_from_entities(google_result.get('entities', []))
        
        # Verify measurements between OCR and blueprint
        verification_result = roof_measurement_service.verify_measurements(
            ocr_measurements, 
            roof_measurement_result.get('measurements', [])
        )
        
        # Use the most reliable measurements
        if verification_result['recommendation'] == 'use_blueprint':
            final_measurements = roof_measurement_result.get('measurements', [])
            measurement_method = 'hybrid_blueprint_measurement'
            confidence = roof_measurement_result.get('confidence', 0.8)
        else:
            final_measurements = ocr_measurements
            measurement_method = 'google_document_ai'
            confidence = 0.7
        
        return ExtractedContent(
            text=google_result.get('text', ''),
            images=self._extract_images_from_pdf(file_path),
            measurements=final_measurements,
            tables=google_result.get('tables', []),
            entities=google_result.get('entities', []),
            extraction_method=measurement_method,
            confidence=confidence,
            # Add roof features and verification data
            roof_features=roof_measurement_result.get('roof_features', []),
            verification_result=verification_result
        )
    
    async def _extract_inspection_content(self, file_path: str) -> ExtractedContent:
        """Extract content from inspection reports"""
        logger.info("Extracting inspection report content")
        
        # Use Google Document AI for form field extraction
        google_result = await self.google_service.process_document_with_ai(file_path)
        
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                images=self._extract_images_from_pdf(file_path),
                measurements=self._extract_measurements_from_entities(google_result.get('entities', [])),
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai',
                confidence=0.85
            )
        else:
            return await self._extract_generic_content(file_path)
    
    async def _extract_photo_content(self, file_path: str) -> ExtractedContent:
        """Extract content from photos"""
        logger.info("Extracting photo content")
        
        vision_results = []
        temp_files = []
        
        try:
            # Convert PDF to images and use Vision API
            images = convert_from_path(file_path)
            
            for i, image in enumerate(images):
                # Save image temporarily
                temp_path = f"/tmp/page_{i}.jpg"
                temp_files.append(temp_path)
                image.save(temp_path, "JPEG")
                
                # Analyze with Vision API
                vision_result = await self.google_service.analyze_image_with_vision(temp_path)
                vision_results.append(vision_result)
        
        except Exception as e:
            logger.error(f"Photo extraction failed: {e}")
            vision_results = []
        
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")
        
        # Combine all text from images
        combined_text = "\n".join([result.get('text', '') for result in vision_results])
        
        return ExtractedContent(
            text=combined_text,
            images=[{"page": i, "analysis": result} for i, result in enumerate(vision_results)],
            measurements=self._extract_measurements_from_text(combined_text),
            tables=[],
            entities=[],
            extraction_method='google_vision_api',
            confidence=0.8
        )
    
    async def _extract_estimate_content(self, file_path: str) -> ExtractedContent:
        """Extract content from existing estimates"""
        logger.info("Extracting estimate content")
        
        # Use Google Document AI for table extraction
        google_result = await self.google_service.process_document_with_ai(file_path)
        
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                images=[],
                measurements=self._extract_measurements_from_entities(google_result.get('entities', [])),
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai',
                confidence=0.9
            )
        else:
            return await self._extract_generic_content(file_path)
    
    async def _extract_generic_content(self, file_path: str) -> ExtractedContent:
        """Fallback generic content extraction"""
        logger.info("Performing generic content extraction")
        
        try:
            # Extract text using PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # If no text, try OCR
            if len(text.strip()) < 50:
                logger.info("No text found, trying OCR...")
                try:
                    images = convert_from_path(file_path)
                    ocr_text = ""
                    for image in images:
                        ocr_text += pytesseract.image_to_string(image) + "\n"
                    text = ocr_text
                except Exception as ocr_error:
                    logger.warning(f"OCR extraction failed: {ocr_error}")
                    text = ""
            
            return ExtractedContent(
                text=text,
                images=[],
                measurements=self._extract_measurements_from_text(text),
                tables=[],
                entities=[],
                extraction_method='pypdf2_ocr',
                confidence=0.6
            )
            
        except Exception as e:
            logger.error(f"Generic extraction failed: {e}")
            return ExtractedContent(
                text="",
                images=[],
                measurements=[],
                tables=[],
                entities=[],
                extraction_method='failed',
                confidence=0.0
            )
    
    def _extract_images_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF pages"""
        try:
            images = convert_from_path(file_path)
            return [{"page": i, "size": image.size} for i, image in enumerate(images)]
        except Exception as e:
            logger.warning(f"Image extraction failed: {e}")
            return []
    
    def _extract_measurements_from_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract measurements from Document AI entities"""
        measurements = []
        for entity in entities:
            text = entity.get('text', '').lower()
            if any(keyword in text for keyword in ['sq', 'square', 'feet', 'ft', 'area', 'dimension']):
                measurements.append({
                    'text': entity.get('text', ''),
                    'confidence': entity.get('confidence', 0.0),
                    'type': 'area_measurement'
                })
        return measurements
    
    def _extract_measurements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract measurements from text using regex"""
        import re
        
        measurements = []
        
        # Look for area measurements
        area_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|square\s+feet)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sf|sqft)',
            r'area[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
        ]
        
        for pattern in area_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1).replace(',', ''))
                    measurements.append({
                        'text': match.group(0),
                        'value': value,
                        'type': 'area_measurement',
                        'confidence': 0.7
                    })
                except ValueError:
                    continue
        
        return measurements

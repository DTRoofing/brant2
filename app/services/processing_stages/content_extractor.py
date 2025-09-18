import logging
from typing import Dict, Any

from app.models.processing import DocumentAnalysis, ExtractedContent, DocumentType
from app.services.google_services import google_service

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Stage 2: Extract content from document based on analysis"""

    def __init__(self):
        self.google_service = google_service

    async def extract_content(self, doc_uri: str, analysis: DocumentAnalysis) -> ExtractedContent:
        """
        Extract content from a document using the appropriate method based on its type.

        Args:
            doc_uri: Path or GCS URI to the document.
            analysis: The result from the DocumentAnalyzer stage.

        Returns:
            ExtractedContent with text, images, tables, etc.
        """
        logger.info(f"Extracting content from {doc_uri} with type: {analysis.document_type.value}")

        doc_type = analysis.document_type
        
        # The document analyzer might have created a temporary, smaller PDF.
        # We should use that if it exists.
        processing_uri = analysis.metadata.get('processing_file_path', doc_uri)
        logger.info(f"Using processing URI: {processing_uri}")

        if doc_type in [DocumentType.BLUEPRINT, DocumentType.MCDONALDS_ROOFING]:
            return await self._extract_blueprint_content(processing_uri)
        elif doc_type == DocumentType.INSPECTION_REPORT:
            return await self._extract_report_content(processing_uri)
        elif doc_type == DocumentType.ESTIMATE:
            return await self._extract_estimate_content(processing_uri)
        elif doc_type == DocumentType.PHOTO:
            return await self._extract_photo_content(processing_uri)
        else: # UNKNOWN
            return await self._extract_generic_content(processing_uri)

    async def _extract_blueprint_content(self, doc_uri: str) -> ExtractedContent:
        """Extract content from architectural blueprints using Document AI."""
        logger.info(f"Extracting blueprint content from {doc_uri}")
        
        google_result = await self.google_service.process_document_with_ai(doc_uri)
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                images=[],
                measurements=[],
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai',
                confidence=google_result.get('confidence', 0.8)
            )
        return ExtractedContent(extraction_method='google_document_ai_failed')

    async def _extract_report_content(self, doc_uri: str) -> ExtractedContent:
        """Extract content from inspection reports."""
        logger.info(f"Extracting report content from {doc_uri}")
        google_result = await self.google_service.process_document_with_ai(doc_uri)
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai',
                confidence=google_result.get('confidence', 0.85)
            )
        return ExtractedContent(extraction_method='google_document_ai_failed')

    async def _extract_estimate_content(self, doc_uri: str) -> ExtractedContent:
        """Extract content from existing estimates."""
        logger.info(f"Extracting estimate content from {doc_uri}")
        google_result = await self.google_service.process_document_with_ai(doc_uri)
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai',
                confidence=google_result.get('confidence', 0.9)
            )
        return ExtractedContent(extraction_method='google_document_ai_failed')

    async def _extract_generic_content(self, doc_uri: str) -> ExtractedContent:
        """Generic content extraction for unknown document types."""
        logger.info(f"Extracting generic content from {doc_uri}")
        google_result = await self.google_service.process_document_with_ai(doc_uri)
        if google_result:
            return ExtractedContent(
                text=google_result.get('text', ''),
                tables=google_result.get('tables', []),
                entities=google_result.get('entities', []),
                extraction_method='google_document_ai_ocr',
                confidence=google_result.get('confidence', 0.7)
            )
        return ExtractedContent(extraction_method='google_document_ai_failed')

    async def _extract_photo_content(self, doc_uri: str) -> ExtractedContent:
        """Extract content from photos using Vision AI."""
        logger.info(f"Extracting photo content from {doc_uri}")
        vision_result = await self.google_service.process_image_with_vision_ai(doc_uri)
        if vision_result:
            return ExtractedContent(
                text=vision_result.get('text', ''),
                entities=vision_result.get('labels', []),
                extraction_method='google_vision_api',
                confidence=vision_result.get('confidence', 0.8)
            )
        return ExtractedContent(extraction_method='google_vision_api_failed')
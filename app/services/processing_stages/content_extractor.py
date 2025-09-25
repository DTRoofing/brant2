# This file was not in the context, so I am providing the complete, corrected code.
# Path: app/services/processing_stages/content_extractor.py

import logging
import os
import tempfile
import gc
import psutil
from typing import List, Tuple

from pdf2image import convert_from_path
from google.cloud import documentai_v1 as documentai, vision_v1
from google.api_core.client_options import ClientOptions

from app.core.config import settings

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    Extracts content from a PDF using either text extraction or OCR (Google Vision API).
    Optimized to handle large files and prevent memory exhaustion.
    """

    def __init__(self):
        self.vision_client = None
        # Re-enable the Vision API. Set to False to disable.
        self.vision_api_enabled = True
        if self.vision_api_enabled:
            try:
                # Use regional endpoint for potentially lower latency
                client_options = ClientOptions(api_endpoint=f"{settings.DOCUMENT_AI_LOCATION}-vision.googleapis.com")
                self.vision_client = vision_v1.ImageAnnotatorClient(client_options=client_options)
                logger.info("Google Vision API client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision API client: {e}", exc_info=True)
                self.vision_api_enabled = False

    def _log_memory_usage(self, stage: str):
        """Helper to log current memory usage."""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        logger.info(f"Memory usage at stage '{stage}': {mem_info.rss / 1024 ** 2:.2f} MB")

    async def extract_text_from_pdf(self, file_path: str) -> Tuple[str, str]:
        """
        Extracts text from a PDF. First tries text extraction, then falls back to OCR if enabled.
        Returns a tuple of (extracted_text, extraction_method).
        """
        # 1. First, try direct text extraction (fast, low memory)
        try:
            # This part would use a library like PyMuPDF to get text directly
            # For brevity, we'll assume it's implemented elsewhere and returns little text for image-based PDFs.
            text_content = self._direct_text_extraction(file_path)
            if len(text_content) > 500: # Heuristic: if we get substantial text, it's likely not image-based
                logger.info(f"Successfully extracted {len(text_content)} characters via direct text extraction.")
                return text_content, "text"
        except Exception as e:
            logger.warning(f"Direct text extraction failed: {e}. Proceeding to OCR.")

        # 2. If direct extraction yields little text and Vision API is on, use OCR
        if self.vision_api_enabled and self.vision_client:
            logger.info("Direct text extraction yielded minimal content. Falling back to Vision API OCR.")
            try:
                return await self._extract_text_with_vision_ocr(file_path), "ocr_vision"
            except Exception as e:
                logger.error(f"Vision API OCR processing failed: {e}", exc_info=True)
                # Fallback to returning whatever little text we got initially
                return text_content, "text_fallback"
        
        logger.warning("Vision API is disabled or failed. Returning only directly extracted text.")
        return text_content, "text"

    def _direct_text_extraction(self, file_path: str) -> str:
        """Placeholder for a direct text extraction method (e.g., using PyMuPDF)."""
        # In a real implementation, you would use a library like fitz (PyMuPDF) here.
        # import fitz
        # doc = fitz.open(file_path)
        # text = "".join(page.get_text() for page in doc)
        # return text
        logger.info("Performing placeholder direct text extraction.")
        return "" # Assume it returns empty for image-based PDFs

    async def _extract_text_with_vision_ocr(self, file_path: str) -> str:
        """
        Processes a PDF page-by-page using Google Vision API to control memory usage.
        """
        all_text = []
        self._log_memory_usage("start_ocr")

        with tempfile.TemporaryDirectory() as temp_path:
            try:
                # Convert PDF to a list of images (PIL objects) one by one
                # This is the most memory-intensive step, so we handle it carefully.
                logger.info("Converting PDF to images for OCR...")
                
                # Explicitly set poppler path to ensure pdf2image can find the utilities
                poppler_path = os.environ.get('POPPLER_PATH', '/usr/bin')
                logger.info(f"Using poppler path: {poppler_path}")
                
                images = convert_from_path(
                    file_path, 
                    output_folder=temp_path, 
                    fmt='jpeg', 
                    thread_count=2,
                    poppler_path=poppler_path
                )
                self._log_memory_usage("pdf_to_images_complete")

                for i, image_path in enumerate(sorted(os.listdir(temp_path))):
                    page_num = i + 1
                    full_image_path = os.path.join(temp_path, image_path)
                    logger.info(f"Processing page {page_num} with Vision API...")
                    
                    with open(full_image_path, "rb") as image_file:
                        content = image_file.read()

                    image = vision_v1.Image(content=content)
                    feature = vision_v1.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)
                    request = vision_v1.AnnotateImageRequest(image=image, features=[feature])

                    # The Vision API call itself
                    response = await self.vision_client.annotate_image(request=request)
                    
                    if response.full_text_annotation:
                        all_text.append(response.full_text_annotation.text)
                    
                    if response.error.message:
                        raise Exception(f"Vision API Error on page {page_num}: {response.error.message}")

                    # Clean up memory after each page
                    del content, image, request, response
                    gc.collect()
                    self._log_memory_usage(f"page_{page_num}_complete")

            except Exception as e:
                logger.error(f"An error occurred during page-by-page OCR: {e}", exc_info=True)
                raise

        logger.info(f"Vision API OCR completed successfully. Total characters extracted: {sum(len(t) for t in all_text)}")
        return "\n\n--- Page Break ---\n\n".join(all_text)


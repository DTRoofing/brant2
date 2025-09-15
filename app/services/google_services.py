import logging
import os
from typing import Optional, Dict, Any
from pathlib import Path
import json

from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from google.cloud import vision
from google.oauth2 import service_account

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleCloudService:
    """Service for interacting with Google Cloud APIs"""
    
    def __init__(self):
        """Initialize Google Cloud clients"""
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        self.processor_id = settings.DOCUMENT_AI_PROCESSOR_ID
        self.location = settings.DOCUMENT_AI_LOCATION or "us"
        self.bucket_name = settings.GOOGLE_CLOUD_STORAGE_BUCKET
        
        # Initialize credentials if available
        self.credentials = None
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            try:
                # Try both absolute and relative paths
                cred_paths = [
                    settings.GOOGLE_APPLICATION_CREDENTIALS,
                    os.path.abspath(settings.GOOGLE_APPLICATION_CREDENTIALS),
                    "/app/google-credentials.json",  # Docker container path
                    "./google-credentials.json"  # Local path
                ]
                
                for cred_path in cred_paths:
                    if os.path.exists(cred_path):
                        self.credentials = service_account.Credentials.from_service_account_file(
                            cred_path
                        )
                        logger.info(f"Google Cloud credentials loaded successfully from: {cred_path}")
                        break
                
                if not self.credentials:
                    logger.warning(f"Credentials file not found at any location")
            except Exception as e:
                logger.error(f"Failed to load Google Cloud credentials: {e}")
        
        # Initialize clients
        self._document_ai_client = None
        self._storage_client = None
        self._vision_client = None
    
    @property
    def document_ai_client(self):
        """Lazy initialization of Document AI client"""
        if self._document_ai_client is None and self.credentials:
            self._document_ai_client = documentai.DocumentProcessorServiceClient(
                credentials=self.credentials
            )
        return self._document_ai_client
    
    @property
    def storage_client(self):
        """Lazy initialization of Storage client"""
        if self._storage_client is None and self.credentials:
            self._storage_client = storage.Client(
                credentials=self.credentials,
                project=self.project_id
            )
        return self._storage_client
    
    @property
    def vision_client(self):
        """Lazy initialization of Vision client"""
        if self._vision_client is None and self.credentials:
            self._vision_client = vision.ImageAnnotatorClient(
                credentials=self.credentials
            )
        return self._vision_client
    
    async def upload_to_gcs(self, file_path: str, destination_blob_name: str) -> str:
        """
        Upload a file to Google Cloud Storage
        
        Args:
            file_path: Local path to the file
            destination_blob_name: Name for the file in GCS
            
        Returns:
            GCS URI of the uploaded file
        """
        if not self.storage_client or not self.bucket_name:
            logger.warning("Google Cloud Storage not configured")
            return ""
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(file_path)
            
            logger.info(f"File uploaded to GCS: gs://{self.bucket_name}/{destination_blob_name}")
            return f"gs://{self.bucket_name}/{destination_blob_name}"
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            return ""
    
    async def process_document_with_ai(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document using Google Document AI with automatic splitting for large files
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted document data (combined from all chunks if split)
        """
        if not self.document_ai_client or not self.project_id or not self.processor_id:
            logger.warning("Document AI not configured, skipping processing")
            return {}
        
        try:
            from .pdf_splitter import pdf_splitter
            
            # Check if PDF needs splitting
            if pdf_splitter.needs_splitting(file_path):
                logger.info(f"Large PDF detected, splitting into chunks: {file_path}")
                
                # Split PDF into chunks
                chunks = pdf_splitter.split_pdf(file_path)
                chunk_results = []
                
                # Process each chunk
                for i, chunk in enumerate(chunks):
                    if chunk.get('is_original', False):
                        # Original file doesn't need splitting
                        result = await self._process_single_document(chunk['file_path'])
                        chunk_results.append(result)
                    else:
                        logger.info(f"Processing chunk {i+1}/{len(chunks)}: "
                                   f"pages {chunk['start_page']}-{chunk['end_page']} "
                                   f"({chunk['file_size_mb']}MB)")
                        
                        result = await self._process_single_document(chunk['file_path'])
                        if result:
                            # Add chunk metadata to result
                            result.update({
                                'chunk_info': chunk,
                                'start_page': chunk['start_page'],
                                'end_page': chunk['end_page'],
                                'page_count': chunk['page_count']
                            })
                        chunk_results.append(result)
                
                # Merge results from all chunks
                combined_result = pdf_splitter.merge_results(chunk_results, file_path)
                
                # Clean up temporary chunk files
                pdf_splitter.cleanup_chunks(chunks)
                
                # Convert combined result to expected format
                final_result = {
                    "text": combined_result.get('combined_text', ''),
                    "pages": combined_result.get('total_pages', 0),
                    "entities": combined_result.get('combined_entities', []),
                    "tables": combined_result.get('combined_tables', []),
                    "measurements": combined_result.get('combined_measurements', []),
                    "chunk_count": combined_result.get('chunk_count', 0),
                    "chunk_summaries": combined_result.get('chunk_summaries', [])
                }
                
                logger.info(f"Combined Document AI processing complete. "
                           f"Processed {len(chunks)} chunks, "
                           f"extracted {len(final_result['text'])} characters")
                
                return final_result
            else:
                # Process single document normally
                return await self._process_single_document(file_path)
            
        except Exception as e:
            logger.error(f"Document AI processing failed: {e}")
            return {}
    
    async def _process_single_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document with Document AI (internal method)
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted document data
        """
        try:
            # Read the file
            with open(file_path, "rb") as file:
                file_content = file.read()
            
            # Check file size
            file_size_mb = len(file_content) / 1024 / 1024
            if file_size_mb > 30:
                logger.warning(f"File size {file_size_mb:.2f}MB exceeds Document AI limit")
                return {}
            
            # Create the Document AI request
            name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=file_content,
                    mime_type="application/pdf"
                )
            )
            
            # Process the document
            logger.debug(f"Processing single document with Document AI: {file_path}")
            result = self.document_ai_client.process_document(request=request)
            
            # Extract relevant information
            document_data = {
                "text": result.document.text,
                "pages": len(result.document.pages),
                "entities": [],
                "tables": [],
                "measurements": []
            }
            
            # Extract entities (form fields, key-value pairs)
            for entity in result.document.entities:
                entity_data = {
                    "type": entity.type_,
                    "text": entity.mention_text,
                    "confidence": entity.confidence
                }
                
                # Check if this might be a measurement
                if any(keyword in entity.mention_text.lower() for keyword in ["sq", "square", "feet", "ft", "area"]):
                    document_data["measurements"].append(entity_data)
                
                document_data["entities"].append(entity_data)
            
            # Extract tables if present
            for page in result.document.pages:
                for table in page.tables:
                    table_data = []
                    for row in table.body_rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = self._get_text_from_layout(cell.layout, result.document.text)
                            row_data.append(cell_text)
                        table_data.append(row_data)
                    document_data["tables"].append(table_data)
            
            logger.debug(f"Single document processing complete. Extracted {len(document_data['text'])} characters")
            return document_data
            
        except Exception as e:
            logger.error(f"Single document processing failed: {e}")
            return {}
    
    def _get_text_from_layout(self, layout, document_text: str) -> str:
        """
        Extract text from a layout element
        """
        text = ""
        for segment in layout.text_anchor.text_segments:
            start_index = segment.start_index if segment.start_index else 0
            end_index = segment.end_index
            text += document_text[start_index:end_index]
        return text.strip()
    
    async def analyze_image_with_vision(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze an image using Google Cloud Vision API
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Vision API analysis results
        """
        if not self.vision_client:
            logger.warning("Vision API not configured")
            return {}
        
        try:
            with open(file_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform text detection
            response = self.vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            result = {
                "text": texts[0].description if texts else "",
                "annotations": []
            }
            
            for text in texts[1:]:  # Skip the first one as it's the full text
                result["annotations"].append({
                    "text": text.description,
                    "bounds": [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
                })
            
            logger.info(f"Vision API processing complete for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Vision API processing failed: {e}")
            return {}


# Singleton instance
google_service = GoogleCloudService()
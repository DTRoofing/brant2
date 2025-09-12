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
                if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                    self.credentials = service_account.Credentials.from_service_account_file(
                        settings.GOOGLE_APPLICATION_CREDENTIALS
                    )
                    logger.info("Google Cloud credentials loaded successfully")
                else:
                    logger.warning(f"Credentials file not found: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
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
        Process a document using Google Document AI
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted document data
        """
        if not self.document_ai_client or not self.project_id or not self.processor_id:
            logger.warning("Document AI not configured, skipping processing")
            return {}
        
        try:
            # Read the file
            with open(file_path, "rb") as file:
                file_content = file.read()
            
            # Create the Document AI request
            name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
            
            document = documentai.Document(
                content=file_content,
                mime_type="application/pdf"
            )
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=file_content,
                    mime_type="application/pdf"
                )
            )
            
            # Process the document
            logger.info(f"Processing document with Document AI: {file_path}")
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
            
            logger.info(f"Document AI processing complete. Extracted {len(document_data['text'])} characters")
            return document_data
            
        except Exception as e:
            logger.error(f"Document AI processing failed: {e}")
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
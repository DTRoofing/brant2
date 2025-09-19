import logging
from typing import TYPE_CHECKING, Optional, Dict, Any
from pathlib import Path
import tempfile
import uuid
from datetime import timedelta

try:
    from google.cloud import documentai, vision, storage
    from google.cloud.storage import Client as StorageClient, Bucket, Blob
    from google.api_core.exceptions import GoogleAPICallError, RetryError
    HAS_GOOGLE_CLOUD = True
except ImportError as e:
    logging.warning(f"Google Cloud libraries not available: {e}")
    documentai = None
    vision = None
    storage = None
    StorageClient = None
    Bucket = None
    Blob = None
    GoogleAPICallError = Exception
    RetryError = Exception
    HAS_GOOGLE_CLOUD = False

if TYPE_CHECKING:
    from google.cloud.documentai import DocumentProcessorServiceClient
    from google.cloud.vision import ImageAnnotatorClient
else:
    DocumentProcessorServiceClient = None
    ImageAnnotatorClient = None

from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleService:
    def __init__(self):
        self.document_ai_client: Optional[DocumentProcessorServiceClient] = None
        self.vision_ai_client: Optional[ImageAnnotatorClient] = None
        self.storage_client: Optional[StorageClient] = None
        self.processor_name: Optional[str] = None

    def initialize_clients(self):
        """Initializes all Google Cloud clients. Should be called once per worker process."""
        if not HAS_GOOGLE_CLOUD:
            logger.warning("Google Cloud libraries not available. Document AI and Vision AI will be disabled.")
            return

        # Initialize clients only if they haven't been already for this process
        if self.document_ai_client is None:
            if settings.GOOGLE_CLOUD_PROJECT_ID and settings.DOCUMENT_AI_LOCATION and settings.DOCUMENT_AI_PROCESSOR_ID:
                try:
                    client_options = {"api_endpoint": f"{settings.DOCUMENT_AI_LOCATION}-documentai.googleapis.com"}
                    self.document_ai_client = documentai.DocumentProcessorServiceClient(client_options=client_options)
                    self.processor_name = self.document_ai_client.processor_path(
                        settings.GOOGLE_CLOUD_PROJECT_ID, settings.DOCUMENT_AI_LOCATION, settings.DOCUMENT_AI_PROCESSOR_ID
                    )
                    logger.info("Google Document AI client initialized successfully for this process.")
                except Exception as e:
                    logger.error(f"Failed to initialize Google Document AI client: {e}")

        if self.vision_ai_client is None:
            try:
                self.vision_ai_client = vision.ImageAnnotatorClient()
                logger.info("Google Vision AI client initialized successfully for this process.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision AI client: {e}")

        if self.storage_client is None:
            try:
                self.storage_client = storage.Client()
                logger.info("Google Cloud Storage client initialized successfully for this process.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Cloud Storage client: {e}")

    def _get_mime_type_from_uri(self, uri: str) -> str:
        """Infers the MIME type from a file URI's extension."""
        lower_uri = uri.lower()
        if lower_uri.endswith(".pdf"):
            return "application/pdf"
        if lower_uri.endswith(".png"):
            return "image/png"
        if lower_uri.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        if lower_uri.endswith((".tif", ".tiff")):
            return "image/tiff"
        logger.warning(f"Could not determine MIME type for {uri}, defaulting to application/pdf.")
        return "application/pdf"  # Default fallback

    async def process_document_with_ai(self, doc_uri: str) -> Optional[Dict[str, Any]]:
        """
        Processes a document from a URI using Document AI.
        The URI can be a local file path or a GCS URI.
        """
        if not HAS_GOOGLE_CLOUD:
            logger.warning("Google Cloud libraries not available. Cannot process document with Document AI.")
            return None
            
        if not self.document_ai_client or not self.processor_name:
            logger.error("Document AI client not initialized. Cannot process document.")
            raise RuntimeError("Document AI client is not configured.")

        logger.info(f"Processing document with Document AI: {doc_uri}")

        request = None
        if doc_uri.startswith("gs://"):
            logger.info("Processing as GCS document.")
            mime_type = self._get_mime_type_from_uri(doc_uri)
            gcs_document = documentai.GcsDocument(gcs_uri=doc_uri, mime_type=mime_type)
            request = documentai.ProcessRequest(
                name=self.processor_name, gcs_document=gcs_document, skip_human_review=True
            )
        else:
            logger.warning(f"Processing as local file: {doc_uri}. This is not recommended for production.")
            try:
                mime_type = self._get_mime_type_from_uri(doc_uri)
                with open(doc_uri, "rb") as f:
                    content = f.read()
                raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
                request = documentai.ProcessRequest(
                    name=self.processor_name, raw_document=raw_document, skip_human_review=True
                )
            except FileNotFoundError:
                logger.error(f"Local file not found: {doc_uri}")
                raise

        if not request:
            raise ValueError("Could not create a valid Document AI request.")

        try:
            result = self.document_ai_client.process_document(request=request)
            document = result.document
            
            # Process all pages for tables and calculate average confidence
            all_tables = []
            total_confidence = 0.0
            if document.pages:
                for page in document.pages:
                    total_confidence += page.confidence
                    for table in page.tables:
                        all_tables.append(self._parse_table(table))

            # Store raw response for debugging (best practice)
            raw_response = {
                "document_text": document.text,
                "pages_count": len(document.pages) if document.pages else 0,
                "entities_count": len(document.entities) if document.entities else 0,
                "tables_count": len(all_tables)
            }
            logger.debug(f"Document AI raw response for {doc_uri}: {raw_response}")

            return {
                "text": document.text,
                "tables": all_tables,
                "entities": [self._parse_entity(entity) for entity in document.entities],
                "confidence": (total_confidence / len(document.pages)) if document.pages else 0.0,
                "raw_response": raw_response  # Store for debugging
            }
        except GoogleAPICallError as e:
            # Handle quota limits gracefully (best practice)
            if 'quota' in str(e).lower() or 'quota_exceeded' in str(e).lower():
                logger.error(f"Document AI quota exceeded for {doc_uri}: {e}")
                raise RuntimeError("Document AI quota exceeded. Please try again later.")
            elif 'permission' in str(e).lower() or 'forbidden' in str(e).lower():
                logger.error(f"Document AI permission denied for {doc_uri}: {e}")
                raise RuntimeError("Document AI access denied. Check credentials and permissions.")
            else:
                logger.error(f"Document AI API call failed for {doc_uri}: {e}")
                raise
        except RetryError as e:
            logger.error(f"Document AI retry failed for {doc_uri}: {e}")
            raise RuntimeError("Document AI service temporarily unavailable. Please try again.")
        except Exception as e:
            logger.error(f"Document AI processing failed for {doc_uri}: {e}", exc_info=True)
            raise

    async def process_image_with_vision_ai(self, image_uri: str) -> Optional[Dict[str, Any]]:
        """Processes an image from a URI using Vision AI."""
        if not HAS_GOOGLE_CLOUD:
            logger.warning("Google Cloud libraries not available. Cannot process image with Vision AI.")
            return None
            
        if not self.vision_ai_client:
            raise RuntimeError("Vision AI client is not configured.")

        logger.info(f"Processing image with Vision AI: {image_uri}")
        
        image = vision.Image()
        if image_uri.startswith("gs://"):
            image.source.image_uri = image_uri
        else:
            with open(image_uri, "rb") as image_file:
                content = image_file.read()
            image.content = content

        try:
            response = self.vision_ai_client.label_detection(image=image)
            labels = response.label_annotations
            text_response = self.vision_ai_client.text_detection(image=image)
            texts = text_response.text_annotations

            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")

            # Store raw response for debugging (best practice)
            raw_response = {
                "labels_count": len(labels) if labels else 0,
                "text_annotations_count": len(texts) if texts else 0,
                "has_text": bool(texts and texts[0].description)
            }
            logger.debug(f"Vision AI raw response for {image_uri}: {raw_response}")

            return {
                "labels": [{"description": label.description, "score": label.score} for label in labels],
                "text": texts[0].description if texts else "",
                "confidence": labels[0].score if labels else 0.0,
                "raw_response": raw_response  # Store for debugging
            }
        except GoogleAPICallError as e:
            # Handle quota limits gracefully (best practice)
            if 'quota' in str(e).lower() or 'quota_exceeded' in str(e).lower():
                logger.error(f"Vision AI quota exceeded for {image_uri}: {e}")
                raise RuntimeError("Vision AI quota exceeded. Please try again later.")
            elif 'permission' in str(e).lower() or 'forbidden' in str(e).lower():
                logger.error(f"Vision AI permission denied for {image_uri}: {e}")
                raise RuntimeError("Vision AI access denied. Check credentials and permissions.")
            else:
                logger.error(f"Vision AI API call failed for {image_uri}: {e}")
                raise
        except RetryError as e:
            logger.error(f"Vision AI retry failed for {image_uri}: {e}")
            raise RuntimeError("Vision AI service temporarily unavailable. Please try again.")
        except Exception as e:
            logger.error(f"Vision AI processing failed for {image_uri}: {e}", exc_info=True)
            raise

    def _parse_table(self, table: documentai.Document.Page.Table) -> dict:
        return {"row_count": table.header_rows, "column_count": table.body_rows}

    def _parse_entity(self, entity: documentai.Document.Entity) -> dict:
        return {"type": entity.type_, "text": entity.mention_text, "confidence": entity.confidence}

    def download_gcs_to_temp(self, gcs_object_name: str) -> str:
        """Downloads a GCS object to a local temporary file."""
        if not self.storage_client:
            raise RuntimeError("GCS storage client not initialized.")
        
        bucket = self.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(gcs_object_name).suffix) as tmp:
            temp_local_path = tmp.name
        
        logger.info(f"Downloading {gcs_object_name} to temporary file {temp_local_path}")
        
        try:
            blob = bucket.blob(gcs_object_name)
            blob.download_to_filename(temp_local_path)
            return temp_local_path
        except Exception as e:
            logger.error(f"Failed to download GCS object {gcs_object_name}: {e}")
            if Path(temp_local_path).exists():
                Path(temp_local_path).unlink()
            raise

    def upload_temp_to_gcs(self, local_file_path: str, original_gcs_name: str) -> str:
        """Uploads a local temporary file to GCS and returns the new object name."""
        if not self.storage_client:
            raise RuntimeError("GCS storage client not initialized.")

        bucket = self.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)

        # Create a unique name in a dedicated 'extracted' folder to keep things organized
        new_gcs_name = f"extracted/{uuid.uuid4()}/{Path(original_gcs_name).name}"
        logger.info(f"Uploading {local_file_path} to GCS as {new_gcs_name}")
        
        try:
            blob = bucket.blob(new_gcs_name)
            blob.upload_from_filename(local_file_path)
            return new_gcs_name
        except Exception as e:
            logger.error(f"Failed to upload {local_file_path} to GCS: {e}")
            raise

    def get_gcs_blob_metadata(self, gcs_object_name: str) -> Optional[Blob]:
        """Fetches the metadata for a blob in GCS."""
        if not self.storage_client:
            logger.warning("GCS storage client not initialized, cannot fetch metadata.")
            return None
        
        try:
            bucket = self.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
            return bucket.get_blob(gcs_object_name)
        except Exception as e:
            logger.error(f"Failed to get GCS blob metadata for {gcs_object_name}: {e}")
            return None

    def generate_upload_signed_url_v4(self, gcs_object_name: str, content_type: str, size: int) -> str:
        """
        Generates a v4 signed URL for uploading a file, with content restrictions.
        """
        if not self.storage_client:
            raise RuntimeError("GCS storage client not initialized.")

        # Enforce file size limit from settings
        if size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File size {size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes.")

        bucket = self.storage_client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(gcs_object_name)

        # Generate a URL that is valid for 15 minutes
        expiration = timedelta(minutes=15)

        # Enforce content type and size via headers
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(size),
        }

        url = blob.generate_signed_url(version="v4", expiration=expiration, method="PUT", headers=headers)
        return url

google_service = GoogleService()
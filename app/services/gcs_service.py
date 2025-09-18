import datetime
import os
from typing import Optional
from google.cloud import storage
from google.api_core.exceptions import GoogleAPICallError, RetryError, Forbidden, NotFound
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GCSService:
    def __init__(self):
        self.client = None
        self.bucket = None
        self.bucket_name = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of GCS client."""
        if self._initialized:
            return
        
        try:
            # Set the credentials path if it's configured
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
                logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            
            self.client = storage.Client()
            self.bucket_name = settings.GOOGLE_CLOUD_STORAGE_BUCKET
            if not self.bucket_name:
                raise ValueError("GOOGLE_CLOUD_STORAGE_BUCKET is not set.")
            self.bucket = self.client.bucket(self.bucket_name)
            self._initialized = True
            logger.info("Google Cloud Storage client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage client: {e}")
            self.client = None
            self.bucket = None
            self._initialized = False

    def generate_upload_signed_url(self, blob_name: str, content_type: str) -> Optional[str]:
        """Generate a signed URL for secure file upload with proper error handling."""
        self._initialize()
        if not self.bucket:
            logger.error("GCS bucket not initialized.")
            return None
        
        # Validate input parameters
        if not blob_name or not content_type:
            logger.error("Invalid parameters: blob_name and content_type are required.")
            return None
        
        # Sanitize blob name to prevent path traversal attacks
        if ".." in blob_name or blob_name.startswith("/"):
            logger.error(f"Invalid blob name: {blob_name}. Path traversal not allowed.")
            return None
        
        blob = self.bucket.blob(blob_name)

        try:
            # The URL is valid for 15 minutes (best practice: short expiration)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="PUT",
                content_type=content_type,
            )
            logger.info(f"Generated signed URL for {blob_name} with content type {content_type}")
            return url
        except Forbidden as e:
            logger.error(f"Permission denied generating signed URL for {blob_name}: {e}")
            return None
        except GoogleAPICallError as e:
            logger.error(f"GCS API error generating signed URL for {blob_name}: {e}")
            return None
        except RetryError as e:
            logger.error(f"GCS retry failed generating signed URL for {blob_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating signed URL for {blob_name}: {e}")
            return None

    def download_to_file(self, blob_name: str, destination_file_path: str) -> bool:
        """Downloads a blob from the bucket to a local file with proper error handling."""
        self._initialize()
        if not self.bucket:
            logger.error("GCS bucket not initialized.")
            return False

        # Validate input parameters
        if not blob_name or not destination_file_path:
            logger.error("Invalid parameters: blob_name and destination_file_path are required.")
            return False

        # Sanitize blob name to prevent path traversal attacks
        if ".." in blob_name or blob_name.startswith("/"):
            logger.error(f"Invalid blob name: {blob_name}. Path traversal not allowed.")
            return False

        try:
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists before attempting download
            if not blob.exists():
                logger.error(f"Blob {blob_name} does not exist in bucket {self.bucket_name}")
                return False
                
            blob.download_to_filename(destination_file_path)
            logger.info(f"Blob {blob_name} downloaded to {destination_file_path}.")
            return True
        except NotFound as e:
            logger.error(f"Blob {blob_name} not found: {e}")
            return False
        except Forbidden as e:
            logger.error(f"Permission denied downloading {blob_name}: {e}")
            return False
        except GoogleAPICallError as e:
            logger.error(f"GCS API error downloading {blob_name}: {e}")
            return False
        except RetryError as e:
            logger.error(f"GCS retry failed downloading {blob_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {blob_name}: {e}")
            return False

gcs_service = GCSService()
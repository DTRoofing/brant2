from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import logging
import os

# --- Google Secret Manager Integration ---
# This block will only be active if the google-cloud-secret-manager library is installed.


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5432/brant_roofing", description="Database connection URL")
    POSTGRES_DB: str = "brant_roofing"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"

    # Redis/Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", description="Celery result backend URL")

    # Application
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = False
    PORT: int = Field(default=8080, description="Application port (Cloud Run uses PORT env var)")
    API_KEY: Optional[str] = None
    MAX_FILE_SIZE: int = 209715200  # 200MB
    FAILED_DOC_CLEANUP_HOURS: int = 24  # Hours after which failed documents are cleaned up
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = Field(default=None, description="Required Google Cloud Project ID")
    DOCUMENT_AI_PROCESSOR_ID: Optional[str] = Field(default=None, description="Required Document AI Processor ID")
    DOCUMENT_AI_LOCATION: str = Field(default="us", description="Document AI Location")
    GOOGLE_CLOUD_STORAGE_BUCKET: Optional[str] = Field(default=None, description="Required Google Cloud Storage Bucket")
    GOOGLE_STUDIO_API_KEY: Optional[str] = None
    ENABLE_GOOGLE_VISION: bool = False
    GOOGLE_VISION_API_KEY: Optional[str] = None
    
    # Database SSL mode. Set to "require" in production, "disable" for local dev.
    DB_SSL_MODE: str = "disable"
    
    # CORS Configuration
    CORS_ORIGINS: list = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "https://dtrooftools.com,https://www.dtrooftools.com,http://localhost:3000,http://localhost:3001").split(","),
        description="Allowed CORS origins"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # The Model Version for Claude
    CLAUDE_MODEL_VERSION: str = "claude-3-5-sonnet-20240620"
    
    def validate_required_config(self):
        """Validate required configuration when actually needed"""
        if not self.GOOGLE_CLOUD_PROJECT_ID or self.GOOGLE_CLOUD_PROJECT_ID == "your-project-id-here":
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID must be set to a valid project ID")
        if not self.DOCUMENT_AI_PROCESSOR_ID or self.DOCUMENT_AI_PROCESSOR_ID == "your-processor-id-here":
            raise ValueError("DOCUMENT_AI_PROCESSOR_ID must be set to a valid processor ID")
        if not self.GOOGLE_CLOUD_STORAGE_BUCKET or self.GOOGLE_CLOUD_STORAGE_BUCKET == "your-bucket-name-here":
            raise ValueError("GOOGLE_CLOUD_STORAGE_BUCKET must be set to a valid bucket name")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "allow"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """
            If running in a GCP environment and no local credentials file, fetch secrets from Google Secret Manager.
            Otherwise, fall back to the default .env file loading.
            """
            # Only use Secret Manager if GCP_PROJECT is set AND no local credentials file exists
            if os.getenv("GCP_PROJECT") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                from google.cloud import secretmanager

                client = secretmanager.SecretManagerServiceClient()
                project_id = os.getenv("GCP_PROJECT")
                
                # Define which environment variables should be fetched from Secret Manager
                # The secret ID in Secret Manager should match the environment variable name.
                secrets_to_fetch = {
                    # Database
                    "DATABASE_URL",
                    "POSTGRES_DB",
                    "POSTGRES_USER",
                    "POSTGRES_PASSWORD",
                    # Celery
                    "CELERY_BROKER_URL",
                    "CELERY_RESULT_BACKEND",
                    "REDIS_URL",
                    # Application
                    "SECRET_KEY",
                    "API_KEY",
                    # AI Services
                    "ANTHROPIC_API_KEY",
                    "GOOGLE_STUDIO_API_KEY",
                    "GOOGLE_VISION_API_KEY",
                    # GCP Config (managed as secrets for consistency)
                    "GOOGLE_CLOUD_PROJECT_ID",
                    "GOOGLE_CLOUD_STORAGE_BUCKET",
                    "DOCUMENT_AI_PROCESSOR_ID",
                    "DOCUMENT_AI_LOCATION",
                    # Google Credentials
                    "GOOGLE_APPLICATION_CREDENTIALS",
                }

                # For a production environment, some secrets are non-negotiable.
                # If these can't be fetched, the application should fail fast.
                critical_secrets = {
                    "DATABASE_URL",
                    "CELERY_BROKER_URL",
                    "ANTHROPIC_API_KEY",
                    "SECRET_KEY",
                }

                gcp_secrets = {}
                for secret_id in secrets_to_fetch:
                    # Only fetch if the variable is not already set (e.g., by the OS)
                    if secret_id not in os.environ:
                        try:
                            # Convert ENV_VAR_NAME to brant-env-var-name to match Terraform convention
                            gcp_secret_name = f"brant-{secret_id.lower().replace('_', '-')}"
                            name = f"projects/{project_id}/secrets/{gcp_secret_name}/versions/latest"
                            response = client.access_secret_version(name=name)
                            gcp_secrets[secret_id] = response.payload.data.decode("UTF-8")
                        except Exception as e:
                            # If a critical secret is missing, raise an exception to halt startup.
                            if secret_id in critical_secrets:
                                logging.critical(f"CRITICAL: Could not fetch mandatory secret '{gcp_secret_name}' (for env var '{secret_id}'). Shutting down. Error: {e}")
                                raise ValueError(f"Missing critical secret: {secret_id}") from e
                            logging.warning(f"Could not fetch optional secret '{gcp_secret_name}' (for env var '{secret_id}'). Falling back. Error: {e}")
                
                # GCP secrets take precedence over .env file but not over existing env vars
                return (init_settings, env_settings, lambda: gcp_secrets, file_secret_settings)

            return (init_settings, env_settings, file_secret_settings)

settings = Settings()
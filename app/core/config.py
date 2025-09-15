from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Redis/Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Application
    SECRET_KEY: str
    DEBUG: bool = False
    PORT: int = 3001
    API_KEY: Optional[str] = None
    MAX_FILE_SIZE: int = 209715200  # 200MB
    
    # File Processing
    UPLOAD_DIR: str = "/app/uploads"
    UPLOAD_PATH: Optional[str] = None
    FAILED_DOC_CLEANUP_HOURS: int = 24
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    DOCUMENT_AI_PROCESSOR_ID: Optional[str] = None
    DOCUMENT_AI_LOCATION: Optional[str] = None
    GOOGLE_CLOUD_STORAGE_BUCKET: Optional[str] = None
    GOOGLE_STUDIO_API_KEY: Optional[str] = None
    ENABLE_GOOGLE_VISION: bool = False
    GOOGLE_VISION_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env
        
        # Override with Docker-specific env file if it exists
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            import os
            if os.path.exists('.env.docker'):
                # In Docker, use .env.docker for overrides
                return (init_settings, env_settings, file_secret_settings)
            return (init_settings, env_settings, file_secret_settings)

settings = Settings()
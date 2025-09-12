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
    MAX_FILE_SIZE: int = 104857600
    
    # File Processing
    UPLOAD_DIR: str = "/app/uploads"
    UPLOAD_PATH: Optional[str] = None
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    DOCUMENT_AI_PROCESSOR_ID: Optional[str] = None
    DOCUMENT_AI_LOCATION: Optional[str] = None
    GOOGLE_CLOUD_STORAGE_BUCKET: Optional[str] = None
    GOOGLE_STUDIO_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()
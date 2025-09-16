# Root folder: .env.gcp
# ====================================
# DT Roofing Agent - Google Cloud Configuration
# ====================================

# REQUIRED: Your Google Cloud Project Configuration
GOOGLE_CLOUD_PROJECT=your-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=/secrets/service-account.json
PROJECT_ID=your-project-id-here
REGION=us-central1

# Database Configuration (Cloud SQL)
# Replace with your Cloud SQL instance details
DATABASE_URL=postgresql://roofing_user:YOUR_DB_PASSWORD@YOUR_CLOUD_SQL_IP:5432/roofing_db
CLOUD_SQL_CONNECTION_NAME=your-project-id:us-central1:dt-roofing-db

# Redis Configuration (Cloud Memorystore)
# Replace with your Memorystore Redis instance details
CELERY_BROKER_URL=redis://YOUR_REDIS_IP:6379/0
CELERY_RESULT_BACKEND=redis://YOUR_REDIS_IP:6379/0
REDIS_HOST=YOUR_REDIS_IP
REDIS_PORT=6379

# Cloud Storage Configuration
CLOUD_STORAGE_BUCKET=your-project-id-roofing-uploads
UPLOAD_METHOD=cloud_storage  # Options: local, cloud_storage

# Application Security
SECRET_KEY=your-super-secret-key-generate-with-openssl
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-32-byte-encryption-key

# Application Settings
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
API_VERSION=v1

# CORS Configuration for Production
CORS_ORIGINS=["https://your-domain.com","https://api.your-domain.com"]

# File Processing Configuration
MAX_FILE_SIZE=104857600  # 100MB
SUPPORTED_FORMATS=["pdf"]
TESSERACT_CONFIG=--oem 3 --psm 6
MIN_CONFIDENCE_THRESHOLD=0.7

# OCR and AI Services
GOOGLE_VISION_API_ENABLED=true
OPENAI_API_KEY=your-openai-api-key-if-using
ANTHROPIC_API_KEY=your-anthropic-api-key-if-using

# Monitoring and Logging
GOOGLE_CLOUD_LOGGING_ENABLED=true
GOOGLE_CLOUD_MONITORING_ENABLED=true
SENTRY_DSN=your-sentry-dsn-for-error-tracking

# Email Configuration (using SendGrid or Gmail)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@your-domain.com

# Celery Configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_SOFT_TIME_LIMIT=600
CELERY_TASK_TIME_LIMIT=1200
CELERY_WORKER_MAX_TASKS_PER_CHILD=50

# Cloud Run Specific
PORT=8080
CLOUD_RUN_SERVICE_NAME=dt-roofing-api
CLOUD_RUN_REGION=us-central1

# Feature Flags
ENABLE_OCR_PROCESSING=true
ENABLE_AI_MEASUREMENTS=true
ENABLE_MANUAL_OVERRIDE=true
ENABLE_BATCH_PROCESSING=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Backup and Recovery
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
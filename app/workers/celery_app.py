from celery import Celery
from app.core.config import settings

# The Celery app instance is configured with the broker and backend URLs from settings.
# It uses Memorystore if enabled, otherwise falls back to local Redis.
celery_app = Celery(
    "tasks",
    broker=settings.get_celery_broker_url(),
    backend=settings.get_celery_result_backend_url(),
    include=[
        "app.workers.tasks.new_pdf_processing",
        "app.workers.document_processor",
    ],
)

# Optional Celery configuration
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,  # Store results for 1 hour
    broker_connection_retry_on_startup=True,
)
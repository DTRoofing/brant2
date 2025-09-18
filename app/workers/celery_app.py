from celery import Celery
from app.core.config import settings

# The Celery app instance is configured with the broker and backend URLs from settings.
# It's also configured to automatically discover tasks in the specified modules.
celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
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
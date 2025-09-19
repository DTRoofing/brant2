# ---- Builder Stage ----
# This stage installs dependencies and builds wheels.
FROM python:3.11-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry dependency files
COPY poetry.lock pyproject.toml ./

# Install dependencies using poetry, without creating a virtualenv
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# ---- Final Stage ----
# This is the final, minimal image that will be deployed.
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for PDF processing and computer vision
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    netcat-openbsd \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Create a non-root user for security
RUN addgroup --system appuser && adduser --system --group appuser

# Copy the rest of the application's code to the working directory
COPY --chown=appuser:appuser ./app/ ./app

# Switch to non-root user
USER appuser

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Define the command to run the Celery worker.
# Concurrency is configurable via the CELERY_CONCURRENCY env var, with a default of 4.
CMD ["sh", "-c", "celery -A app.workers.celery_app:celery_app worker --loglevel=info --concurrency=${CELERY_CONCURRENCY:-4}"]

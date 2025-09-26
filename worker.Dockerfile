# ---- Builder Stage ----
# This stage installs dependencies and builds wheels.
FROM python:3.11-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry==1.8.2

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

# Verify poppler installation and set PATH
RUN ls -la /usr/bin/pdfinfo /usr/bin/pdftoppm /usr/bin/pdftocairo && \
    /usr/bin/pdfinfo --version && \
    /usr/bin/pdftoppm -h && \
    /usr/bin/pdftocairo -h
ENV POPPLER_PATH=/usr/bin
ENV PATH="/usr/bin:${PATH}"

# Set the working directory in the container
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy the rest of the application's code to the working directory
COPY --chown=app:app ./app/ .

# Google Cloud authentication is handled via Workload Identity
# No credentials file needed - the service account attached to Cloud Run
# will automatically authenticate with Google Cloud services

# Switch to non-root user
USER app

# Define the command to run the Celery worker.
# Concurrency is configurable via the CELERY_CONCURRENCY env var, with a default of 4.
CMD ["sh", "-c", "celery -A app.workers.celery_app:celery_app worker --loglevel=info --concurrency=${CELERY_CONCURRENCY:-4}"]

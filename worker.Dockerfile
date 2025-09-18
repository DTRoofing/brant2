# ---- Builder Stage ----
# This stage installs dependencies and builds wheels.
FROM python:3.11-slim as builder

WORKDIR /app

# Install build tools that are only needed for this stage
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Build wheels for all dependencies, which is faster than installing directly
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ---- Final Stage ----
# This is the final, minimal image that will be deployed.
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for PDF processing and computer vision
RUN apt-get update && apt-get install -y \
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

# Copy the pre-built wheels from the builder stage
COPY --from=builder /app/wheels /wheels

# Install Python dependencies from the wheels
RUN pip install --no-cache-dir /wheels/*

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

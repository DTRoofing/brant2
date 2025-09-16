# Use an official Python runtime as a parent image
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
    libglib2.0-0 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt ./

# Install Python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the rest of the application's code to the working directory
COPY ./app/ ./app

# Create directories for uploads and logs
RUN mkdir -p /app/uploads /app/logs

# Copy Google credentials with secure permissions
COPY --chown=appuser:appuser --chmod=600 ./google-credentials.json ./google-credentials.json

# Change ownership of application directories to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Define the command to run the Celery worker.
CMD ["celery", "-A", "app.workers.celery_app:celery_app", "worker", "--loglevel=info", "--concurrency=4"]

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry first, so it's available for subsequent steps
RUN pip install poetry==1.6.1

# Configure Poetry to create the virtualenv inside the project directory
# This must be set before poetry is used.
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUAL_ENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies using Poetry
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# Copy the rest of the application's code to the working directory
COPY ./app/ ./app

# Create directories for uploads and logs
RUN mkdir -p /app/uploads /app/logs

# Define the command to run the Celery worker.
# Use poetry run to execute the command in the virtual environment.
CMD ["poetry", "run", "celery", "-A", "app.workers.celery_app:celery_app", "worker", "--loglevel=info", "--concurrency=4"]

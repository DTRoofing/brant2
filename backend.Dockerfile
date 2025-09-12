# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for PDF processing and health checks
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.6.1

# Configure Poetry to create the virtualenv inside the project directory
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUAL_ENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY pyproject.toml poetry.lock* ./

# Install any needed packages specified in requirements.txt
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# Copy the rest of the application's code to the working directory
COPY ./app/ ./app

# Create directories for uploads and logs
RUN mkdir -p /app/uploads /app/logs

# Make port 3001 available to the world outside this container
EXPOSE 3001

# Define the command to run the application
# Use poetry run to execute the command in the virtual environment.
# Note: The app path is now app.main:app because of the corrected COPY command.
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001", "--reload"]
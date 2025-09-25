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

# Install system dependencies for PDF processing and health checks
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify poppler installation and set PATH
RUN ls -la /usr/bin/pdfinfo /usr/bin/pdftoppm /usr/bin/pdftocairo && \
    /usr/bin/pdfinfo --version && \
    /usr/bin/pdftoppm -h && \
    /usr/bin/pdftocairo -h
ENV POPPLER_PATH=/usr/bin
ENV PATH="/usr/bin:${PATH}"

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code
# This comes after pip install to leverage caching
COPY --chown=app:app ./app .

# Copy Google Cloud credentials if they exist in the build context.
# This is primarily for local development. In GCP, use Workload Identity.
COPY --chown=app:app ./google-credentials.json /app/google-credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json

# Switch to the non-root user
USER app

# Expose the port the application runs on
# This should match the default port used in the CMD instruction for clarity.
EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:3001/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3001}"]
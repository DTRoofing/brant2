# ---- Builder Stage ----
# This stage installs dependencies and builds wheels.
FROM python:3.11-slim as builder

WORKDIR /app

# Install build tools that are only needed for this stage
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Build wheels for all dependencies, which is faster than installing directly
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ---- Final Stage ----
# This is the final, minimal image that will be deployed.
FROM python:3.11-slim

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Copy the pre-built wheels from the builder stage
COPY --from=builder /app/wheels /wheels

# Install the dependencies from the wheels
RUN pip install --no-cache /wheels/*

# Copy the application code
# This comes after pip install to leverage caching
COPY --chown=app:app ./app ./app

# Switch to the non-root user
USER app

# Expose the port the application runs on
# Cloud Run provides the PORT environment variable. Default to 8080 for local use.
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:3001/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3001}"]
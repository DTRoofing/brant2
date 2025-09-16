#!/bin/bash
set -e

echo "Starting BRANT container initialization..."

# Create necessary directories
mkdir -p /app/uploads /app/logs

# Set proper permissions
chmod 755 /app/uploads /app/logs

# Check for Google credentials
if [ -f "/app/google-credentials.json" ]; then
    echo "Google credentials found at /app/google-credentials.json"
    export GOOGLE_APPLICATION_CREDENTIALS="/app/google-credentials.json"
else
    echo "Warning: Google credentials not found at /app/google-credentials.json"
fi

# Verify Poppler installation
if command -v pdftoppm &> /dev/null; then
    echo "Poppler (pdftoppm) is installed: $(which pdftoppm)"
else
    echo "Warning: Poppler not found in PATH"
fi

# Verify Tesseract installation
if command -v tesseract &> /dev/null; then
    echo "Tesseract is installed: $(tesseract --version 2>&1 | head -n 1)"
else
    echo "Warning: Tesseract not found in PATH"
fi

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "Redis is ready!"

# Execute the main command
echo "Starting application..."
exec "$@"
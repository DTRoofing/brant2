#!/bin/bash
set -e

echo "🚀 Brant Roofing System - Quick Start Setup"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
    exit 1
fi

# Find the service account key
KEY_FILE=$(find secrets -name '*.json' -print -quit)

# Check if service account key exists
if [ -z "$KEY_FILE" ]; then
    echo "❌ Google service account key (.json file) not found in the 'secrets' directory."
    echo "   Please place your service account key there."
    exit 1
fi
echo "🔑 Found service account key: $KEY_FILE"

# Google Cloud authentication is handled via Workload Identity
# No credentials file needed - Workload Identity handles authentication
echo "🔐 Using Workload Identity for Google Cloud authentication"

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose --profile local up --build -d

echo "✅ Setup complete!"
echo ""
echo "🌐 Access your application:"
echo "   - API: http://localhost:3001"
echo "   - API Docs: http://localhost:3001/docs"
echo "   - Health Check: http://localhost:3001/api/v1/health"
echo ""
echo "📊 Check status with: make status"
echo "📜 View logs with: make logs"

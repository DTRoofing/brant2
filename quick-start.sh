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

# Check if service account key exists
if [ ! -f "secrets/brant-roofing-system-2025-a5b8920b36d5.json" ]; then
    echo "❌ Google service account key not found."
    echo "   Please place your service account key at:"
    echo "   secrets/brant-roofing-system-2025-a5b8920b36d5.json"
    exit 1
fi

# Create google-credentials.json symlink for Docker compatibility
if [ ! -f "google-credentials.json" ]; then
    echo "🔗 Creating google-credentials.json symlink..."
    ln -s "secrets/brant-roofing-system-2025-a5b8920b36d5.json" "google-credentials.json"
fi

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

echo "✅ Setup complete!"
echo ""
echo "🌐 Access your application:"
echo "   - API: http://localhost:3001"
echo "   - API Docs: http://localhost:3001/docs"
echo "   - Health Check: http://localhost:3001/api/v1/health"
echo ""
echo "📊 Check status with: make status"
echo "📜 View logs with: make logs"

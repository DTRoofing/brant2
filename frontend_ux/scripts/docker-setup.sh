#!/bin/bash

set -e

echo "🚀 Setting up DT Commercial Roofing Docker Environment"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p credentials
mkdir -p backups
mkdir -p nginx/ssl
mkdir -p database/init-scripts

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run Prisma migrations
echo "🗄️  Running database migrations..."
docker-compose exec app npx prisma migrate deploy

# Generate Prisma client
echo "🔧 Generating Prisma client..."
docker-compose exec app npx prisma generate

echo "✅ Setup complete!"
echo "🌐 Application is running at http://localhost:3000"
echo "🗄️  Database is running at localhost:5432"
echo "📊 Use 'docker-compose logs -f' to view logs"
echo "🛑 Use 'docker-compose down' to stop all services"

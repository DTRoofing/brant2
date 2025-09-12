#!/bin/bash

set -e

echo "🛠️  Setting up DT Commercial Roofing Development Environment"

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create development directories
echo "📁 Creating development directories..."
mkdir -p credentials
mkdir -p backups
mkdir -p database/dev-init-scripts
mkdir -p logs

# Setup environment files
if [ ! -f .env ]; then
    echo "📋 Creating development .env file..."
    cp .env.development .env
    echo "✅ Development environment file created"
else
    echo "⚠️  .env file already exists, skipping creation"
fi

# Create development credentials file (mock)
if [ ! -f credentials/google-credentials.json ]; then
    echo "🔑 Creating mock Google credentials for development..."
    cat > credentials/google-credentials.json << 'EOF'
{
  "type": "service_account",
  "project_id": "dev-project",
  "private_key_id": "dev-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nDEV_MOCK_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "dev@dev-project.iam.gserviceaccount.com",
  "client_id": "dev-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
EOF
    echo "✅ Mock credentials created for development"
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build development images
echo "🔨 Building development Docker images..."
docker-compose build

# Start development services
echo "🚀 Starting development services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Run database migrations
echo "🗄️  Running Prisma migrations..."
docker-compose exec app npx prisma migrate dev --name init

# Generate Prisma client
echo "🔧 Generating Prisma client..."
docker-compose exec app npx prisma generate

# Seed development data
echo "🌱 Seeding development data..."
docker-compose exec app npx prisma db seed || echo "⚠️  Seeding failed or no seed script found"

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🌐 Application: http://localhost:3000"
echo "🗄️  Database: localhost:5433 (postgres/postgres)"
echo "📧 Mailhog (Email testing): http://localhost:8025"
echo "🔧 Adminer (DB admin): http://localhost:8080"
echo ""
echo "📊 Useful commands:"
echo "  docker-compose logs -f app     # View app logs"
echo "  docker-compose logs -f database # View database logs"
echo "  docker-compose exec app sh     # Access app container"
echo "  docker-compose down            # Stop all services"
echo ""
echo "🔧 Development tools (optional):"
echo "  docker-compose --profile dev-tools up -d  # Start dev tools"

#!/bin/bash

set -e

echo "🚀 Deploying DT Commercial Roofing to Production"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root"
    exit 1
fi

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Check if production environment file exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found"
    echo "Please create .env.production with your production configuration"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/private.key ]; then
    echo "❌ SSL certificates not found"
    echo "Please place your SSL certificates in nginx/ssl/"
    exit 1
fi

# Create production directories
echo "📁 Creating production directories..."
mkdir -p backups
mkdir -p logs
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Backup existing data if any
if docker volume ls | grep -q postgres_prod_data; then
    echo "💾 Creating backup of existing data..."
    docker-compose -f docker-compose.prod.yml exec database pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backups/pre-deploy-$(date +%Y%m%d_%H%M%S).sql
fi

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Build application
echo "🔨 Building application..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

# Start services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec app npx prisma migrate deploy

# Health check
echo "🏥 Performing health checks..."
for i in {1..10}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Application is healthy"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Health check failed"
        docker-compose -f docker-compose.prod.yml logs app
        exit 1
    fi
    echo "⏳ Waiting for application to be ready... ($i/10)"
    sleep 10
done

echo ""
echo "✅ Production deployment complete!"
echo ""
echo "🌐 Application: https://yourdomain.com"
echo "📊 Monitoring: https://yourdomain.com:3001 (if enabled)"
echo ""
echo "📊 Useful commands:"
echo "  docker-compose -f docker-compose.prod.yml logs -f    # View logs"
echo "  docker-compose -f docker-compose.prod.yml ps         # Check status"
echo "  docker-compose -f docker-compose.prod.yml down       # Stop services"

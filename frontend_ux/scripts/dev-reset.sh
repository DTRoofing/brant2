#!/bin/bash

set -e

echo "🔄 Resetting development environment..."

# Stop all services
echo "🛑 Stopping all services..."
docker-compose down --volumes --remove-orphans

# Remove development volumes
echo "🗑️  Removing development volumes..."
docker volume rm roofing-dashboard_postgres_dev_data 2>/dev/null || true
docker volume rm roofing-dashboard_redis_data 2>/dev/null || true

# Clean up containers and images
echo "🧹 Cleaning up containers and images..."
docker system prune -f

# Rebuild and restart
echo "🔨 Rebuilding and restarting..."
./scripts/dev-setup.sh

echo "✅ Development environment reset complete!"

#!/bin/bash

# Restart and Test Development Server Script
# This script stops, rebuilds, and tests the development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔄 Restarting and Testing Development Server"
echo "============================================"

# Step 1: Stop any running containers
print_status "Stopping any running containers..."
if docker compose --profile local down 2>/dev/null; then
    print_success "Containers stopped successfully"
else
    print_warning "Some containers may not have been running"
fi

# Step 2: Clean up any orphaned containers
print_status "Cleaning up orphaned containers..."
if docker compose --profile local down --remove-orphans 2>/dev/null; then
    print_success "Cleanup completed"
else
    print_warning "No orphaned containers to clean up"
fi

# Step 3: Rebuild and start services
print_status "Rebuilding and starting services..."
if docker compose --profile local up --build -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 4: Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Step 5: Test the build and services
print_status "Testing services..."

# Check if containers are running
print_status "Checking container status..."
docker compose --profile local ps

# Test API health
print_status "Testing API health..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f http://localhost:${API_HOST_PORT:-3001}/api/v1/health >/dev/null 2>&1; then
        print_success "API is healthy at http://localhost:${API_HOST_PORT:-3001}"
        break
    fi
    
    attempt=$((attempt + 1))
    print_status "Waiting for API... (attempt $attempt/$max_attempts)"
    sleep 3
done

if [ $attempt -eq $max_attempts ]; then
    print_warning "API health check failed after $max_attempts attempts"
fi

# Test frontend
print_status "Testing frontend..."
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f http://localhost:${FRONTEND_HOST_PORT:-3000} >/dev/null 2>&1; then
        print_success "Frontend is accessible at http://localhost:${FRONTEND_HOST_PORT:-3000}"
        break
    fi
    
    attempt=$((attempt + 1))
    print_status "Waiting for frontend... (attempt $attempt/$max_attempts)"
    sleep 3
done

if [ $attempt -eq $max_attempts ]; then
    print_warning "Frontend health check failed after $max_attempts attempts"
fi

# Test Next.js build inside the frontend container
print_status "Testing Next.js build in frontend container..."
if docker compose --profile local exec frontend-local npm run build; then
    print_success "Next.js build completed successfully"
else
    print_error "Next.js build failed"
    print_status "Showing build logs..."
    docker compose --profile local logs frontend-local --tail=20
fi

# Show recent logs
print_status "Showing recent logs..."
docker compose --profile local logs --tail=10

echo ""
echo "✅ Development server restart and test completed!"
echo ""
echo "Services available at:"
echo "  - Frontend: http://localhost:${FRONTEND_HOST_PORT:-3000}"
echo "  - API: http://localhost:${API_HOST_PORT:-3001}"
echo "  - API Docs: http://localhost:${API_HOST_PORT:-3001}/docs"
echo "  - Celery Monitor: http://localhost:${FLOWER_HOST_PORT:-5555}"
echo ""
echo "To view logs: docker compose --profile local logs -f"
echo "To stop services: docker compose --profile local down"

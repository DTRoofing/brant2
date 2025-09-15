#!/bin/bash

echo "=========================================="
echo "BRANT DEPLOYMENT TEST"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR] Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Check for required files
echo ""
echo "Checking required files..."
required_files=(
    ".env"
    "google-credentials.json"
    "docker-compose.yml"
    "backend.Dockerfile"
    "worker.Dockerfile"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file is missing${NC}"
        exit 1
    fi
done

# Build containers
echo ""
echo "Building containers..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Container build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Containers built successfully${NC}"

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to start services${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Services started${NC}"

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check API
if curl -f http://localhost:3001/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
fi

# Check database
if docker-compose exec -T db pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is ready${NC}"
else
    echo -e "${RED}✗ Database is not ready${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is ready${NC}"
else
    echo -e "${RED}✗ Redis is not ready${NC}"
fi

# Check worker
if docker-compose ps worker | grep -q "Up"; then
    echo -e "${GREEN}✓ Worker is running${NC}"
else
    echo -e "${RED}✗ Worker is not running${NC}"
fi

# Run health check in container
echo ""
echo "Running container health check..."
docker-compose exec -T api python /app/scripts/container_healthcheck.py

# Show logs
echo ""
echo "Recent API logs:"
docker-compose logs --tail=20 api

echo ""
echo "Recent Worker logs:"
docker-compose logs --tail=20 worker

echo ""
echo "=========================================="
echo "DEPLOYMENT TEST COMPLETE"
echo "=========================================="
echo ""
echo "Services are running at:"
echo "  - API: http://localhost:3001"
echo "  - Flower (Celery monitor): http://localhost:5555"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f [service_name]"
echo "To run tests: docker-compose exec api pytest"
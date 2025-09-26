#!/bin/bash

# Test script to verify Docker Compose fix
# This script tests the Docker Compose configuration and services

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

# Check if Docker is available
check_docker() {
    print_status "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not available in PATH"
        print_status "Please ensure Docker Desktop is running and accessible"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        print_status "Please start Docker Desktop"
        return 1
    fi
    
    print_success "Docker is available and running"
    return 0
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose availability..."
    
    if docker compose version &> /dev/null; then
        print_success "Docker Compose (v2) is available"
        COMPOSE_CMD="docker compose"
    elif docker-compose --version &> /dev/null; then
        print_success "Docker Compose (v1) is available"
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose is not available"
        return 1
    fi
    
    return 0
}

# Verify configuration files
verify_config() {
    print_status "Verifying configuration files..."
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        return 1
    fi
    
    # Check if frontend Dockerfile exists
    if [ ! -f "frontend_ux/Dockerfile" ]; then
        print_error "frontend_ux/Dockerfile not found"
        return 1
    fi
    
    # Check if backend Dockerfile exists
    if [ ! -f "backend.Dockerfile" ]; then
        print_error "backend.Dockerfile not found"
        return 1
    fi
    
    # Check if worker Dockerfile exists
    if [ ! -f "worker.Dockerfile" ]; then
        print_error "worker.Dockerfile not found"
        return 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found - services may not start properly"
    fi
    
    print_success "All configuration files are present"
    return 0
}

# Test Docker Compose configuration
test_compose_config() {
    print_status "Testing Docker Compose configuration..."
    
    if $COMPOSE_CMD config &> /dev/null; then
        print_success "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration has errors"
        $COMPOSE_CMD config
        return 1
    fi
    
    return 0
}

# Build services
build_services() {
    print_status "Building services..."
    
    if $COMPOSE_CMD --profile local build; then
        print_success "All services built successfully"
    else
        print_error "Service build failed"
        return 1
    fi
    
    return 0
}

# Start services
start_services() {
    print_status "Starting services..."
    
    if $COMPOSE_CMD --profile local up -d; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        return 1
    fi
    
    return 0
}

# Check service status
check_services() {
    print_status "Checking service status..."
    
    # Wait a moment for services to start
    sleep 10
    
    # Check if containers are running
    local running_containers=$($COMPOSE_CMD --profile local ps --format "table {{.Name}}\t{{.Status}}" | grep -c "Up" || echo "0")
    
    if [ "$running_containers" -ge 3 ]; then
        print_success "All services are running ($running_containers containers)"
    else
        print_warning "Some services may not be running properly"
        $COMPOSE_CMD --profile local ps
    fi
    
    return 0
}

# Test API endpoint
test_api() {
    print_status "Testing API endpoint..."
    
    # Wait for API to be ready
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f http://localhost:${API_HOST_PORT:-3001}/api/v1/health &> /dev/null; then
            print_success "API is responding at http://localhost:${API_HOST_PORT:-3001}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        print_status "Waiting for API... (attempt $attempt/$max_attempts)"
        sleep 2
    done
    
    print_warning "API health check failed - service may still be starting"
    return 1
}

# Test frontend
test_frontend() {
    print_status "Testing frontend..."
    
    # Wait for frontend to be ready
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f http://localhost:${FRONTEND_HOST_PORT:-3000} &> /dev/null; then
            print_success "Frontend is responding at http://localhost:${FRONTEND_HOST_PORT:-3000}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        print_status "Waiting for frontend... (attempt $attempt/$max_attempts)"
        sleep 2
    done
    
    print_warning "Frontend health check failed - service may still be starting"
    return 1
}

# Show service logs
show_logs() {
    print_status "Showing recent logs..."
    $COMPOSE_CMD --profile local logs --tail=20
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    $COMPOSE_CMD --profile local down
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "🧪 Testing Docker Compose Fix for Brant Roofing System"
    echo "======================================================"
    
    # Check prerequisites
    if ! check_docker; then
        print_error "Docker is not available. Please start Docker Desktop and try again."
        exit 1
    fi
    
    if ! check_docker_compose; then
        print_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
    
    # Verify configuration
    if ! verify_config; then
        print_error "Configuration verification failed"
        exit 1
    fi
    
    # Test configuration
    if ! test_compose_config; then
        print_error "Docker Compose configuration test failed"
        exit 1
    fi
    
    # Build services
    if ! build_services; then
        print_error "Service build failed"
        exit 1
    fi
    
    # Start services
    if ! start_services; then
        print_error "Service startup failed"
        exit 1
    fi
    
    # Check services
    check_services
    
    # Test endpoints
    test_api
    test_frontend
    
    # Show logs
    show_logs
    
    echo ""
    echo "✅ Docker Compose fix verification completed!"
    echo ""
    echo "Services should be available at:"
    echo "  - API: http://localhost:${API_HOST_PORT:-3001}"
    echo "  - Frontend: http://localhost:${FRONTEND_HOST_PORT:-3000}"
    echo "  - API Docs: http://localhost:${API_HOST_PORT:-3001}/docs"
    echo ""
    echo "To stop services: docker compose --profile local down"
    echo "To view logs: docker compose --profile local logs -f"
}

# Run main function
main "$@"

#!/bin/bash
# Quick setup script for Google Cloud Memorystore migration

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

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    print_success "gcloud CLI is installed"
}

# Check if user is authenticated
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi
    print_success "gcloud authentication is active"
}

# Get project ID
get_project_id() {
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No project ID set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
        exit 1
    fi
    print_success "Using project: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."
    
    gcloud services enable redis.googleapis.com --project=$PROJECT_ID
    gcloud services enable servicenetworking.googleapis.com --project=$PROJECT_ID
    
    print_success "APIs enabled successfully"
}

# Create Memorystore instance
create_memorystore() {
    print_status "Creating Memorystore Redis instance..."
    
    # Check if instance already exists
    if gcloud redis instances describe brant-redis-instance --region=us-central1 --project=$PROJECT_ID &>/dev/null; then
        print_warning "Memorystore instance 'brant-redis-instance' already exists"
        return 0
    fi
    
    # Create the instance
    gcloud redis instances create brant-redis-instance \
        --size=1 \
        --region=us-central1 \
        --redis-version=redis_7_0 \
        --tier=basic \
        --network=projects/$PROJECT_ID/global/networks/default \
        --project=$PROJECT_ID
    
    print_success "Memorystore instance created successfully"
}

# Get instance details
get_instance_info() {
    print_status "Getting instance information..."
    
    INSTANCE_INFO=$(gcloud redis instances describe brant-redis-instance --region=us-central1 --project=$PROJECT_ID --format="value(host,port,memorySizeGb,redisVersion)")
    
    if [ -z "$INSTANCE_INFO" ]; then
        print_error "Failed to get instance information"
        exit 1
    fi
    
    HOST=$(echo $INSTANCE_INFO | cut -d' ' -f1)
    PORT=$(echo $INSTANCE_INFO | cut -d' ' -f2)
    MEMORY=$(echo $INSTANCE_INFO | cut -d' ' -f3)
    VERSION=$(echo $INSTANCE_INFO | cut -d' ' -f4)
    
    print_success "Instance details:"
    echo "  Host: $HOST"
    echo "  Port: $PORT"
    echo "  Memory: ${MEMORY}GB"
    echo "  Version: $VERSION"
}

# Create environment file
create_env_file() {
    print_status "Creating .env.memorystore file..."
    
    cat > .env.memorystore << EOF
# Google Cloud Memorystore Configuration
USE_MEMORYSTORE=true
MEMORYSTORE_REGION=us-central1
MEMORYSTORE_INSTANCE_NAME=brant-redis-instance
GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID

# Redis URLs (auto-configured)
REDIS_URL=redis://$HOST:$PORT/2
CELERY_BROKER_URL=redis://$HOST:$PORT/0
CELERY_RESULT_BACKEND=redis://$HOST:$PORT/1

# Other required variables (update these with your values)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
DATABASE_URL=postgresql+asyncpg://user:password@YOUR_CLOUD_SQL_IP:5432/brant_roofing
ANTHROPIC_API_KEY=your-anthropic-api-key
SECRET_KEY=your-secret-key
EOF
    
    print_success "Environment file created: .env.memorystore"
    print_warning "Please update the placeholder values in .env.memorystore with your actual configuration"
}

# Test connection
test_connection() {
    print_status "Testing Memorystore connection..."
    
    if python scripts/migrate_to_memorystore.py --test-only; then
        print_success "Memorystore connection test passed"
    else
        print_warning "Memorystore connection test failed. This is expected if you haven't set up authentication yet."
    fi
}

# Main function
main() {
    echo "🚀 Setting up Google Cloud Memorystore for Brant Roofing System"
    echo "=================================================================="
    
    check_gcloud
    check_auth
    get_project_id
    enable_apis
    create_memorystore
    get_instance_info
    create_env_file
    test_connection
    
    echo ""
    echo "🎉 Memorystore setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Update .env.memorystore with your actual configuration values"
    echo "2. Copy .env.memorystore to .env if you want to use Memorystore locally"
    echo "3. Deploy your application with the new configuration"
    echo ""
    echo "For more information, see: docs/MEMORYSTORE_MIGRATION_GUIDE.md"
}

# Run main function
main "$@"

#!/bin/bash

# Cloud Build Monitoring Script
# This script monitors the latest Cloud Build and shows real-time status

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

echo "🔍 Monitoring Cloud Build..."
echo "=========================="

# Check if gcloud is available
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not available. Please install it first."
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "No active gcloud authentication found. Please run 'gcloud auth login' first."
    exit 1
fi

# Get latest build ID
print_status "Getting latest build information..."
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")

if [ -z "$BUILD_ID" ]; then
    print_warning "No builds found. The build may not have started yet."
    exit 0
fi

echo "Latest Build ID: $BUILD_ID"

# Get build status
STATUS=$(gcloud builds describe $BUILD_ID --format="value(status)")
echo "Status: $STATUS"

# Get build details
BUILD_TIME=$(gcloud builds describe $BUILD_ID --format="value(createTime)")
DURATION=$(gcloud builds describe $BUILD_ID --format="value(duration)")

echo "Created: $BUILD_TIME"
echo "Duration: $DURATION"

# Handle different statuses
case $STATUS in
    "WORKING")
        print_status "Build is currently running..."
        echo ""
        print_status "Streaming live logs (Press Ctrl+C to stop):"
        echo "=============================================="
        gcloud builds log --stream $BUILD_ID
        ;;
    "SUCCESS")
        print_success "Build completed successfully!"
        echo ""
        print_status "Build Summary:"
        echo "- Build ID: $BUILD_ID"
        echo "- Status: $STATUS"
        echo "- Duration: $DURATION"
        echo ""
        print_status "Services should be deployed to Cloud Run"
        print_status "Check your Cloud Run services in the Google Cloud Console"
        ;;
    "FAILURE")
        print_error "Build failed!"
        echo ""
        print_status "Build Summary:"
        echo "- Build ID: $BUILD_ID"
        echo "- Status: $STATUS"
        echo "- Duration: $DURATION"
        echo ""
        print_status "Recent logs:"
        echo "============="
        gcloud builds log $BUILD_ID --tail=50
        ;;
    "TIMEOUT")
        print_warning "Build timed out!"
        echo ""
        print_status "Build Summary:"
        echo "- Build ID: $BUILD_ID"
        echo "- Status: $STATUS"
        echo "- Duration: $DURATION"
        ;;
    "CANCELLED")
        print_warning "Build was cancelled!"
        echo ""
        print_status "Build Summary:"
        echo "- Build ID: $BUILD_ID"
        echo "- Status: $STATUS"
        echo "- Duration: $DURATION"
        ;;
    *)
        print_status "Build status: $STATUS"
        ;;
esac

echo ""
print_status "To view detailed build information:"
echo "gcloud builds describe $BUILD_ID"

print_status "To view all recent builds:"
echo "gcloud builds list --limit=5"

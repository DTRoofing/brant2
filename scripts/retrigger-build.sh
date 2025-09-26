#!/bin/bash

# Retrigger Cloud Build Script
# This script creates an empty commit to retrigger the Cloud Build

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

echo "🔄 Retriggering Cloud Build..."
echo "=============================="

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "Git is not available. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git status &> /dev/null; then
    print_error "Not in a git repository. Please navigate to the project directory."
    exit 1
fi

# Create empty commit to retrigger build
print_status "Creating empty commit to retrigger Cloud Build..."
if ! git commit --allow-empty -m "retrigger: Force Cloud Build to run again"; then
    print_error "Failed to create empty commit"
    exit 1
fi

# Push to trigger the build
print_status "Pushing to trigger Cloud Build..."
if ! git push origin main; then
    print_error "Failed to push to remote repository"
    exit 1
fi

print_success "Cloud Build retriggered successfully!"
echo ""
print_status "Build should start shortly. Monitor with:"
echo "  gcloud builds list --limit=1"
echo "  gcloud builds log --stream \$(gcloud builds list --limit=1 --format=\"value(id)\")"
echo ""
print_status "Or use the monitoring script:"
echo "  ./monitor-build.sh"

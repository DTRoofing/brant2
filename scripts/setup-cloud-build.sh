#!/bin/bash

# Cloud Build Setup Script for Brant Roofing System
# This script automates the initial setup of Cloud Build

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

# Check if gcloud is installed and authenticated
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active gcloud authentication found. Please run 'gcloud auth login' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Get project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        print_status "Getting current GCP project..."
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        
        if [ -z "$PROJECT_ID" ]; then
            print_error "No GCP project set. Please set it with: gcloud config set project YOUR_PROJECT_ID"
            exit 1
        fi
        
        print_success "Using project: $PROJECT_ID"
    else
        print_success "Using provided project: $PROJECT_ID"
    fi
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required GCP APIs..."
    
    local apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "artifactregistry.googleapis.com"
        "secretmanager.googleapis.com"
        "sqladmin.googleapis.com"
        "documentai.googleapis.com"
        "vpcaccess.googleapis.com"
        "redis.googleapis.com"
        "compute.googleapis.com"
        "vision.googleapis.com"
        "certificatemanager.googleapis.com"
        "servicenetworking.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" || print_warning "Failed to enable $api"
    done
    
    print_success "APIs enabled"
}

# Create Artifact Registry repository
create_artifact_registry() {
    print_status "Creating Artifact Registry repository..."
    
    gcloud artifacts repositories create brant-repo \
        --repository-format=docker \
        --location=us-central1 \
        --description="Brant Roofing System Docker Repository" \
        --project="$PROJECT_ID" || print_warning "Repository might already exist"
    
    print_success "Artifact Registry repository created"
}

# Configure Docker authentication
configure_docker_auth() {
    print_status "Configuring Docker authentication..."
    
    gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
    
    print_success "Docker authentication configured"
}

# Create Cloud Build service account
create_cloudbuild_sa() {
    print_status "Creating Cloud Build service account..."
    
    gcloud iam service-accounts create brant-cloudbuild \
        --display-name="Brant Cloud Build Service Account" \
        --project="$PROJECT_ID" || print_warning "Service account might already exist"
    
    print_success "Cloud Build service account created"
}

# Grant permissions to Cloud Build service account
grant_permissions() {
    print_status "Granting permissions to Cloud Build service account..."
    
    local sa_email="brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com"
    
    local roles=(
        "roles/cloudbuild.builds.builder"
        "roles/run.admin"
        "roles/artifactregistry.writer"
        "roles/secretmanager.secretAccessor"
        "roles/iam.serviceAccountUser"
    )
    
    for role in "${roles[@]}"; do
        print_status "Granting $role..."
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$sa_email" \
            --role="$role" || print_warning "Failed to grant $role"
    done
    
    print_success "Permissions granted"
}

# Create Cloud Build trigger
create_trigger() {
    print_status "Creating Cloud Build trigger..."
    
    local sa_email="brant-cloudbuild@$PROJECT_ID.iam.gserviceaccount.com"
    
    gcloud builds triggers create github \
        --repo-name=brant2 \
        --repo-owner=DTRoofing \
        --branch-pattern="^main$" \
        --build-config=cloudbuild.yaml \
        --service-account="$sa_email" \
        --project="$PROJECT_ID" || print_warning "Trigger might already exist"
    
    print_success "Cloud Build trigger created"
}

# Main execution
main() {
    echo "🚀 Starting Cloud Build setup for Brant Roofing System"
    echo "=================================================="
    
    check_prerequisites
    get_project_id
    enable_apis
    create_artifact_registry
    configure_docker_auth
    create_cloudbuild_sa
    grant_permissions
    create_trigger
    
    echo ""
    echo "✅ Cloud Build setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Deploy infrastructure: cd deployment && terraform apply"
    echo "2. Configure secrets in Google Secret Manager"
    echo "3. Update substitution variables in the Cloud Build trigger"
    echo "4. Test by pushing to main branch"
    echo ""
    echo "For detailed instructions, see: CLOUD_BUILD_SETUP_PLAN.md"
}

# Run main function
main "$@"

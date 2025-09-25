#!/bin/bash
# Fix Artifact Registry permissions for Cloud Build

set -e

# Configuration
PROJECT_ID="brant-roofing-system-2025"
REGION="us-central1"
REPO_NAME="brant-repo"
SERVICE_ACCOUNT="brant-cloudbuild@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔧 Fixing Artifact Registry permissions for Cloud Build"
echo "======================================================"
echo "Project ID: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT"
echo ""

# Function to print status
print_status() {
    echo "📋 $1"
}

print_success() {
    echo "✅ $1"
}

print_warning() {
    echo "⚠️  $1"
}

print_error() {
    echo "❌ $1"
}

# Check if gcloud is authenticated
check_auth() {
    print_status "Checking gcloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi
    print_success "gcloud authentication verified"
}

# Set the project
set_project() {
    print_status "Setting project to $PROJECT_ID..."
    gcloud config set project "$PROJECT_ID"
    print_success "Project set to $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."
    
    local apis=(
        "artifactregistry.googleapis.com"
        "cloudbuild.googleapis.com"
        "iam.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" || print_warning "Failed to enable $api"
    done
    
    print_success "APIs enabled"
}

# Create Artifact Registry repository if it doesn't exist
create_artifact_registry() {
    print_status "Creating Artifact Registry repository..."
    
    if gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
        print_success "Repository $REPO_NAME already exists"
    else
        gcloud artifacts repositories create "$REPO_NAME" \
            --repository-format=docker \
            --location="$REGION" \
            --description="Brant Roofing System Docker Repository" \
            --project="$PROJECT_ID"
        print_success "Repository $REPO_NAME created"
    fi
}

# Create Cloud Build service account if it doesn't exist
create_service_account() {
    print_status "Creating Cloud Build service account..."
    
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" >/dev/null 2>&1; then
        print_success "Service account $SERVICE_ACCOUNT already exists"
    else
        gcloud iam service-accounts create brant-cloudbuild \
            --display-name="Brant Cloud Build Service Account" \
            --project="$PROJECT_ID"
        print_success "Service account $SERVICE_ACCOUNT created"
    fi
}

# Grant required IAM roles
grant_iam_roles() {
    print_status "Granting IAM roles to Cloud Build service account..."
    
    # Essential roles for Cloud Build
    local roles=(
        "roles/cloudbuild.builds.builder"
        "roles/run.admin"
        "roles/artifactregistry.writer"
        "roles/artifactregistry.reader"
        "roles/secretmanager.secretAccessor"
        "roles/iam.serviceAccountUser"
        "roles/storage.admin"
        "roles/cloudsql.client"
    )
    
    for role in "${roles[@]}"; do
        print_status "Granting $role..."
        if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="$role" \
            --quiet; then
            print_success "Granted $role"
        else
            print_warning "Failed to grant $role (might already be granted)"
        fi
    done
}

# Grant Artifact Registry specific permissions
grant_artifact_registry_permissions() {
    print_status "Granting Artifact Registry specific permissions..."
    
    # Grant repository-level permissions
    local repo_permissions=(
        "artifactregistry.repositories.uploadArtifacts"
        "artifactregistry.repositories.downloadArtifacts"
        "artifactregistry.repositories.get"
        "artifactregistry.repositories.list"
    )
    
    for permission in "${repo_permissions[@]}"; do
        print_status "Granting $permission..."
        gcloud artifacts repositories add-iam-policy-binding "$REPO_NAME" \
            --location="$REGION" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/artifactregistry.writer" \
            --project="$PROJECT_ID" || print_warning "Failed to grant $permission"
    done
    
    print_success "Artifact Registry permissions granted"
}

# Configure Docker authentication
configure_docker_auth() {
    print_status "Configuring Docker authentication..."
    
    gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
    print_success "Docker authentication configured"
}

# Test permissions
test_permissions() {
    print_status "Testing Artifact Registry permissions..."
    
    # Test if the service account can access the repository
    if gcloud artifacts repositories get-iam-policy "$REPO_NAME" \
        --location="$REGION" \
        --project="$PROJECT_ID" >/dev/null 2>&1; then
        print_success "Repository access verified"
    else
        print_warning "Could not verify repository access"
    fi
}

# Update Cloud Build trigger with correct service account
update_cloud_build_trigger() {
    print_status "Checking Cloud Build trigger configuration..."
    
    # List existing triggers
    local triggers=$(gcloud builds triggers list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null || echo "")
    
    if [ -n "$triggers" ]; then
        print_status "Found existing Cloud Build triggers"
        for trigger in $triggers; do
            print_status "Updating trigger: $trigger"
            gcloud builds triggers update "$trigger" \
                --service-account="$SERVICE_ACCOUNT" \
                --project="$PROJECT_ID" || print_warning "Failed to update trigger $trigger"
        done
        print_success "Cloud Build triggers updated"
    else
        print_warning "No Cloud Build triggers found. You may need to create one manually."
    fi
}

# Main execution
main() {
    echo "🚀 Starting Artifact Registry permissions fix"
    echo "=============================================="
    
    check_auth
    set_project
    enable_apis
    create_artifact_registry
    create_service_account
    grant_iam_roles
    grant_artifact_registry_permissions
    configure_docker_auth
    test_permissions
    update_cloud_build_trigger
    
    echo ""
    echo "🎉 Artifact Registry permissions fix completed!"
    echo ""
    echo "Next steps:"
    echo "1. Verify the service account has the correct roles in the GCP Console"
    echo "2. Test a Cloud Build trigger to ensure it can push to Artifact Registry"
    echo "3. Check the Cloud Build logs for any remaining permission issues"
    echo ""
    echo "Service Account: $SERVICE_ACCOUNT"
    echo "Repository: $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"
}

# Run the main function
main "$@"

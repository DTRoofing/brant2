#!/bin/bash
# Verify Artifact Registry permissions for Cloud Build

set -e

# Configuration
PROJECT_ID="brant-roofing-system-2025"
REGION="us-central1"
REPO_NAME="brant-repo"
SERVICE_ACCOUNT="brant-cloudbuild@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔍 Verifying Artifact Registry permissions for Cloud Build"
echo "=========================================================="
echo "Project ID: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT"
echo "Repository: $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"
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

# Check project
check_project() {
    print_status "Checking current project..."
    local current_project=$(gcloud config get-value project)
    if [ "$current_project" = "$PROJECT_ID" ]; then
        print_success "Project is set to $PROJECT_ID"
    else
        print_warning "Project is set to $current_project, expected $PROJECT_ID"
        gcloud config set project "$PROJECT_ID"
        print_success "Project updated to $PROJECT_ID"
    fi
}

# Check if Artifact Registry repository exists
check_repository() {
    print_status "Checking Artifact Registry repository..."
    
    if gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
        print_success "Repository $REPO_NAME exists"
        
        # Get repository details
        local repo_info=$(gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" --format="value(name,format,location)")
        echo "   Repository info: $repo_info"
    else
        print_error "Repository $REPO_NAME does not exist"
        return 1
    fi
}

# Check if service account exists
check_service_account() {
    print_status "Checking Cloud Build service account..."
    
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" >/dev/null 2>&1; then
        print_success "Service account $SERVICE_ACCOUNT exists"
        
        # Get service account details
        local sa_info=$(gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" --format="value(displayName,email)")
        echo "   Service account info: $sa_info"
    else
        print_error "Service account $SERVICE_ACCOUNT does not exist"
        return 1
    fi
}

# Check IAM roles for the service account
check_iam_roles() {
    print_status "Checking IAM roles for service account..."
    
    local required_roles=(
        "roles/cloudbuild.builds.builder"
        "roles/run.admin"
        "roles/artifactregistry.writer"
        "roles/artifactregistry.reader"
        "roles/secretmanager.secretAccessor"
        "roles/iam.serviceAccountUser"
    )
    
    for role in "${required_roles[@]}"; do
        if gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="table(bindings.role)" \
            --filter="bindings.members:$SERVICE_ACCOUNT" | grep -q "$role"; then
            print_success "Has role: $role"
        else
            print_warning "Missing role: $role"
        fi
    done
}

# Check Artifact Registry specific permissions
check_artifact_registry_permissions() {
    print_status "Checking Artifact Registry specific permissions..."
    
    # Get repository IAM policy
    local repo_policy=$(gcloud artifacts repositories get-iam-policy "$REPO_NAME" \
        --location="$REGION" \
        --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -n "$repo_policy" ]; then
        print_success "Repository IAM policy accessible"
        
        # Check if service account has writer role
        if echo "$repo_policy" | grep -q "$SERVICE_ACCOUNT"; then
            print_success "Service account has repository-level permissions"
        else
            print_warning "Service account may not have repository-level permissions"
        fi
    else
        print_warning "Could not retrieve repository IAM policy"
    fi
}

# Check Cloud Build triggers
check_cloud_build_triggers() {
    print_status "Checking Cloud Build triggers..."
    
    local triggers=$(gcloud builds triggers list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null || echo "")
    
    if [ -n "$triggers" ]; then
        print_success "Found Cloud Build triggers"
        for trigger in $triggers; do
            echo "   Trigger: $trigger"
            
            # Check if trigger uses the correct service account
            local trigger_sa=$(gcloud builds triggers describe "$trigger" --project="$PROJECT_ID" --format="value(serviceAccount)" 2>/dev/null || echo "")
            if [ "$trigger_sa" = "$SERVICE_ACCOUNT" ]; then
                print_success "   Uses correct service account: $trigger_sa"
            else
                print_warning "   Uses different service account: $trigger_sa"
            fi
        done
    else
        print_warning "No Cloud Build triggers found"
    fi
}

# Test Docker authentication
test_docker_auth() {
    print_status "Testing Docker authentication..."
    
    if gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet 2>/dev/null; then
        print_success "Docker authentication configured"
    else
        print_warning "Docker authentication may need manual configuration"
    fi
}

# Check recent Cloud Build logs for permission errors
check_build_logs() {
    print_status "Checking recent Cloud Build logs for permission errors..."
    
    local recent_builds=$(gcloud builds list --limit=5 --project="$PROJECT_ID" --format="value(id,status)" 2>/dev/null || echo "")
    
    if [ -n "$recent_builds" ]; then
        print_success "Found recent builds"
        echo "$recent_builds" | while read -r build_id status; do
            echo "   Build $build_id: $status"
        done
    else
        print_warning "No recent builds found"
    fi
}

# Main execution
main() {
    echo "🔍 Starting Artifact Registry permissions verification"
    echo "======================================================"
    
    check_auth
    check_project
    
    echo ""
    echo "📋 Repository Check:"
    if check_repository; then
        print_success "Repository check passed"
    else
        print_error "Repository check failed"
        exit 1
    fi
    
    echo ""
    echo "📋 Service Account Check:"
    if check_service_account; then
        print_success "Service account check passed"
    else
        print_error "Service account check failed"
        exit 1
    fi
    
    echo ""
    echo "📋 IAM Roles Check:"
    check_iam_roles
    
    echo ""
    echo "📋 Artifact Registry Permissions Check:"
    check_artifact_registry_permissions
    
    echo ""
    echo "📋 Cloud Build Triggers Check:"
    check_cloud_build_triggers
    
    echo ""
    echo "📋 Docker Authentication Check:"
    test_docker_auth
    
    echo ""
    echo "📋 Recent Build Logs Check:"
    check_build_logs
    
    echo ""
    echo "🎯 Verification Summary:"
    echo "========================"
    echo "If you see any warnings or errors above, run the fix script:"
    echo "  ./fix-artifact-registry-permissions.sh"
    echo ""
    echo "To test the fix, trigger a Cloud Build and check the logs for:"
    echo "  - Successful image push to Artifact Registry"
    echo "  - No permission denied errors"
}

# Run the main function
main "$@"

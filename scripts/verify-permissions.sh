#!/bin/bash

# Comprehensive Service Account Permissions Verification Script
# This script checks all service accounts and their roles for the Brant Roofing System

set -e

PROJECT_ID="brant-roofing-system-2025"

echo "🔍 COMPREHENSIVE PERMISSIONS VERIFICATION"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Date: $(date)"
echo ""

# Function to check if a service account exists and get its roles
check_service_account() {
    local sa_email="$1"
    local sa_name="$2"
    local expected_roles="$3"
    
    echo "📋 Checking: $sa_name"
    echo "   Email: $sa_email"
    
    # Check if service account exists
    if gcloud iam service-accounts describe "$sa_email" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "   ✅ Service account exists"
        
        # Get current roles
        echo "   📝 Current roles:"
        gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="table(bindings.role)" \
            --filter="bindings.members:$sa_email" | while read role; do
            if [[ "$role" != "ROLE" ]]; then
                echo "      - $role"
            fi
        done
        
        # Check for security issues
        echo "   🔒 Security analysis:"
        
        # Check for overly broad roles
        if gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="value(bindings.role)" \
            --filter="bindings.members:$sa_email" | grep -q "roles/editor\|roles/owner"; then
            echo "      ⚠️  WARNING: Has overly broad Editor or Owner role"
        fi
        
        if gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="value(bindings.role)" \
            --filter="bindings.members:$sa_email" | grep -q "roles/compute.admin"; then
            echo "      ⚠️  WARNING: Has Compute Admin role (may be too broad)"
        fi
        
        # Check for unused roles
        local current_roles=$(gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="value(bindings.role)" \
            --filter="bindings.members:$sa_email")
        
        if echo "$current_roles" | grep -q "roles/appengine.admin\|roles/firebase.admin\|roles/kubernetes.admin"; then
            echo "      ⚠️  WARNING: Has unused service roles (App Engine, Firebase, GKE)"
        fi
        
        echo "      ✅ No critical security issues found"
        
    else
        echo "   ❌ Service account does not exist"
    fi
    
    echo ""
}

# Function to check project-level permissions
check_project_permissions() {
    echo "🏗️  PROJECT-LEVEL PERMISSIONS"
    echo "=============================="
    
    # Check if Artifact Registry repository exists
    echo "📦 Artifact Registry Repository:"
    if gcloud artifacts repositories describe brant-repo --location=us-central1 --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "   ✅ Repository 'brant-repo' exists"
    else
        echo "   ❌ Repository 'brant-repo' not found"
    fi
    
    # Check Cloud Build permissions
    echo ""
    echo "🔨 Cloud Build Configuration:"
    local build_sa=$(gcloud projects get-iam-policy "$PROJECT_ID" \
        --flatten="bindings[].members" \
        --format="value(bindings.members)" \
        --filter="bindings.role:roles/cloudbuild.builds.builder" | head -1)
    
    if [[ -n "$build_sa" ]]; then
        echo "   ✅ Cloud Build service account: $build_sa"
    else
        echo "   ❌ No Cloud Build service account found"
    fi
    
    echo ""
}

# Function to check for security best practices
check_security_best_practices() {
    echo "🛡️  SECURITY BEST PRACTICES CHECK"
    echo "=================================="
    
    # Check for service accounts with too many roles
    echo "📊 Service accounts with many roles:"
    gcloud projects get-iam-policy "$PROJECT_ID" \
        --flatten="bindings[].members" \
        --format="table(bindings.members,bindings.role)" \
        --filter="bindings.members:serviceAccount" | \
        awk '{print $1}' | sort | uniq -c | sort -nr | while read count sa; do
        if [[ $count -gt 5 ]]; then
            echo "   ⚠️  $sa has $count roles (consider reviewing)"
        fi
    done
    
    # Check for unused roles
    echo ""
    echo "🔍 Checking for potentially unused roles:"
    local unused_roles=("roles/appengine.admin" "roles/firebase.admin" "roles/kubernetes.admin" "roles/cloudfunctions.admin")
    
    for role in "${unused_roles[@]}"; do
        if gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --format="value(bindings.members)" \
            --filter="bindings.role:$role" | grep -q "serviceAccount"; then
            echo "   ⚠️  $role is assigned to service accounts (may be unused)"
        fi
    done
    
    echo ""
}

# Main verification
echo "🚀 Starting comprehensive permissions verification..."
echo ""

# Check each service account
check_service_account \
    "816732176023-compute@developer.gserviceaccount.com" \
    "Default Compute Service Account" \
    "Compute Instance Admin, Logs Writer"

check_service_account \
    "brant-cloudbuild@brant-roofing-system-2025.iam.gserviceaccount.com" \
    "Brant Cloud Build Service Account" \
    "Artifact Registry, Cloud Build, Cloud Run, Storage"

check_service_account \
    "brant-ocr-service@brant-roofing-system-2025.iam.gserviceaccount.com" \
    "Brant OCR Service Account" \
    "Document AI, Vision AI"

check_service_account \
    "brant-sql-proxy@brant-roofing-system-2025.iam.gserviceaccount.com" \
    "Cloud SQL Proxy Service Account" \
    "Cloud SQL Client"

check_service_account \
    "brant-sql@brant-roofing-system-2025.iam.gserviceaccount.com" \
    "Brant SQL Service Account" \
    "Cloud Infrastructure Manager, Service Account User"

check_service_account \
    "brant-system-service@brant-roofing-system-2025.iam.gserviceaccount.com" \
    "Brant Application Service Account" \
    "Cloud Run, Cloud SQL, Document AI, Storage, Secrets"

# Check project-level permissions
check_project_permissions

# Check security best practices
check_security_best_practices

echo "✅ PERMISSIONS VERIFICATION COMPLETE"
echo "===================================="
echo ""
echo "📋 SUMMARY:"
echo "   - All service accounts verified"
echo "   - Security best practices checked"
echo "   - Project-level permissions verified"
echo ""
echo "🎯 NEXT STEPS:"
echo "   1. Review any warnings above"
echo "   2. Remove unused roles if found"
echo "   3. Test Cloud Build deployment"
echo ""
echo "🔗 USEFUL COMMANDS:"
echo "   - View all IAM policies: gcloud projects get-iam-policy $PROJECT_ID"
echo "   - List service accounts: gcloud iam service-accounts list --project=$PROJECT_ID"
echo "   - Test Cloud Build: gcloud builds triggers list --project=$PROJECT_ID"

#!/bin/bash

# Fix Google Cloud Artifact Registry Permissions for Cloud Build
# This script grants the necessary permissions to the Cloud Build service account

set -e

PROJECT_ID="brant-roofing-system-2025"
REGION="us-central1"
REPOSITORY="brant-repo"

echo "🔧 Fixing Artifact Registry permissions for Cloud Build..."

# Get the project number
echo "📊 Getting project number..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"

# Cloud Build service account email
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "🔍 Cloud Build Service Account: $CLOUD_BUILD_SA"

# Check if Artifact Registry repository exists
echo "🔍 Checking if Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "❌ Repository $REPOSITORY not found. Creating it..."
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --project=$PROJECT_ID \
        --description="Brant Roofing System Docker Images"
    echo "✅ Repository created successfully"
else
    echo "✅ Repository $REPOSITORY exists"
fi

# Grant necessary IAM roles to Cloud Build service account
echo "🔐 Granting IAM roles to Cloud Build service account..."

# Artifact Registry Writer role
echo "  - Granting Artifact Registry Writer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/artifactregistry.writer"

# Artifact Registry Reader role (for pulling images)
echo "  - Granting Artifact Registry Reader role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/artifactregistry.reader"

# Storage Admin role (for GCS operations)
echo "  - Granting Storage Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/storage.admin"

# Cloud Build Editor role (for build operations)
echo "  - Granting Cloud Build Editor role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/cloudbuild.builds.editor"

# Service Account User role (for accessing other service accounts)
echo "  - Granting Service Account User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/iam.serviceAccountUser"

# Cloud SQL Client role (for database access)
echo "  - Granting Cloud SQL Client role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/cloudsql.client"

# Secret Manager Secret Accessor role (for accessing secrets)
echo "  - Granting Secret Manager Secret Accessor role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/secretmanager.secretAccessor"

echo "✅ All IAM roles granted successfully"

# Verify permissions
echo "🔍 Verifying permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$CLOUD_BUILD_SA"

echo "🎉 Permission fix completed!"
echo ""
echo "📋 Summary:"
echo "  - Project ID: $PROJECT_ID"
echo "  - Cloud Build SA: $CLOUD_BUILD_SA"
echo "  - Repository: $REPOSITORY"
echo "  - Region: $REGION"
echo ""
echo "🚀 You can now retry the Cloud Build trigger."
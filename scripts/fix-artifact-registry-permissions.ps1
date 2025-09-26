# Fix Google Cloud Artifact Registry Permissions for Cloud Build
# This script grants the necessary permissions to the Cloud Build service account

$PROJECT_ID = "brant-roofing-system-2025"
$REGION = "us-central1"
$REPOSITORY = "brant-repo"

Write-Host "🔧 Fixing Artifact Registry permissions for Cloud Build..." -ForegroundColor Green

# Get the project number
Write-Host "📊 Getting project number..." -ForegroundColor Yellow
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
Write-Host "Project Number: $PROJECT_NUMBER" -ForegroundColor Cyan

# Cloud Build service account email
$CLOUD_BUILD_SA = "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

Write-Host "🔍 Cloud Build Service Account: $CLOUD_BUILD_SA" -ForegroundColor Cyan

# Check if Artifact Registry repository exists
Write-Host "🔍 Checking if Artifact Registry repository exists..." -ForegroundColor Yellow
$repoExists = gcloud artifacts repositories describe $REPOSITORY --location=$REGION --project=$PROJECT_ID 2>$null
if (-not $repoExists) {
    Write-Host "❌ Repository $REPOSITORY not found. Creating it..." -ForegroundColor Red
    gcloud artifacts repositories create $REPOSITORY `
        --repository-format=docker `
        --location=$REGION `
        --project=$PROJECT_ID `
        --description="Brant Roofing System Docker Images"
    Write-Host "✅ Repository created successfully" -ForegroundColor Green
} else {
    Write-Host "✅ Repository $REPOSITORY exists" -ForegroundColor Green
}

# Grant necessary IAM roles to Cloud Build service account
Write-Host "🔐 Granting IAM roles to Cloud Build service account..." -ForegroundColor Yellow

# Artifact Registry Writer role
Write-Host "  - Granting Artifact Registry Writer role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/artifactregistry.writer"

# Artifact Registry Reader role (for pulling images)
Write-Host "  - Granting Artifact Registry Reader role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/artifactregistry.reader"

# Storage Admin role (for GCS operations)
Write-Host "  - Granting Storage Admin role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/storage.admin"

# Cloud Build Editor role (for build operations)
Write-Host "  - Granting Cloud Build Editor role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/cloudbuild.builds.editor"

# Service Account User role (for accessing other service accounts)
Write-Host "  - Granting Service Account User role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/iam.serviceAccountUser"

# Cloud SQL Client role (for database access)
Write-Host "  - Granting Cloud SQL Client role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/cloudsql.client"

# Secret Manager Secret Accessor role (for accessing secrets)
Write-Host "  - Granting Secret Manager Secret Accessor role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$CLOUD_BUILD_SA" `
    --role="roles/secretmanager.secretAccessor"

Write-Host "✅ All IAM roles granted successfully" -ForegroundColor Green

# Verify permissions
Write-Host "🔍 Verifying permissions..." -ForegroundColor Yellow
gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --format="table(bindings.role)" `
    --filter="bindings.members:$CLOUD_BUILD_SA"

Write-Host "🎉 Permission fix completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  - Project ID: $PROJECT_ID" -ForegroundColor White
Write-Host "  - Cloud Build SA: $CLOUD_BUILD_SA" -ForegroundColor White
Write-Host "  - Repository: $REPOSITORY" -ForegroundColor White
Write-Host "  - Region: $REGION" -ForegroundColor White
Write-Host ""
Write-Host "🚀 You can now retry the Cloud Build trigger." -ForegroundColor Green

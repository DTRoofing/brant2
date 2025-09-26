@echo off
echo 🔧 Quick Fix for Artifact Registry Permissions
echo.

REM Get project number
echo 📊 Getting project number...
for /f "tokens=*" %%i in ('gcloud projects describe brant-roofing-system-2025 --format="value(projectNumber)"') do set PROJECT_NUMBER=%%i
echo Project Number: %PROJECT_NUMBER%

REM Cloud Build service account
set CLOUD_BUILD_SA=%PROJECT_NUMBER%@cloudbuild.gserviceaccount.com
echo Cloud Build Service Account: %CLOUD_BUILD_SA%
echo.

echo 🔐 Granting IAM roles...
echo.

echo   - Artifact Registry Writer...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/artifactregistry.writer"

echo   - Artifact Registry Reader...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/artifactregistry.reader"

echo   - Storage Admin...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/storage.admin"

echo   - Cloud Build Editor...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/cloudbuild.builds.editor"

echo   - Service Account User...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/iam.serviceAccountUser"

echo   - Cloud SQL Client...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/cloudsql.client"

echo   - Secret Manager Secret Accessor...
gcloud projects add-iam-policy-binding brant-roofing-system-2025 --member="serviceAccount:%CLOUD_BUILD_SA%" --role="roles/secretmanager.secretAccessor"

echo.
echo ✅ All permissions granted!
echo.
echo 🚀 You can now retry the Cloud Build trigger.
echo.
pause

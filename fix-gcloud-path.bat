@echo off
REM Simple script to fix gcloud PATH and run verification

echo 🔧 Fixing gcloud PATH and running verification...

REM Add gcloud to current session PATH
set "PATH=%PATH%;C:\Users\brian\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

REM Test gcloud
echo Testing gcloud...
gcloud version --format="value(Google Cloud SDK)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ gcloud still not working. Trying alternative path...
    set "PATH=%PATH%;C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
    gcloud version --format="value(Google Cloud SDK)" 2>nul
    if %errorlevel% neq 0 (
        echo ❌ gcloud not found in common locations
        echo Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install
        pause
        exit /b 1
    )
)

echo ✅ gcloud is working!

REM Set project
echo Setting project to brant-roofing-system-2025...
gcloud config set project brant-roofing-system-2025

REM Run verification
echo.
echo Running permissions verification...
echo.

set "PROJECT_ID=brant-roofing-system-2025"

echo 🔍 SERVICE ACCOUNT ROLES VERIFICATION
echo ======================================

echo.
echo 1. Default Compute Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:816732176023-compute@developer.gserviceaccount.com"

echo.
echo 2. Brant Cloud Build Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-cloudbuild@brant-roofing-system-2025.iam.gserviceaccount.com"

echo.
echo 3. Brant OCR Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-ocr-service@brant-roofing-system-2025.iam.gserviceaccount.com"

echo.
echo 4. Cloud SQL Proxy Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-sql-proxy@brant-roofing-system-2025.iam.gserviceaccount.com"

echo.
echo 5. Brant SQL Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-sql@brant-roofing-system-2025.iam.gserviceaccount.com"

echo.
echo 6. Brant Application Service Account:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-system-service@brant-roofing-system-2025.iam.gserviceaccount.com"

echo.
echo 🏗️ PROJECT-LEVEL CHECKS
echo ========================

echo.
echo Artifact Registry Repository:
gcloud artifacts repositories describe brant-repo --location=us-central1 --project=%PROJECT_ID%

echo.
echo Cloud Build Triggers:
gcloud builds triggers list --project=%PROJECT_ID%

echo.
echo ✅ VERIFICATION COMPLETE!
echo.
pause

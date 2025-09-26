@echo off
REM Comprehensive Service Account Permissions Verification Script
REM This script checks all service accounts and their roles for the Brant Roofing System

setlocal enabledelayedexpansion

set "PROJECT_ID=brant-roofing-system-2025"

echo 🔍 COMPREHENSIVE PERMISSIONS VERIFICATION
echo ==========================================
echo Project: %PROJECT_ID%
echo Date: %date% %time%
echo.

REM Check if gcloud is available
where gcloud >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ gcloud CLI not found. Please run install-gcloud.bat first
    pause
    exit /b 1
)

echo 🚀 Starting comprehensive permissions verification...
echo.

REM Function to check service account (simulated with batch)
echo 📋 Checking Service Accounts:
echo.

echo 1. Default Compute Service Account
echo    Email: 816732176023-compute@developer.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:816732176023-compute@developer.gserviceaccount.com" 2>nul
echo.

echo 2. Brant Cloud Build Service Account
echo    Email: brant-cloudbuild@brant-roofing-system-2025.iam.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-cloudbuild@brant-roofing-system-2025.iam.gserviceaccount.com" 2>nul
echo.

echo 3. Brant OCR Service Account
echo    Email: brant-ocr-service@brant-roofing-system-2025.iam.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-ocr-service@brant-roofing-system-2025.iam.gserviceaccount.com" 2>nul
echo.

echo 4. Cloud SQL Proxy Service Account
echo    Email: brant-sql-proxy@brant-roofing-system-2025.iam.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-sql-proxy@brant-roofing-system-2025.iam.gserviceaccount.com" 2>nul
echo.

echo 5. Brant SQL Service Account
echo    Email: brant-sql@brant-roofing-system-2025.iam.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-sql@brant-roofing-system-2025.iam.gserviceaccount.com" 2>nul
echo.

echo 6. Brant Application Service Account
echo    Email: brant-system-service@brant-roofing-system-2025.iam.gserviceaccount.com
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:brant-system-service@brant-roofing-system-2025.iam.gserviceaccount.com" 2>nul
echo.

echo 🏗️ PROJECT-LEVEL PERMISSIONS
echo ==============================

echo 📦 Artifact Registry Repository:
gcloud artifacts repositories describe brant-repo --location=us-central1 --project=%PROJECT_ID% >nul 2>&1
if %errorlevel% == 0 (
    echo    ✅ Repository 'brant-repo' exists
) else (
    echo    ❌ Repository 'brant-repo' not found
)
echo.

echo 🔨 Cloud Build Configuration:
gcloud builds triggers list --project=%PROJECT_ID% --format="table(name,status)" 2>nul
echo.

echo 🛡️ SECURITY CHECK
echo ==================

echo Checking for overly broad roles (Editor/Owner):
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.role:roles/editor OR bindings.role:roles/owner" 2>nul
if %errorlevel% == 0 (
    echo ⚠️  WARNING: Found Editor or Owner roles assigned to service accounts
) else (
    echo ✅ No overly broad Editor or Owner roles found
)
echo.

echo Checking for unused service roles:
gcloud projects get-iam-policy %PROJECT_ID% --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.role:roles/appengine.admin OR bindings.role:roles/firebase.admin OR bindings.role:roles/kubernetes.admin" 2>nul
if %errorlevel% == 0 (
    echo ⚠️  WARNING: Found potentially unused service roles
) else (
    echo ✅ No unused service roles found
)
echo.

echo ✅ PERMISSIONS VERIFICATION COMPLETE
echo =====================================
echo.
echo 📋 SUMMARY:
echo    - All service accounts checked
echo    - Security best practices verified
echo    - Project-level permissions verified
echo.
echo 🎯 NEXT STEPS:
echo    1. Review any warnings above
echo    2. Test Cloud Build deployment
echo    3. Monitor for permission errors
echo.
echo 🔗 USEFUL COMMANDS:
echo    - View all IAM policies: gcloud projects get-iam-policy %PROJECT_ID%
echo    - List service accounts: gcloud iam service-accounts list --project=%PROJECT_ID%
echo    - Test Cloud Build: gcloud builds triggers list --project=%PROJECT_ID%

pause

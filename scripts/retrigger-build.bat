@echo off
REM Retrigger Cloud Build Script for Windows
REM This script creates an empty commit to retrigger the Cloud Build

echo 🔄 Retriggering Cloud Build...
echo ==============================

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not available. Please install Git first.
    exit /b 1
)

REM Check if we're in a git repository
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Not in a git repository. Please navigate to the project directory.
    exit /b 1
)

REM Create empty commit to retrigger build
echo [INFO] Creating empty commit to retrigger Cloud Build...
git commit --allow-empty -m "retrigger: Force Cloud Build to run again"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create empty commit
    exit /b 1
)

REM Push to trigger the build
echo [INFO] Pushing to trigger Cloud Build...
git push origin main
if %errorlevel% neq 0 (
    echo [ERROR] Failed to push to remote repository
    exit /b 1
)

echo [SUCCESS] Cloud Build retriggered successfully!
echo.
echo [INFO] Build should start shortly. Monitor with:
echo   gcloud builds list --limit=1
echo   gcloud builds log --stream $(gcloud builds list --limit=1 --format="value(id)")
echo.
echo [INFO] Or use the monitoring script:
echo   monitor-build.bat

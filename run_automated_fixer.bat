@echo off
REM Automated Build Fixer Runner for Windows
setlocal enabledelayedexpansion

REM Configuration
set PROJECT_ID=brant-roofing-system-2025
set REGION=us-central1
set MAX_ATTEMPTS=3

echo 🤖 Automated Build Fixer
echo =========================
echo Project: %PROJECT_ID%
echo Region: %REGION%
echo Max Attempts: %MAX_ATTEMPTS%
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ gcloud CLI not found. Please install Google Cloud SDK.
    exit /b 1
)

REM Check if user is authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Not authenticated with gcloud. Please run 'gcloud auth login'
    exit /b 1
)

REM Check if project exists
gcloud projects describe %PROJECT_ID% >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Project %PROJECT_ID% not found or no access
    exit /b 1
)

REM Set the project
gcloud config set project %PROJECT_ID%

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo ❌ Python not found. Please install Python 3.
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Check if cloudbuild.yaml exists
if not exist "cloudbuild.yaml" (
    echo ❌ cloudbuild.yaml not found. Please run from the project root.
    exit /b 1
)

REM Run the automated fixer
echo 🚀 Starting automated build fixer...
echo.

for /l %%i in (1,1,%MAX_ATTEMPTS%) do (
    echo 🔄 Attempt %%i/%MAX_ATTEMPTS%
    echo ================================
    
    %PYTHON_CMD% smart_build_fixer.py %PROJECT_ID% %REGION%
    if !errorlevel! equ 0 (
        echo.
        echo 🎉 SUCCESS! Build errors have been automatically resolved.
        echo ✅ The build should now pass without errors.
        exit /b 0
    ) else (
        echo.
        echo ⚠️ Attempt %%i failed.
        
        if %%i lss %MAX_ATTEMPTS% (
            echo 🔄 Retrying in 30 seconds...
            timeout /t 30 /nobreak >nul
        ) else (
            echo ❌ All attempts failed. Manual intervention may be required.
            echo.
            echo 📋 Check the logs for details:
            echo    - smart_build_fixer.log
            echo    - Recent build logs in Google Cloud Console
            echo.
            echo 🔧 Common manual fixes:
            echo    1. Check IAM permissions for Cloud Build service account
            echo    2. Verify all required APIs are enabled
            echo    3. Check for syntax errors in Python files
            echo    4. Ensure all dependencies are properly installed
            exit /b 1
        )
    )
)

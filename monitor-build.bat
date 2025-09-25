@echo off
REM Cloud Build Monitoring Script for Windows
REM This script monitors the latest Cloud Build and shows real-time status

echo 🔍 Monitoring Cloud Build...
echo ==========================

REM Check if gcloud is available
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] gcloud CLI is not available. Please install it first.
    exit /b 1
)

REM Check if authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No active gcloud authentication found. Please run 'gcloud auth login' first.
    exit /b 1
)

REM Get latest build ID
echo [INFO] Getting latest build information...
for /f "tokens=*" %%i in ('gcloud builds list --limit=1 --format="value(id)"') do set BUILD_ID=%%i

if "%BUILD_ID%"=="" (
    echo [WARNING] No builds found. The build may not have started yet.
    exit /b 0
)

echo Latest Build ID: %BUILD_ID%

REM Get build status
for /f "tokens=*" %%i in ('gcloud builds describe %BUILD_ID% --format="value(status)"') do set STATUS=%%i
echo Status: %STATUS%

REM Get build details
for /f "tokens=*" %%i in ('gcloud builds describe %BUILD_ID% --format="value(createTime)"') do set BUILD_TIME=%%i
for /f "tokens=*" %%i in ('gcloud builds describe %BUILD_ID% --format="value(duration)"') do set DURATION=%%i

echo Created: %BUILD_TIME%
echo Duration: %DURATION%

REM Handle different statuses
if "%STATUS%"=="WORKING" (
    echo [INFO] Build is currently running...
    echo.
    echo [INFO] Streaming live logs (Press Ctrl+C to stop):
    echo ==============================================
    gcloud builds log --stream %BUILD_ID%
) else if "%STATUS%"=="SUCCESS" (
    echo [SUCCESS] Build completed successfully!
    echo.
    echo [INFO] Build Summary:
    echo - Build ID: %BUILD_ID%
    echo - Status: %STATUS%
    echo - Duration: %DURATION%
    echo.
    echo [INFO] Services should be deployed to Cloud Run
    echo [INFO] Check your Cloud Run services in the Google Cloud Console
) else if "%STATUS%"=="FAILURE" (
    echo [ERROR] Build failed!
    echo.
    echo [INFO] Build Summary:
    echo - Build ID: %BUILD_ID%
    echo - Status: %STATUS%
    echo - Duration: %DURATION%
    echo.
    echo [INFO] Recent logs:
    echo =============
    gcloud builds log %BUILD_ID% --tail=50
) else if "%STATUS%"=="TIMEOUT" (
    echo [WARNING] Build timed out!
    echo.
    echo [INFO] Build Summary:
    echo - Build ID: %BUILD_ID%
    echo - Status: %STATUS%
    echo - Duration: %DURATION%
) else if "%STATUS%"=="CANCELLED" (
    echo [WARNING] Build was cancelled!
    echo.
    echo [INFO] Build Summary:
    echo - Build ID: %BUILD_ID%
    echo - Status: %STATUS%
    echo - Duration: %DURATION%
) else (
    echo [INFO] Build status: %STATUS%
)

echo.
echo [INFO] To view detailed build information:
echo gcloud builds describe %BUILD_ID%

echo [INFO] To view all recent builds:
echo gcloud builds list --limit=5

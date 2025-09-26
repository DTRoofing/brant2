@echo off
REM Build Monitoring Script for Brant Roofing System

set "BUILD_ID=fb55b5e9-cdf7-48e1-a4c0-e70409deb2c9"
set "PROJECT_ID=brant-roofing-system-2025"

echo 🔍 Monitoring Build Progress
echo ============================
echo Build ID: %BUILD_ID%
echo Project: %PROJECT_ID%
echo.

:check_status
echo [%date% %time%] Checking build status...

gcloud builds describe %BUILD_ID% --project=%PROJECT_ID% --format="value(status)" > temp_status.txt 2>nul
set /p BUILD_STATUS=<temp_status.txt
del temp_status.txt

if "%BUILD_STATUS%"=="QUEUED" (
    echo Status: QUEUED - Build is waiting in queue
    timeout /t 30 /nobreak >nul
    goto check_status
)

if "%BUILD_STATUS%"=="WORKING" (
    echo Status: WORKING - Build is in progress
    timeout /t 30 /nobreak >nul
    goto check_status
)

if "%BUILD_STATUS%"=="SUCCESS" (
    echo ✅ Status: SUCCESS - Build completed successfully!
    echo.
    echo 🎉 DEPLOYMENT SUCCESSFUL!
    echo All services have been deployed to Cloud Run.
    echo.
    echo 📋 Deployed Services:
    echo - brant-api (Backend API)
    echo - brant-worker (Background Processing)
    echo - brant-frontend (Frontend Application)
    echo.
    echo 🔗 View build details: https://console.cloud.google.com/cloud-build/builds/%BUILD_ID%?project=%PROJECT_ID%
    goto end
)

if "%BUILD_STATUS%"=="FAILURE" (
    echo ❌ Status: FAILURE - Build failed
    echo.
    echo 📋 Build Logs:
    gcloud builds log %BUILD_ID% --project=%PROJECT_ID%
    goto end
)

if "%BUILD_STATUS%"=="TIMEOUT" (
    echo ⏰ Status: TIMEOUT - Build timed out
    goto end
)

if "%BUILD_STATUS%"=="CANCELLED" (
    echo 🚫 Status: CANCELLED - Build was cancelled
    goto end
)

echo Unknown status: %BUILD_STATUS%
timeout /t 30 /nobreak >nul
goto check_status

:end
echo.
echo Build monitoring complete.
pause
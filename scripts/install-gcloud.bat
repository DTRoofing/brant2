@echo off
REM Google Cloud SDK Installation and Configuration Script
REM This script will install gcloud CLI if not present and configure it

echo 🔧 Google Cloud SDK Installation and Configuration
echo =================================================

REM Check if gcloud is already installed
where gcloud >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ gcloud CLI is already installed
    gcloud version --format="value(Google Cloud SDK)" 2>nul
    goto :check_auth
)

echo ❌ gcloud CLI not found. Checking for existing installation...

REM Check common installation paths
set "GCLOUD_PATH="
if exist "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
    set "GCLOUD_PATH=C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
)
if exist "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
    set "GCLOUD_PATH=C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"
)
if exist "%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
    set "GCLOUD_PATH=%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
)

if defined GCLOUD_PATH (
    echo ✅ Found gcloud at: %GCLOUD_PATH%
    echo Adding to PATH...
    
    REM Add to current session PATH
    set "PATH=%PATH%;%GCLOUD_PATH%"
    
    REM Add to user PATH permanently
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
    echo %USER_PATH% | findstr /C:"%GCLOUD_PATH%" >nul
    if %errorlevel% neq 0 (
        reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "%USER_PATH%;%GCLOUD_PATH%" /f >nul
        echo ✅ Added to user PATH
    )
) else (
    echo ❌ Google Cloud SDK not found. Please install it first:
    echo 1. Download from: https://cloud.google.com/sdk/docs/install
    echo 2. Or run: winget install Google.CloudSDK
    echo 3. Or run: choco install gcloudsdk
    pause
    exit /b 1
)

:check_auth
REM Verify gcloud is now available
gcloud version --format="value(Google Cloud SDK)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ gcloud CLI found but not working properly
    pause
    exit /b 1
)

echo ✅ gcloud CLI is working!

REM Check if authenticated
echo.
echo 🔐 Checking authentication status...
gcloud auth list --filter="status:ACTIVE" --format="value(account)" >nul 2>&1
if %errorlevel% == 0 (
    for /f %%i in ('gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2^>nul') do echo ✅ Authenticated as: %%i
) else (
    echo ❌ Not authenticated. Please run: gcloud auth login
    echo Or run: gcloud auth activate-service-account --key-file=path/to/key.json
)

REM Check if project is set
echo.
echo 🏗️ Checking project configuration...
gcloud config get-value project >nul 2>&1
if %errorlevel% == 0 (
    for /f %%i in ('gcloud config get-value project 2^>nul') do echo ✅ Project set to: %%i
) else (
    echo ❌ No project set. Please run: gcloud config set project brant-roofing-system-2025
)

echo.
echo 🎯 Next steps:
echo 1. If not authenticated: gcloud auth login
echo 2. Set project: gcloud config set project brant-roofing-system-2025
echo 3. Run verification: verify-permissions.bat
pause

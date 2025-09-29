@echo off
REM ===================================================================
REM SETUP PYTHON 3.11 ENVIRONMENT
REM ===================================================================
REM This script helps you set up Python 3.11 as your primary Python environment
REM by downloading, installing, and configuring Python 3.11.

setlocal enabledelayedexpansion

echo [SETUP] Starting Python 3.11 environment setup...

REM ===================================================================
REM CHECK CURRENT PYTHON INSTALLATIONS
REM ===================================================================
echo [SETUP] Checking current Python installations...

set PYTHON311_FOUND=false
set PYTHON313_FOUND=false
set OTHER_PYTHON_FOUND=false

REM Check for existing Python installations
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Found existing Python installations:
    for /f "tokens=*" %%i in ('where python') do (
        echo   - %%i
        %%i --version 2>nul | findstr /i "3\.11" >nul
        if !errorlevel! equ 0 (
            echo     Version: Python 3.11 ✓
            set PYTHON311_FOUND=true
        ) else (
            %%i --version 2>nul | findstr /i "3\.13" >nul
            if !errorlevel! equ 0 (
                echo     Version: Python 3.13 ✗
                set PYTHON313_FOUND=true
            ) else (
                %%i --version 2>nul
                echo     Version: Other ⚠
                set OTHER_PYTHON_FOUND=true
            )
        )
    )
) else (
    echo [INFO] No existing Python installations found
)

REM ===================================================================
REM DOWNLOAD AND INSTALL PYTHON 3.11
REM ===================================================================
if "%PYTHON311_FOUND%"=="false" (
    echo [SETUP] Python 3.11 not found. Downloading and installing...
    
    REM Create temporary directory for download
    set TEMP_DIR=%TEMP%\python311_setup
    if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
    
    REM Download Python 3.11 installer
    echo [SETUP] Downloading Python 3.11 installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP_DIR%\python-3.11.9-amd64.exe'}"
    
    if exist "%TEMP_DIR%\python-3.11.9-amd64.exe" (
        echo [SETUP] Installing Python 3.11...
        echo [INFO] This will open the Python installer. Please follow these steps:
        echo   1. Check "Add Python to PATH"
        echo   2. Check "Install for all users" (if you have admin rights)
        echo   3. Click "Install Now"
        echo   4. Wait for installation to complete
        echo   5. Close the installer when done
        echo.
        pause
        
        REM Run the installer
        start /wait "%TEMP_DIR%\python-3.11.9-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1
        
        REM Clean up
        del "%TEMP_DIR%\python-3.11.9-amd64.exe"
        rmdir "%TEMP_DIR%"
        
        echo [SETUP] Python 3.11 installation completed
    ) else (
        echo [ERROR] Failed to download Python 3.11 installer
        echo [INFO] Please download Python 3.11 manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    echo [SETUP] Python 3.11 already installed ✓
)

REM ===================================================================
REM CONFIGURE PYTHON 3.11 AS PRIMARY
REM ===================================================================
echo [SETUP] Configuring Python 3.11 as primary Python...

REM Find Python 3.11 installation
set PYTHON311_PATH=
for /f "tokens=*" %%i in ('where python') do (
    %%i --version 2>nul | findstr /i "3\.11" >nul
    if !errorlevel! equ 0 (
        set PYTHON311_PATH=%%i
        goto :found_python311
    )
)

:found_python311
if defined PYTHON311_PATH (
    echo [INFO] Found Python 3.11 at: %PYTHON311_PATH%
    
    REM Get the directory containing python.exe
    for %%i in ("%PYTHON311_PATH%") do set PYTHON311_DIR=%%~dpi
    for %%i in ("%PYTHON311_DIR%") do set PYTHON311_DIR=%%~pi
    
    echo [INFO] Python 3.11 directory: %PYTHON311_DIR%
    
    REM Update environment variables
    echo [SETUP] Updating environment variables...
    
    REM Set PYTHON_HOME
    setx PYTHON_HOME "%PYTHON311_DIR%" /M
    echo [INFO] Set PYTHON_HOME to: %PYTHON311_DIR%
    
    REM Set PYTHON_EXECUTABLE
    setx PYTHON_EXECUTABLE "%PYTHON311_PATH%" /M
    echo [INFO] Set PYTHON_EXECUTABLE to: %PYTHON311_PATH%
    
    REM Update PATH to prioritize Python 3.11
    echo [SETUP] Updating PATH to prioritize Python 3.11...
    
    REM Get current PATH
    for /f "tokens=*" %%i in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do (
        set CURRENT_PATH=%%i
    )
    
    REM Remove Python 3.13 paths from PATH
    set NEW_PATH=
    for %%i in ("%CURRENT_PATH:;=" "%") do (
        set "CURRENT_PATH_ITEM=%%~i"
        echo !CURRENT_PATH_ITEM! | findstr /i "python.*3\.13" >nul
        if !errorlevel! neq 0 (
            if defined NEW_PATH (
                set "NEW_PATH=!NEW_PATH!;!CURRENT_PATH_ITEM!"
            ) else (
                set "NEW_PATH=!CURRENT_PATH_ITEM!"
            )
        ) else (
            echo [REMOVED] Python 3.13 path: !CURRENT_PATH_ITEM!
        )
    )
    
    REM Add Python 3.11 paths to the beginning of PATH
    set PYTHON311_SCRIPTS=%PYTHON311_DIR%Scripts
    set PYTHON311_LIB=%PYTHON311_DIR%Lib
    
    REM Check if Python 3.11 paths are already in PATH
    echo %NEW_PATH% | findstr /i "%PYTHON311_DIR%" >nul
    if !errorlevel! neq 0 (
        set "NEW_PATH=%PYTHON311_DIR%;%PYTHON311_SCRIPTS%;%NEW_PATH%"
        echo [ADDED] Python 3.11 paths to PATH
    ) else (
        echo [INFO] Python 3.11 paths already in PATH
    )
    
    REM Update PATH in registry
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "%NEW_PATH%" /f
    echo [INFO] Updated system PATH
    
    REM Update current session PATH
    set "PATH=%PYTHON311_DIR%;%PYTHON311_SCRIPTS%;%PATH%"
    echo [INFO] Updated current session PATH
    
) else (
    echo [ERROR] Could not find Python 3.11 installation
    echo [INFO] Please ensure Python 3.11 is installed and in PATH
    pause
    exit /b 1
)

REM ===================================================================
REM VERIFY PYTHON 3.11 SETUP
REM ===================================================================
echo [SETUP] Verifying Python 3.11 setup...

REM Check Python version
python --version 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Python command working:
    python --version
) else (
    echo [WARNING] Python command not working in current session
)

REM Check Python3 version
python3 --version 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Python3 command working:
    python3 --version
) else (
    echo [WARNING] Python3 command not working in current session
)

REM Check pip
pip --version 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] pip working:
    pip --version
) else (
    echo [WARNING] pip not working in current session
)

REM ===================================================================
REM INSTALL ESSENTIAL PACKAGES
REM ===================================================================
echo [SETUP] Installing essential Python packages...

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install essential packages
echo [INFO] Installing essential packages...
python -m pip install setuptools wheel

REM Install project dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo [INFO] Installing project dependencies from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo [INFO] No requirements.txt found, skipping project dependencies
)

REM ===================================================================
REM CREATE VIRTUAL ENVIRONMENT
REM ===================================================================
echo [SETUP] Creating Python 3.11 virtual environment...

if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Created virtual environment: venv
) else (
    echo [INFO] Virtual environment already exists: venv
)

REM ===================================================================
REM FINAL VERIFICATION
REM ===================================================================
echo [SETUP] Final verification...

REM Run the verification script
if exist "%~dp0verify-python311-env.bat" (
    echo [INFO] Running Python 3.11 verification...
    call "%~dp0verify-python311-env.bat"
) else (
    echo [WARNING] Verification script not found
)

REM ===================================================================
REM SUMMARY
REM ===================================================================
echo [SETUP] Python 3.11 environment setup completed!
echo.
echo [SUMMARY] What was done:
echo   - Checked for existing Python installations
echo   - Downloaded and installed Python 3.11 (if needed)
echo   - Configured Python 3.11 as primary Python
echo   - Updated environment variables (PYTHON_HOME, PYTHON_EXECUTABLE)
echo   - Updated PATH to prioritize Python 3.11
echo   - Removed Python 3.13 paths from PATH
echo   - Installed essential Python packages
echo   - Created virtual environment
echo   - Verified the setup
echo.
echo [IMPORTANT] You may need to restart your terminal or system for all changes to take effect.
echo [INFO] To activate the virtual environment, run: venv\Scripts\activate
echo [INFO] To verify the setup, run: scripts\verify-python311-env.bat
echo.

pause

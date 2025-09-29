@echo off
REM ===================================================================
REM VERIFY PYTHON 3.11 ENVIRONMENT VARIABLES
REM ===================================================================
REM This script verifies that all Python-related environment variables
REM point to Python 3.11 installations and not Python 3.13 or other versions.

setlocal enabledelayedexpansion

echo [VERIFY] Starting Python 3.11 environment verification...

REM ===================================================================
REM CHECK PYTHON EXECUTABLES IN PATH
REM ===================================================================
echo [VERIFY] Checking Python executables in PATH...

set PYTHON_FOUND=false
set PYTHON311_FOUND=false
set PYTHON313_FOUND=false
set OTHER_PYTHON_FOUND=false

REM Check for python command
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_FOUND=true
    echo [INFO] Found 'python' command:
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
                echo     Version: Other ✗
                set OTHER_PYTHON_FOUND=true
            )
        )
    )
) else (
    echo [WARNING] No 'python' command found in PATH
)

REM Check for python3 command
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_FOUND=true
    echo [INFO] Found 'python3' command:
    for /f "tokens=*" %%i in ('where python3') do (
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
                echo     Version: Other ✗
                set OTHER_PYTHON_FOUND=true
            )
        )
    )
) else (
    echo [WARNING] No 'python3' command found in PATH
)

REM ===================================================================
REM CHECK PYTHON-RELATED ENVIRONMENT VARIABLES
REM ===================================================================
echo [VERIFY] Checking Python-related environment variables...

REM Check PYTHONPATH
if defined PYTHONPATH (
    echo [INFO] PYTHONPATH is set:
    echo   %PYTHONPATH%
    
    REM Check if PYTHONPATH contains Python 3.11 paths
    echo %PYTHONPATH% | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo   Contains Python 3.11 paths ✓
    ) else (
        echo   No Python 3.11 paths found ⚠
    )
    
    REM Check if PYTHONPATH contains Python 3.13 paths
    echo %PYTHONPATH% | findstr /i "python.*3\.13" >nul
    if !errorlevel! equ 0 (
        echo   Contains Python 3.13 paths ✗
    ) else (
        echo   No Python 3.13 paths found ✓
    )
) else (
    echo [INFO] PYTHONPATH is not set
)

REM Check PYTHON_HOME
if defined PYTHON_HOME (
    echo [INFO] PYTHON_HOME is set:
    echo   %PYTHON_HOME%
    
    echo %PYTHON_HOME% | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo   Points to Python 3.11 ✓
    ) else (
        echo %PYTHON_HOME% | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo   Points to Python 3.13 ✗
        ) else (
            echo   Points to other Python version ⚠
        )
    )
) else (
    echo [INFO] PYTHON_HOME is not set
)

REM Check PYTHON_ROOT
if defined PYTHON_ROOT (
    echo [INFO] PYTHON_ROOT is set:
    echo   %PYTHON_ROOT%
    
    echo %PYTHON_ROOT% | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo   Points to Python 3.11 ✓
    ) else (
        echo %PYTHON_ROOT% | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo   Points to Python 3.13 ✗
        ) else (
            echo   Points to other Python version ⚠
        )
    )
) else (
    echo [INFO] PYTHON_ROOT is not set
)

REM Check PYTHON_INSTALL_DIR
if defined PYTHON_INSTALL_DIR (
    echo [INFO] PYTHON_INSTALL_DIR is set:
    echo   %PYTHON_INSTALL_DIR%
    
    echo %PYTHON_INSTALL_DIR% | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo   Points to Python 3.11 ✓
    ) else (
        echo %PYTHON_INSTALL_DIR% | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo   Points to Python 3.13 ✗
        ) else (
            echo   Points to other Python version ⚠
        )
    )
) else (
    echo [INFO] PYTHON_INSTALL_DIR is not set
)

REM Check PYTHON_EXECUTABLE
if defined PYTHON_EXECUTABLE (
    echo [INFO] PYTHON_EXECUTABLE is set:
    echo   %PYTHON_EXECUTABLE%
    
    echo %PYTHON_EXECUTABLE% | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo   Points to Python 3.11 ✓
    ) else (
        echo %PYTHON_EXECUTABLE% | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo   Points to Python 3.13 ✗
        ) else (
            echo   Points to other Python version ⚠
        )
    )
) else (
    echo [INFO] PYTHON_EXECUTABLE is not set
)

REM ===================================================================
REM CHECK PATH FOR PYTHON INSTALLATIONS
REM ===================================================================
echo [VERIFY] Checking PATH for Python installations...

set PYTHON311_PATHS_FOUND=0
set PYTHON313_PATHS_FOUND=0
set OTHER_PYTHON_PATHS_FOUND=0

REM Check each path in PATH for Python installations
for %%i in ("%PATH:;=" "%") do (
    set "CURRENT_PATH=%%~i"
    
    REM Check if this path contains Python 3.11
    echo !CURRENT_PATH! | findstr /i "python.*3\.11" >nul
    if !errorlevel! equ 0 (
        echo [FOUND] Python 3.11 path: !CURRENT_PATH! ✓
        set /a PYTHON311_PATHS_FOUND+=1
    ) else (
        REM Check if this path contains Python 3.13
        echo !CURRENT_PATH! | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo [FOUND] Python 3.13 path: !CURRENT_PATH! ✗
            set /a PYTHON313_PATHS_FOUND+=1
        ) else (
            REM Check if this path contains other Python versions
            echo !CURRENT_PATH! | findstr /i "python" >nul
            if !errorlevel! equ 0 (
                echo [FOUND] Other Python path: !CURRENT_PATH! ⚠
                set /a OTHER_PYTHON_PATHS_FOUND+=1
            )
        )
    )
)

REM ===================================================================
REM CHECK VIRTUAL ENVIRONMENTS
REM ===================================================================
echo [VERIFY] Checking for virtual environments...

REM Check VIRTUAL_ENV
if defined VIRTUAL_ENV (
    echo [INFO] VIRTUAL_ENV is set:
    echo   %VIRTUAL_ENV%
    
    REM Check if the virtual environment uses Python 3.11
    if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
        "%VIRTUAL_ENV%\Scripts\python.exe" --version 2>nul | findstr /i "3\.11" >nul
        if !errorlevel! equ 0 (
            echo   Virtual environment uses Python 3.11 ✓
        ) else (
            "%VIRTUAL_ENV%\Scripts\python.exe" --version 2>nul | findstr /i "3\.13" >nul
            if !errorlevel! equ 0 (
                echo   Virtual environment uses Python 3.13 ✗
            ) else (
                echo   Virtual environment uses other Python version ⚠
            )
        )
    ) else (
        echo   Cannot determine Python version in virtual environment ⚠
    )
) else (
    echo [INFO] VIRTUAL_ENV is not set (no active virtual environment)
)

REM ===================================================================
REM SUMMARY
REM ===================================================================
echo [VERIFY] Verification Summary:
echo.

if "%PYTHON_FOUND%"=="true" (
    if "%PYTHON311_FOUND%"=="true" (
        echo [RESULT] Python 3.11 executables found ✓
    ) else (
        echo [RESULT] Python 3.11 executables NOT found ✗
    )
    
    if "%PYTHON313_FOUND%"=="true" (
        echo [RESULT] Python 3.13 executables found ✗
    ) else (
        echo [RESULT] No Python 3.13 executables found ✓
    )
    
    if "%OTHER_PYTHON_FOUND%"=="true" (
        echo [RESULT] Other Python versions found ⚠
    ) else (
        echo [RESULT] No other Python versions found ✓
    )
) else (
    echo [RESULT] No Python executables found in PATH ✗
)

echo [RESULT] Python 3.11 paths in PATH: %PYTHON311_PATHS_FOUND%
echo [RESULT] Python 3.13 paths in PATH: %PYTHON313_PATHS_FOUND%
echo [RESULT] Other Python paths in PATH: %OTHER_PYTHON_PATHS_FOUND%

echo.
if "%PYTHON311_FOUND%"=="true" (
    if "%PYTHON313_FOUND%"=="false" (
        if "%OTHER_PYTHON_FOUND%"=="false" (
            echo [SUCCESS] All Python environment variables point to Python 3.11 ✓
        ) else (
            echo [WARNING] Python 3.11 found but other Python versions also present ⚠
        )
    ) else (
        echo [ERROR] Python 3.13 found in environment ✗
    )
) else (
    echo [ERROR] Python 3.11 not found in environment ✗
)

echo.
echo [VERIFY] Verification completed.

pause


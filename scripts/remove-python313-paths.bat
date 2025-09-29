@echo off
REM ===================================================================
REM REMOVE PYTHON 3.13 PATHS FROM ENVIRONMENT VARIABLES
REM ===================================================================
REM This script removes Python 3.13 paths from PATH and other environment variables
REM to prevent conflicts with other Python versions.

echo [INFO] Starting Python 3.13 path removal process...

REM ===================================================================
REM BACKUP CURRENT ENVIRONMENT
REM ===================================================================
echo [INFO] Creating backup of current environment variables...
set BACKUP_DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DATE=%BACKUP_DATE: =0%
echo [INFO] Backup timestamp: %BACKUP_DATE%

REM Backup PATH
echo %PATH% > "env_backup_%BACKUP_DATE%_PATH.txt"
echo [INFO] PATH backed up to: env_backup_%BACKUP_DATE%_PATH.txt

REM Backup PYTHONPATH if it exists
if defined PYTHONPATH (
    echo %PYTHONPATH% > "env_backup_%BACKUP_DATE%_PYTHONPATH.txt"
    echo [INFO] PYTHONPATH backed up to: env_backup_%BACKUP_DATE%_PYTHONPATH.txt
)

REM ===================================================================
REM REMOVE PYTHON 3.13 PATHS FROM PATH
REM ===================================================================
echo [INFO] Removing Python 3.13 paths from PATH...

REM Create a temporary file to store the cleaned PATH
set TEMP_PATH_FILE=%TEMP%\clean_path_%RANDOM%.txt
echo. > "%TEMP_PATH_FILE%"

REM Process each path in PATH
for %%i in ("%PATH:;=" "%") do (
    set "CURRENT_PATH=%%~i"
    
    REM Check if the path contains Python 3.13 references
    echo !CURRENT_PATH! | findstr /i "python.*3\.13" >nul
    if !errorlevel! neq 0 (
        REM Path doesn't contain Python 3.13, keep it
        echo !CURRENT_PATH! >> "%TEMP_PATH_FILE%"
    ) else (
        echo [REMOVED] Python 3.13 path: !CURRENT_PATH!
    )
)

REM Rebuild PATH from cleaned paths
set NEW_PATH=
for /f "usebackq delims=" %%i in ("%TEMP_PATH_FILE%") do (
    if defined NEW_PATH (
        set "NEW_PATH=!NEW_PATH!;%%i"
    ) else (
        set "NEW_PATH=%%i"
    )
)

REM Clean up temporary file
del "%TEMP_PATH_FILE%"

REM ===================================================================
REM REMOVE PYTHON 3.13 PATHS FROM PYTHONPATH
REM ===================================================================
if defined PYTHONPATH (
    echo [INFO] Removing Python 3.13 paths from PYTHONPATH...
    
    set TEMP_PYTHONPATH_FILE=%TEMP%\clean_pythonpath_%RANDOM%.txt
    echo. > "%TEMP_PYTHONPATH_FILE%"
    
    for %%i in ("%PYTHONPATH:;=" "%") do (
        set "CURRENT_PYTHONPATH=%%~i"
        
        echo !CURRENT_PYTHONPATH! | findstr /i "python.*3\.13" >nul
        if !errorlevel! neq 0 (
            echo !CURRENT_PYTHONPATH! >> "%TEMP_PYTHONPATH_FILE%"
        ) else (
            echo [REMOVED] Python 3.13 PYTHONPATH: !CURRENT_PYTHONPATH!
        )
    )
    
    set NEW_PYTHONPATH=
    for /f "usebackq delims=" %%i in ("%TEMP_PYTHONPATH_FILE%") do (
        if defined NEW_PYTHONPATH (
            set "NEW_PYTHONPATH=!NEW_PYTHONPATH!;%%i"
        ) else (
            set "NEW_PYTHONPATH=%%i"
        )
    )
    
    del "%TEMP_PYTHONPATH_FILE%"
)

REM ===================================================================
REM REMOVE OTHER PYTHON 3.13 RELATED ENVIRONMENT VARIABLES
REM ===================================================================
echo [INFO] Checking for other Python 3.13 related environment variables...

REM List of environment variables that might contain Python 3.13 paths
set PYTHON_ENV_VARS=PYTHON_HOME PYTHON_ROOT PYTHON_INSTALL_DIR PYTHON_EXECUTABLE

for %%v in (%PYTHON_ENV_VARS%) do (
    if defined %%v (
        echo !%%v! | findstr /i "python.*3\.13" >nul
        if !errorlevel! equ 0 (
            echo [REMOVED] Python 3.13 environment variable %%v: !%%v!
            set "%%v="
        )
    )
)

REM ===================================================================
REM APPLY CHANGES
REM ===================================================================
echo [INFO] Applying cleaned environment variables...

REM Update PATH
set "PATH=%NEW_PATH%"

REM Update PYTHONPATH if it was modified
if defined NEW_PYTHONPATH (
    set "PYTHONPATH=%NEW_PYTHONPATH%"
)

REM ===================================================================
REM VERIFY CHANGES
REM ===================================================================
echo [INFO] Verifying changes...

REM Check if any Python 3.13 paths remain in PATH
echo %PATH% | findstr /i "python.*3\.13" >nul
if !errorlevel! equ 0 (
    echo [WARNING] Some Python 3.13 paths may still exist in PATH
) else (
    echo [SUCCESS] No Python 3.13 paths found in PATH
)

REM Check if any Python 3.13 paths remain in PYTHONPATH
if defined PYTHONPATH (
    echo %PYTHONPATH% | findstr /i "python.*3\.13" >nul
    if !errorlevel! equ 0 (
        echo [WARNING] Some Python 3.13 paths may still exist in PYTHONPATH
    ) else (
        echo [SUCCESS] No Python 3.13 paths found in PYTHONPATH
    )
)

REM ===================================================================
REM DISPLAY CURRENT PYTHON VERSIONS
REM ===================================================================
echo [INFO] Current Python installations in PATH:
where python >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('where python') do (
        echo   - %%i
        %%i --version 2>nul
    )
) else (
    echo   - No Python found in PATH
)

where python3 >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('where python3') do (
        echo   - %%i
        %%i --version 2>nul
    )
)

REM ===================================================================
REM SUMMARY
REM ===================================================================
echo.
echo [SUMMARY] Python 3.13 path removal completed
echo [INFO] Backup files created with timestamp: %BACKUP_DATE%
echo [INFO] Current PATH length: %PATH:~0,1% characters
if defined PYTHONPATH (
    echo [INFO] Current PYTHONPATH length: %PYTHONPATH:~0,1% characters
)
echo.
echo [NOTE] These changes are only active in this command prompt session.
echo [NOTE] To make changes permanent, run this script from a new command prompt
echo [NOTE] or restart your system.
echo.

pause

@echo off
REM ===================================================================
REM TEST SCRIPT FOR PYTHON 3.13 PATH REMOVAL
REM ===================================================================
REM This script tests the Python 3.13 removal functionality by temporarily
REM adding fake Python 3.13 paths and then removing them.

echo [TEST] Starting Python 3.13 removal test...

REM ===================================================================
REM SETUP TEST ENVIRONMENT
REM ===================================================================
echo [TEST] Setting up test environment with fake Python 3.13 paths...

REM Add fake Python 3.13 paths to PATH
set "TEST_PYTHON313_PATH_1=C:\Python313\Scripts"
set "TEST_PYTHON313_PATH_2=C:\Python313\Lib\site-packages"
set "TEST_PYTHON313_PATH_3=C:\Program Files\Python313"

REM Add fake Python 3.13 paths to PYTHONPATH
set "TEST_PYTHON313_PYTHONPATH_1=C:\Python313\Lib"
set "TEST_PYTHON313_PYTHONPATH_2=C:\Python313\Lib\site-packages"

REM Add fake Python 3.13 environment variables
set "TEST_PYTHON313_HOME=C:\Python313"
set "TEST_PYTHON313_EXECUTABLE=C:\Python313\python.exe"

REM Add these to current session PATH and PYTHONPATH
set "PATH=%PATH%;%TEST_PYTHON313_PATH_1%;%TEST_PYTHON313_PATH_2%;%TEST_PYTHON313_PATH_3%"
set "PYTHONPATH=%PYTHONPATH%;%TEST_PYTHON313_PYTHONPATH_1%;%TEST_PYTHON313_PYTHONPATH_2%"

echo [TEST] Added fake Python 3.13 paths to environment
echo [TEST] Current PATH contains Python 3.13 paths: %PATH% | findstr /i "python.*3\.13" >nul && echo YES || echo NO
echo [TEST] Current PYTHONPATH contains Python 3.13 paths: %PYTHONPATH% | findstr /i "python.*3\.13" >nul && echo YES || echo NO

REM ===================================================================
REM RUN THE REMOVAL SCRIPT
REM ===================================================================
echo [TEST] Running Python 3.13 removal script...
call "%~dp0remove-python313-paths.bat"

REM ===================================================================
REM VERIFY RESULTS
REM ===================================================================
echo [TEST] Verifying removal results...

REM Check if Python 3.13 paths were removed from PATH
echo %PATH% | findstr /i "python.*3\.13" >nul
if %errorlevel% equ 0 (
    echo [TEST FAILED] Python 3.13 paths still exist in PATH
    echo %PATH% | findstr /i "python.*3\.13"
) else (
    echo [TEST PASSED] No Python 3.13 paths found in PATH
)

REM Check if Python 3.13 paths were removed from PYTHONPATH
if defined PYTHONPATH (
    echo %PYTHONPATH% | findstr /i "python.*3\.13" >nul
    if %errorlevel% equ 0 (
        echo [TEST FAILED] Python 3.13 paths still exist in PYTHONPATH
        echo %PYTHONPATH% | findstr /i "python.*3\.13"
    ) else (
        echo [TEST PASSED] No Python 3.13 paths found in PYTHONPATH
    )
) else (
    echo [TEST PASSED] PYTHONPATH is not set or empty
)

REM Check if Python 3.13 environment variables were cleared
if defined TEST_PYTHON313_HOME (
    echo [TEST FAILED] TEST_PYTHON313_HOME still exists
) else (
    echo [TEST PASSED] TEST_PYTHON313_HOME was cleared
)

if defined TEST_PYTHON313_EXECUTABLE (
    echo [TEST FAILED] TEST_PYTHON313_EXECUTABLE still exists
) else (
    echo [TEST PASSED] TEST_PYTHON313_EXECUTABLE was cleared
)

REM ===================================================================
REM CLEANUP
REM ===================================================================
echo [TEST] Cleaning up test environment...

REM Remove test environment variables
set "TEST_PYTHON313_PATH_1="
set "TEST_PYTHON313_PATH_2="
set "TEST_PYTHON313_PATH_3="
set "TEST_PYTHON313_PYTHONPATH_1="
set "TEST_PYTHON313_PYTHONPATH_2="
set "TEST_PYTHON313_HOME="
set "TEST_PYTHON313_EXECUTABLE="

echo [TEST] Test completed. Check the results above.
echo [TEST] If all tests passed, the Python 3.13 removal script is working correctly.

pause


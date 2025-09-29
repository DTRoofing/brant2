@echo off
REM ===================================================================
REM TEST SCRIPT FOR PYTHON 3.11 VERIFICATION
REM ===================================================================
REM This script tests the Python 3.11 verification functionality by
REM temporarily setting up different Python environment scenarios.

echo [TEST] Starting Python 3.11 verification test...

REM ===================================================================
REM TEST SCENARIO 1: PYTHON 3.11 ONLY
REM ===================================================================
echo [TEST] Scenario 1: Python 3.11 only environment...

REM Set up a clean Python 3.11 environment
set "TEST_PYTHON311_HOME=C:\Python311"
set "TEST_PYTHON311_EXECUTABLE=C:\Python311\python.exe"
set "TEST_PYTHON311_PATH=C:\Python311;C:\Python311\Scripts"

REM Set environment variables for this test
set "PYTHON_HOME=%TEST_PYTHON311_HOME%"
set "PYTHON_EXECUTABLE=%TEST_PYTHON311_EXECUTABLE%"
set "PATH=%TEST_PYTHON311_PATH%;%PATH%"

echo [TEST] Running verification with Python 3.11 only...
call "%~dp0verify-python311-env.bat"

echo [TEST] Scenario 1 completed. Press any key to continue to scenario 2...
pause >nul

REM ===================================================================
REM TEST SCENARIO 2: PYTHON 3.11 AND 3.13 MIXED
REM ===================================================================
echo [TEST] Scenario 2: Python 3.11 and 3.13 mixed environment...

REM Add Python 3.13 paths to the environment
set "TEST_PYTHON313_HOME=C:\Python313"
set "TEST_PYTHON313_EXECUTABLE=C:\Python313\python.exe"
set "TEST_PYTHON313_PATH=C:\Python313;C:\Python313\Scripts"

REM Add Python 3.13 to PATH
set "PATH=%PATH%;%TEST_PYTHON313_PATH%"

echo [TEST] Running verification with mixed Python versions...
call "%~dp0verify-python311-env.bat"

echo [TEST] Scenario 2 completed. Press any key to continue to scenario 3...
pause >nul

REM ===================================================================
REM TEST SCENARIO 3: PYTHON 3.13 ONLY
REM ===================================================================
echo [TEST] Scenario 3: Python 3.13 only environment...

REM Remove Python 3.11 and keep only Python 3.13
set "PYTHON_HOME=%TEST_PYTHON313_HOME%"
set "PYTHON_EXECUTABLE=%TEST_PYTHON313_EXECUTABLE%"
set "PATH=%TEST_PYTHON313_PATH%"

echo [TEST] Running verification with Python 3.13 only...
call "%~dp0verify-python311-env.bat"

echo [TEST] Scenario 3 completed. Press any key to continue to scenario 4...
pause >nul

REM ===================================================================
REM TEST SCENARIO 4: NO PYTHON FOUND
REM ===================================================================
echo [TEST] Scenario 4: No Python found environment...

REM Remove all Python paths
set "PYTHON_HOME="
set "PYTHON_EXECUTABLE="
set "PATH="

echo [TEST] Running verification with no Python...
call "%~dp0verify-python311-env.bat"

echo [TEST] Scenario 4 completed. Press any key to continue to cleanup...
pause >nul

REM ===================================================================
REM CLEANUP
REM ===================================================================
echo [TEST] Cleaning up test environment...

REM Remove test environment variables
set "TEST_PYTHON311_HOME="
set "TEST_PYTHON311_EXECUTABLE="
set "TEST_PYTHON311_PATH="
set "TEST_PYTHON313_HOME="
set "TEST_PYTHON313_EXECUTABLE="
set "TEST_PYTHON313_PATH="

REM Restore original environment (this is a simplified restoration)
REM In a real scenario, you would restore from backup files

echo [TEST] Test completed. Check the results above.
echo [TEST] Expected results:
echo   - Scenario 1: SUCCESS - All Python environment variables point to Python 3.11
echo   - Scenario 2: WARNING - Python 3.11 found but other Python versions also present
echo   - Scenario 3: ERROR - Python 3.13 found in environment
echo   - Scenario 4: ERROR - Python 3.11 not found in environment

pause



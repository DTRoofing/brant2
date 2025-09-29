@echo off
REM Comprehensive Build Test Battery Script for Windows
REM This script runs all build verification tests in sequence

setlocal enabledelayedexpansion

REM Configuration
set VERBOSE=false
set SKIP_DOCKER=false
set OUTPUT_DIR=test_results
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Parse command line arguments
:parse_args
if "%~1"=="-v" set VERBOSE=true & shift & goto parse_args
if "%~1"=="--verbose" set VERBOSE=true & shift & goto parse_args
if "%~1"=="--skip-docker" set SKIP_DOCKER=true & shift & goto parse_args
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="-o" set OUTPUT_DIR=%~2 & shift & shift & goto parse_args
if "%~1"=="--output" set OUTPUT_DIR=%~2 & shift & shift & goto parse_args
if not "%~1"=="" echo Unknown option: %~1 & exit /b 1
goto main

:show_help
echo Usage: %0 [OPTIONS]
echo Options:
echo   -v, --verbose     Enable verbose output
echo   --skip-docker     Skip Docker build tests
echo   -o, --output DIR  Output directory for reports
echo   -h, --help        Show this help
exit /b 0

REM Create output directory
:main
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 🏗️  COMPREHENSIVE BUILD TEST BATTERY
echo ====================================
echo Timestamp: %date% %time%
echo Output Directory: %OUTPUT_DIR%
echo Verbose: %VERBOSE%
echo Skip Docker: %SKIP_DOCKER%
echo.

REM Check prerequisites
echo [%time%] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [%time%] ❌ Python is required but not installed
    exit /b 1
)

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo [%time%] ❌ pyproject.toml not found. Please run from project root.
    exit /b 1
)

REM Check Docker (if not skipping)
if "%SKIP_DOCKER%"=="false" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo [%time%] ⚠️  Docker not found. Skipping Docker tests.
        set SKIP_DOCKER=true
    ) else (
        docker info >nul 2>&1
        if errorlevel 1 (
            echo [%time%] ⚠️  Docker daemon not running. Skipping Docker tests.
            set SKIP_DOCKER=true
        )
    )
)

echo [%time%] ✅ Prerequisites check completed

REM Test results tracking
set total_tests=0
set passed_tests=0

REM Test 1: Dependency Verification
echo.
echo [%time%] Running dependency_verification...
set /a total_tests+=1

set verbose_flag=
if "%VERBOSE%"=="true" set verbose_flag=--verbose

python scripts/dependency_verifier.py %verbose_flag% --output "%OUTPUT_DIR%/dependency_report_%TIMESTAMP%.txt" > "%OUTPUT_DIR%/dependency_verification_%TIMESTAMP%.log" 2>&1
if errorlevel 1 (
    echo [%time%] ❌ dependency_verification failed
    if "%VERBOSE%"=="true" type "%OUTPUT_DIR%/dependency_verification_%TIMESTAMP%.log"
) else (
    echo [%time%] ✅ dependency_verification completed successfully
    set /a passed_tests+=1
)

REM Test 2: Comprehensive Build Tests
echo.
echo [%time%] Running comprehensive_build...
set /a total_tests+=1

set docker_flag=
if "%SKIP_DOCKER%"=="true" set docker_flag=--skip-docker

python scripts/comprehensive_build_test_plan.py %verbose_flag% %docker_flag% --output "%OUTPUT_DIR%/build_report_%TIMESTAMP%.txt" > "%OUTPUT_DIR%/comprehensive_build_%TIMESTAMP%.log" 2>&1
if errorlevel 1 (
    echo [%time%] ❌ comprehensive_build failed
    if "%VERBOSE%"=="true" type "%OUTPUT_DIR%/comprehensive_build_%TIMESTAMP%.log"
) else (
    echo [%time%] ✅ comprehensive_build completed successfully
    set /a passed_tests+=1
)

REM Test 3: Cloud Run Emulation (if Docker available)
if "%SKIP_DOCKER%"=="false" (
    echo.
    echo [%time%] Running cloud_run_emulation...
    set /a total_tests+=1
    
    python scripts/cloud_run_emulator.py %verbose_flag% --service all > "%OUTPUT_DIR%/cloud_run_emulation_%TIMESTAMP%.log" 2>&1
    if errorlevel 1 (
        echo [%time%] ❌ cloud_run_emulation failed
        if "%VERBOSE%"=="true" type "%OUTPUT_DIR%/cloud_run_emulation_%TIMESTAMP%.log"
    ) else (
        echo [%time%] ✅ cloud_run_emulation completed successfully
        set /a passed_tests+=1
    )
)

REM Test 4: Integration Tests
echo.
echo [%time%] Running integration_tests...
set /a total_tests+=1

python -m pytest tests/integration/ -v --tb=short > "%OUTPUT_DIR%/integration_tests_%TIMESTAMP%.log" 2>&1
if errorlevel 1 (
    echo [%time%] ❌ integration_tests failed
    if "%VERBOSE%"=="true" type "%OUTPUT_DIR%/integration_tests_%TIMESTAMP%.log"
) else (
    echo [%time%] ✅ integration_tests completed successfully
    set /a passed_tests+=1
)

REM Test 5: E2E Tests
echo.
echo [%time%] Running e2e_tests...
set /a total_tests+=1

python -m pytest tests/e2e/ -v --tb=short > "%OUTPUT_DIR%/e2e_tests_%TIMESTAMP%.log" 2>&1
if errorlevel 1 (
    echo [%time%] ❌ e2e_tests failed
    if "%VERBOSE%"=="true" type "%OUTPUT_DIR%/e2e_tests_%TIMESTAMP%.log"
) else (
    echo [%time%] ✅ e2e_tests completed successfully
    set /a passed_tests+=1
)

REM Calculate success rate
set /a failed_tests=total_tests-passed_tests
set /a success_rate=passed_tests*100/total_tests

REM Generate final summary report
set summary_file=%OUTPUT_DIR%/summary_report_%TIMESTAMP%.txt

echo 🏗️ COMPREHENSIVE BUILD TEST BATTERY SUMMARY > "%summary_file%"
echo ========================================== >> "%summary_file%"
echo. >> "%summary_file%"
echo Execution Time: %date% %time% >> "%summary_file%"
echo Total Tests: %total_tests% >> "%summary_file%"
echo Passed: %passed_tests% >> "%summary_file%"
echo Failed: %failed_tests% >> "%summary_file%"
echo Success Rate: %success_rate%%% >> "%summary_file%"
echo. >> "%summary_file%"

if %passed_tests% equ %total_tests% (
    echo 🎉 BUILD READY: All tests passed! >> "%summary_file%"
    echo ✅ The codebase is ready for Cloud Run deployment. >> "%summary_file%"
) else (
    echo 🚨 BUILD NOT READY: %failed_tests% test(s) failed >> "%summary_file%"
    echo ⚠️ The Cloud Run deployment may fail. >> "%summary_file%"
)

REM Display summary
echo.
echo 📊 FINAL SUMMARY:
echo ==================
type "%summary_file%"

echo.
echo 📁 All test results saved to: %OUTPUT_DIR%
echo 📄 Summary report: %summary_file%

REM Exit with appropriate code
if %passed_tests% equ %total_tests% (
    exit /b 0
) else (
    exit /b 1
)

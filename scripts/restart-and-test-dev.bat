@echo off
REM Restart and Test Development Server Script
REM This script stops, rebuilds, and tests the development environment

echo 🔄 Restarting and Testing Development Server
echo ============================================

REM Step 1: Stop any running containers
echo [1/5] Stopping any running containers...
docker compose --profile local down
if %errorlevel% neq 0 (
    echo [WARNING] Some containers may not have been running
)

REM Step 2: Clean up any orphaned containers
echo [2/5] Cleaning up orphaned containers...
docker compose --profile local down --remove-orphans
if %errorlevel% neq 0 (
    echo [WARNING] No orphaned containers to clean up
)

REM Step 3: Rebuild and start services
echo [3/5] Rebuilding and starting services...
docker compose --profile local up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    exit /b 1
)

REM Step 4: Wait for services to start
echo [4/5] Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Step 5: Test the build and services
echo [5/5] Testing services...

REM Check if containers are running
echo [INFO] Checking container status...
docker compose --profile local ps

REM Test API health
echo [INFO] Testing API health...
set /a attempt=0
set /a max_attempts=10

:test_api_loop
if %attempt% geq %max_attempts% (
    echo [WARNING] API health check failed after %max_attempts% attempts
    goto :test_frontend
)

curl -s -f http://localhost:3001/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] API is healthy at http://localhost:3001
    goto :test_frontend
)

set /a attempt+=1
echo [INFO] Waiting for API... (attempt %attempt%/%max_attempts%)
timeout /t 3 /nobreak >nul
goto :test_api_loop

:test_frontend
REM Test frontend
echo [INFO] Testing frontend...
set /a attempt=0

:test_frontend_loop
if %attempt% geq %max_attempts% (
    echo [WARNING] Frontend health check failed after %max_attempts% attempts
    goto :test_build
)

curl -s -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend is accessible at http://localhost:3000
    goto :test_build
)

set /a attempt+=1
echo [INFO] Waiting for frontend... (attempt %attempt%/%max_attempts%)
timeout /t 3 /nobreak >nul
goto :test_frontend_loop

:test_build
REM Test Next.js build inside the frontend container
echo [INFO] Testing Next.js build in frontend container...
docker compose --profile local exec frontend-local npm run build
if %errorlevel% equ 0 (
    echo [SUCCESS] Next.js build completed successfully
) else (
    echo [ERROR] Next.js build failed
    echo [INFO] Showing build logs...
    docker compose --profile local logs frontend-local --tail=20
)

REM Show recent logs
echo [INFO] Showing recent logs...
docker compose --profile local logs --tail=10

echo.
echo ✅ Development server restart and test completed!
echo.
echo Services available at:
echo   - Frontend: http://localhost:3000
echo   - API: http://localhost:3001
echo   - API Docs: http://localhost:3001/docs
echo   - Celery Monitor: http://localhost:5555
echo.
echo To view logs: docker compose --profile local logs -f
echo To stop services: docker compose --profile local down

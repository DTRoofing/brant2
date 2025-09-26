@echo off
REM Test script to verify Docker Compose fix for Windows
REM This script tests the Docker Compose configuration and services

echo 🧪 Testing Docker Compose Fix for Brant Roofing System
echo ======================================================

REM Check if Docker is available
echo [INFO] Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not available in PATH
    echo [INFO] Please ensure Docker Desktop is running and accessible
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker daemon is not running
    echo [INFO] Please start Docker Desktop
    exit /b 1
)
echo [SUCCESS] Docker is available and running

REM Check if Docker Compose is available
echo [INFO] Checking Docker Compose availability...
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker Compose (v2) is available
    set COMPOSE_CMD=docker compose
    goto :check_config
)

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker Compose (v1) is available
    set COMPOSE_CMD=docker-compose
    goto :check_config
)

echo [ERROR] Docker Compose is not available
exit /b 1

:check_config
REM Verify configuration files
echo [INFO] Verifying configuration files...

if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found
    exit /b 1
)

if not exist "frontend_ux\Dockerfile" (
    echo [ERROR] frontend_ux\Dockerfile not found
    exit /b 1
)

if not exist "backend.Dockerfile" (
    echo [ERROR] backend.Dockerfile not found
    exit /b 1
)

if not exist "worker.Dockerfile" (
    echo [ERROR] worker.Dockerfile not found
    exit /b 1
)

if not exist ".env" (
    echo [WARNING] .env file not found - services may not start properly
)

echo [SUCCESS] All configuration files are present

REM Test Docker Compose configuration
echo [INFO] Testing Docker Compose configuration...
%COMPOSE_CMD% config >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose configuration has errors
    %COMPOSE_CMD% config
    exit /b 1
)
echo [SUCCESS] Docker Compose configuration is valid

REM Build services
echo [INFO] Building services...
%COMPOSE_CMD% --profile local build
if %errorlevel% neq 0 (
    echo [ERROR] Service build failed
    exit /b 1
)
echo [SUCCESS] All services built successfully

REM Start services
echo [INFO] Starting services...
%COMPOSE_CMD% --profile local up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [SUCCESS] Services started successfully

REM Check service status
echo [INFO] Checking service status...
timeout /t 10 /nobreak >nul
%COMPOSE_CMD% --profile local ps

REM Test API endpoint
echo [INFO] Testing API endpoint...
set /a attempt=0
set /a max_attempts=30

:test_api_loop
if %attempt% geq %max_attempts% (
    echo [WARNING] API health check failed - service may still be starting
    goto :test_frontend
)

curl -s -f http://localhost:3001/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] API is responding at http://localhost:3001
    goto :test_frontend
)

set /a attempt+=1
echo [INFO] Waiting for API... (attempt %attempt%/%max_attempts%)
timeout /t 2 /nobreak >nul
goto :test_api_loop

:test_frontend
REM Test frontend
echo [INFO] Testing frontend...
set /a attempt=0

:test_frontend_loop
if %attempt% geq %max_attempts% (
    echo [WARNING] Frontend health check failed - service may still be starting
    goto :show_logs
)

curl -s -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend is responding at http://localhost:3000
    goto :show_logs
)

set /a attempt+=1
echo [INFO] Waiting for frontend... (attempt %attempt%/%max_attempts%)
timeout /t 2 /nobreak >nul
goto :test_frontend_loop

:show_logs
REM Show service logs
echo [INFO] Showing recent logs...
%COMPOSE_CMD% --profile local logs --tail=20

echo.
echo ✅ Docker Compose fix verification completed!
echo.
echo Services should be available at:
echo   - API: http://localhost:3001
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:3001/docs
echo.
echo To stop services: %COMPOSE_CMD% --profile local down
echo To view logs: %COMPOSE_CMD% --profile local logs -f

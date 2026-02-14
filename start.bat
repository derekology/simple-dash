@echo off
REM Simple Dash - Docker Start Script for Windows

echo Starting Simple Dash...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is not available. Please install Docker Desktop.
    pause
    exit /b 1
)

REM Create .env from example if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo .env file created. You can edit it to customize settings.
)

REM Build and start the containers
echo Building Docker images...
docker compose build

echo Starting containers...
docker compose up -d

REM Wait for container to be ready
echo Waiting for container to be ready...
timeout /t 5 /nobreak >nul

REM Check container status
docker compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo Container failed to start. Check logs with: docker compose logs
    pause
    exit /b 1
) else (
    echo Simple Dash is running!
    echo.
    echo Access the application at: http://localhost:8000
    echo.
    echo Useful commands:
    echo   View logs:    docker compose logs -f
    echo   Stop:         docker compose down
    echo   Restart:      docker compose restart
    echo   Shell access: docker compose exec simpledash sh
    echo.
)

pause

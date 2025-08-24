@echo off
echo KRNL Onboarding System - Startup Script
echo ========================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: docker-compose is not installed. Please install Docker Compose.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating default .env file...
    (
        echo # Database Configuration
        echo POSTGRES_DB=krnl_onboarding
        echo POSTGRES_USER=krnl_user
        echo POSTGRES_PASSWORD=krnl_password_123
        echo DATABASE_URL=postgresql://krnl_user:krnl_password_123@postgres:5432/krnl_onboarding
        echo.
        echo # Redis Configuration
        echo REDIS_URL=redis://redis:6379
        echo.
        echo # Application Configuration
        echo ENVIRONMENT=development
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo.
        echo # Email Configuration ^(Optional - for notifications^)
        echo EMAIL_USER=your-email@gmail.com
        echo EMAIL_PASSWORD=your-app-password
        echo SMTP_SERVER=smtp.gmail.com
        echo SMTP_PORT=587
        echo EMAIL_NOTIFICATIONS=false
        echo.
        echo # Agent Timeouts ^(in seconds^)
        echo VALIDATOR_AGENT_TIMEOUT=30
        echo ACCOUNT_SETUP_AGENT_TIMEOUT=60
        echo SCHEDULER_AGENT_TIMEOUT=45
        echo NOTIFIER_AGENT_TIMEOUT=30
        echo.
        echo # Feature Flags
        echo GOOGLE_CALENDAR_ENABLED=false
        echo SLACK_NOTIFICATIONS=false
    ) > .env
    echo .env file created successfully.
)

echo.
echo Starting KRNL Onboarding System...
echo This may take a few minutes on first run to download Docker images.
echo.

REM Stop any existing containers
docker-compose down

REM Build and start services
docker-compose up --build -d

echo.
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check service health
echo Checking service health...

REM Check if backend is responding
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 0 (
    echo ✓ Backend API is running on http://localhost:8000
) else (
    echo ⚠ Backend API may still be starting up. Please wait a moment and check http://localhost:8000/health
)

REM Check if frontend is responding
curl -f http://localhost:3000 >nul 2>&1
if errorlevel 0 (
    echo ✓ Frontend is running on http://localhost:3000
) else (
    echo ⚠ Frontend may still be starting up. Please wait a moment and check http://localhost:3000
)

echo.
echo ========================================
echo KRNL Onboarding System Status:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo ========================================
echo.
echo Press any key to exit...
pause >nul
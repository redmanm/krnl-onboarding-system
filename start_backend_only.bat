@echo off
echo Starting KRNL Onboarding System (Backend Only)
echo ================================================

echo.
echo Stopping any existing containers...
docker-compose down

echo.
echo Starting backend services (without frontend)...
docker-compose up -d postgres redis backend validator-agent account-agent scheduler-agent notifier-agent

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Backend services are running!
echo.
echo API: http://localhost:8000
echo Health Check: http://localhost:8000/health
echo.
echo To start frontend separately, run:
echo   cd frontend
echo   npm install
echo   npm run dev
echo.
echo Frontend will be available at: http://localhost:3000
echo.
pause
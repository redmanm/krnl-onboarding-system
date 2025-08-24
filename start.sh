#!/bin/bash

echo "KRNL Onboarding System - Startup Script"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating default .env file..."
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_DB=krnl_onboarding
POSTGRES_USER=krnl_user
POSTGRES_PASSWORD=krnl_password_123
DATABASE_URL=postgresql://krnl_user:krnl_password_123@postgres:5432/krnl_onboarding

# Redis Configuration
REDIS_URL=redis://redis:6379

# Application Configuration
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here-change-in-production

# Email Configuration (Optional - for notifications)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_NOTIFICATIONS=false

# Agent Timeouts (in seconds)
VALIDATOR_AGENT_TIMEOUT=30
ACCOUNT_SETUP_AGENT_TIMEOUT=60
SCHEDULER_AGENT_TIMEOUT=45
NOTIFIER_AGENT_TIMEOUT=30

# Feature Flags
GOOGLE_CALENDAR_ENABLED=false
SLACK_NOTIFICATIONS=false
EOF
    echo ".env file created successfully."
fi

echo ""
echo "Starting KRNL Onboarding System..."
echo "This may take a few minutes on first run to download Docker images."
echo ""

# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up --build -d

echo ""
echo "Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."

# Check if backend is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend API is running on http://localhost:8000"
else
    echo "⚠ Backend API may still be starting up. Please wait a moment and check http://localhost:8000/health"
fi

# Check if frontend is responding
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend is running on http://localhost:3000"
else
    echo "⚠ Frontend may still be starting up. Please wait a moment and check http://localhost:3000"
fi

echo ""
echo "========================================"
echo "KRNL Onboarding System Status:"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "========================================"
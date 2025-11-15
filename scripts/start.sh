#!/bin/bash

# Job Hunter Bot - Startup Script

set -e

echo "🚀 Starting Job Hunter Bot"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/pyvenv.cfg" ] || [ requirements.txt -nt venv/pyvenv.cfg ]; then
    print_status "Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before running again."
    exit 1
fi

# Start the application
print_status "Starting Job Hunter Bot..."
echo ""
echo "🌐 API Documentation: http://localhost:8000/api/v1/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "📊 Metrics: http://localhost:8000/api/v1/health/metrics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
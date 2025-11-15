#!/bin/bash

# Job Hunter Bot - Test Runner Script

set -e

echo "🧪 Running Job Hunter Bot Tests"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Run linting
print_status "Running code quality checks..."
echo "  - Black formatting check..."
black --check app/ tests/ || {
    print_warning "Code formatting issues found. Run 'black app/ tests/' to fix."
}

echo "  - Import sorting check..."
isort --check-only app/ tests/ || {
    print_warning "Import sorting issues found. Run 'isort app/ tests/' to fix."
}

echo "  - Linting with flake8..."
flake8 app/ tests/ || {
    print_warning "Linting issues found."
}

echo "  - Type checking with mypy..."
mypy app/ || {
    print_warning "Type checking issues found."
}

# Run tests
print_status "Running test suite..."

# Unit tests
echo "  - Running unit tests..."
pytest tests/unit/ -v --cov=app --cov-report=term-missing

# Integration tests
echo "  - Running integration tests..."
pytest tests/integration/ -v --cov=app --cov-report=term-missing

# Generate coverage report
print_status "Generating coverage report..."
pytest --cov=app --cov-report=html --cov-report=term-missing

# Check coverage threshold
COVERAGE=$(pytest --cov=app --cov-report=term-missing --quiet | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
if (( $(echo "$COVERAGE >= 90" | bc -l) )); then
    print_status "Coverage: ${COVERAGE}% (✓ Above 90% threshold)"
else
    print_error "Coverage: ${COVERAGE}% (✗ Below 90% threshold)"
    exit 1
fi

print_status "All tests passed! 🎉"
print_status "Coverage report generated in htmlcov/index.html"
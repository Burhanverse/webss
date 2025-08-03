#!/bin/bash

# WebSS Run Script
echo "Starting WebSS - Website Screenshot API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default configuration."
fi

# Check command line arguments
MODE=${1:-"dev"}

case $MODE in
    "dev"|"development")
        echo "Starting in development mode..."
        echo "API will be available at: http://localhost:8000"
        echo "API documentation: http://localhost:8000/docs"
        echo "Press Ctrl+C to stop"
        echo ""
        cd src && python main.py
        ;;
    "prod"|"production")
        echo "Starting in production mode with Waitress..."
        echo "API will be available at: http://localhost:8000"
        echo "Press Ctrl+C to stop"
        echo ""
        cd src && python server.py
        ;;
    "test")
        echo "Running tests..."
        python -m pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 [dev|prod|test]"
        echo "  dev  - Start development server (default)"
        echo "  prod - Start production server with Waitress"
        echo "  test - Run test suite"
        exit 1
        ;;
esac

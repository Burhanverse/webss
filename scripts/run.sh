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

# Get host and port from environment or use defaults
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}

case $MODE in
    "dev"|"development")
        echo "Starting in development mode..."
        echo "API will be available at: http://$HOST:$PORT"
        echo "API documentation: http://$HOST:$PORT/docs"
        echo "Press Ctrl+C to stop"
        echo ""
        cd src && python3 main.py
        ;;
    "prod"|"production")
        echo "Starting in production mode with Waitress..."
        echo "API will be available at: http://$HOST:$PORT"
        echo "Press Ctrl+C to stop"
        echo ""
        cd src && python3 server.py
        ;;
    "test")
        echo "Running tests..."
        python3 -m pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 [dev|prod|test]"
        echo "  dev  - Start development server (default)"
        echo "  prod - Start production server with Waitress"
        echo "  test - Run test suite"
        echo ""
        echo "Environment variables:"
        echo "  HOST - Host to bind to (default: 0.0.0.0)"
        echo "  PORT - Port to bind to (default: 8000)"
        exit 1
        ;;
esac

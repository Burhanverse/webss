#!/bin/bash

# WebSS Setup Script
echo "Setting up WebSS - Website Screenshot API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; major, minor = sys.version_info[:2]; print(f'{major}.{minor}')")
required_version="3.8"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✓ Python $python_version found (>= $required_version)"
else
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Set permissions
chmod +x scripts/run.sh

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1
THREADS=6

# Environment
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=1

# Browser Configuration
BROWSER_HEADLESS=true
MAX_CONCURRENT_BROWSERS=5
EOL
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start development server: python src/main.py"
echo "3. Or start production server: python src/server.py"
echo "4. Test the API: python src/client.py https://example.com"
echo "5. Run tests: python -m pytest tests/ -v"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""

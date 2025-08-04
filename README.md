# WebSS - Website Screenshot API

A Python API for capturing website screenshots using Playwright. Built with FastAPI for high performance and reliability.

## 🚀 Live Demo

**Try it now**: [https://webss-latest.onrender.com](https://webss-latest.onrender.com)

- **API Documentation**: [https://webss-latest.onrender.com/docs](https://webss-latest.onrender.com/docs)
- **Health Check**: [https://webss-latest.onrender.com/health](https://webss-latest.onrender.com/health)

## ✨ Key Features

### Screenshot Capabilities
- **Multiple Output Formats**: PNG, JPEG, WebP with quality control
- **Flexible Output**: Base64 encoded strings or raw binary data
- **Full Page Screenshots**: Capture entire page content beyond viewport
- **Element-Specific Screenshots**: Target specific CSS selectors
- **Mobile Viewport Support**: Device simulation with touch and scale factor
- **Custom Viewport Sizes**: From 320x240 to 3840x2160 pixels

### Advanced Browser Control
- **Custom User Agents**: Simulate different browsers and devices
- **HTTP Headers**: Set custom headers for authentication or API keys
- **Cookie Management**: Set cookies for authenticated sessions
- **JavaScript Control**: Configurable JavaScript execution
- **Animation Disabling**: Speed up captures by disabling CSS animations
- **Network Timing**: Wait for network idle or custom delays with automatic 5-second minimum for heavy sites

### Performance & Security
- **Built-in Ad Blocking**: Block ads, trackers, and unnecessary resources
- **Rate Limiting**: Configurable request throttling (10 req/sec default)
- **Concurrent Control**: Manage multiple browser instances
- **Memory Optimization**: In-memory processing, no file storage
- **SSL Support**: Handle HTTPS errors gracefully
- **Timeout Management**: Configurable page load timeouts

### Production Features
- **FastAPI Framework**: High-performance async API with automatic OpenAPI docs
- **Structured Logging**: JSON-formatted logs with request tracing
- **Health Monitoring**: Detailed health checks including browser status
- **CORS Support**: Configurable cross-origin resource sharing
- **Environment Configuration**: Full .env support with validation
- **Docker Ready**: Multi-architecture container support
- **CI/CD Pipeline**: Automated builds and deployments

## Project Structure

```
webss/
├── src/
│   ├── main.py          # FastAPI application with screenshot endpoints
│   ├── server.py        # Production server with Uvicorn
│   ├── client.py        # Python client library (async & sync)
│   └── config.py        # Pydantic settings and configuration
├── tests/
│   └── test_api.py      # Comprehensive API test suite
├── scripts/
│   ├── setup.sh         # Environment setup and dependencies
│   ├── run.sh           # Development and production runners
│   └── healthcheck.sh   # Docker health check script
├── .github/
│   └── workflows/
│       └── docker-build.yml  # Automated CI/CD pipeline
├── requirements.txt     # Python dependencies
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Local development setup
├── docker-compose.ghcr.yml  # Production deployment setup
└── README.md           # Documentation
```

## Quick Start

### Option 1: Try the Live Demo

Test the API immediately without any setup:

```bash
# Basic screenshot
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "output_format": "base64"}'

# Advanced screenshot with mobile viewport
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://github.com",
    "width": 375,
    "height": 812,
    "mobile": true,
    "full_page": true,
    "format": "jpeg",
    "quality": 85,
    "block_ads": true
  }'
```

### Option 2: Local Development Setup

#### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/Burhanverse/webss.git
cd webss

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### 2. Start the Server

```bash
# Development mode with auto-reload
./scripts/run.sh dev

# Production mode with Uvicorn
./scripts/run.sh prod

# Run test suite
./scripts/run.sh test
```

#### 3. Test the Local API

```bash
# Using curl (live demo)
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "width": 1920,
    "height": 1080,
    "format": "png",
    "full_page": true,
    "output_format": "base64"
  }'

# Local development
curl -X POST 'http://localhost:8000/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "width": 1920,
    "height": 1080,
    "format": "png",
    "full_page": true,
    "output_format": "base64"
  }'

# Using the Python client
python src/client.py https://example.com
```

## API Reference

### Screenshot Endpoint
```http
POST /screenshot
```

**Request Parameters:**

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `url` | string | required | Valid HTTP/HTTPS URL | Target website to screenshot |
| `width` | integer | 1920 | 320-3840 | Viewport width in pixels |
| `height` | integer | 1080 | 240-2160 | Viewport height in pixels |
| `format` | string | "png" | png, jpeg, webp | Output image format |
| `quality` | integer | null | 1-100 | JPEG/WebP quality (JPEG only) |
| `full_page` | boolean | false | - | Capture full scrollable content |
| `delay` | integer | 0 | 0-30000 | Wait time in milliseconds before capture (minimum 5000ms applied for heavy sites) |
| `timeout` | integer | 30000 | 5000-120000 | Page load timeout in milliseconds |
| `user_agent` | string | null | - | Custom User-Agent header |
| `headers` | object | null | - | Custom HTTP headers |
| `cookies` | array | null | - | Browser cookies to set |
| `selector` | string | null | CSS selector | Screenshot specific element only |
| `mobile` | boolean | false | - | Enable mobile viewport simulation |
| `disable_animations` | boolean | true | - | Disable CSS animations for faster capture |
| `block_ads` | boolean | true | - | Block ads and tracking scripts |
| `output_format` | string | "base64" | base64, binary | Response format |

**Example Request:**
```json
{
  "url": "https://example.com",
  "width": 1920,
  "height": 1080,
  "format": "png",
  "quality": 80,
  "full_page": false,
  "delay": 1000,
  "timeout": 30000,
  "user_agent": "WebSS Bot 1.0",
  "headers": {"Authorization": "Bearer token"},
  "cookies": [{"name": "session", "value": "abc123", "domain": "example.com"}],
  "selector": ".main-content",
  "mobile": false,
  "disable_animations": true,
  "block_ads": true,
  "output_format": "base64"
}
```

**Base64 Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "size": {"width": 1920, "height": 1080},
  "format": "png",
  "timestamp": "2025-08-04T14:22:00.000Z",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Binary Response:**
- Returns raw image data with appropriate `Content-Type` header
- Suitable for direct display or file saving

### Health Check Endpoints
```http
GET /                         # Basic service status
GET /health                   # Detailed health with browser status
```

**Health Response:**
```json
{
  "status": "healthy",
  "browser": "healthy", 
  "timestamp": "2025-08-04T14:22:00.000Z",
  "version": "1.0.0"
}
```

## Configuration

### Environment Variables

The application uses Pydantic Settings for configuration management. Create a `.env` file:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1
THREADS=6

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000
MAX_CONCURRENT_BROWSERS=5

# Screenshot Defaults
DEFAULT_WIDTH=1920
DEFAULT_HEIGHT=1080
DEFAULT_FORMAT=png
MAX_SCREENSHOT_WIDTH=3840
MAX_SCREENSHOT_HEIGHT=2160
DEFAULT_DELAY=5000

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=1

# Security
MAX_REQUEST_TIMEOUT=120000
ALLOWED_ORIGINS=["*"]

# Waitress Server (Production)
BACKLOG=1024
CONNECTION_LIMIT=1000
```

### Browser Security Features

WebSS includes several security and performance optimizations:

**Blocked Resources:**
- Ad networks (Google Ads, DoubleClick, etc.)
- Social media trackers (Facebook, Twitter, LinkedIn)
- Analytics scripts (when `block_ads=true`)
- Unnecessary fonts and media files

**Browser Hardening:**
- Sandboxing enabled (`--no-sandbox` for containers)
- GPU acceleration disabled for stability
- Background process throttling
- Dev tools and extensions disabled

## Python Client Library

WebSS includes both asynchronous and synchronous Python clients for easy integration.

### Async Client (Recommended)

```python
import asyncio
from src.client import WebSSClient

async def capture_screenshots():
    async with WebSSClient("https://webss-latest.onrender.com") as client:
        # Health check
        health = await client.health_check()
        print(f"API Status: {health['status']}")
        
        # Basic screenshot
        result = await client.capture_screenshot(
            url="https://github.com",
            width=1920,
            height=1080,
            full_page=True,
            format="png"
        )
        
        if result['success']:
            print(f"Screenshot: {result['size']}")
            # result['data'] contains base64 image
        
        # Save directly to file
        success = await client.save_screenshot(
            url="https://example.com",
            filename="example.png",
            mobile=True,
            width=375,
            height=812
        )
        
        # Advanced options
        result = await client.capture_screenshot(
            url="https://dashboard.example.com",
            headers={"Authorization": "Bearer token"},
            cookies=[{"name": "session", "value": "abc123"}],
            selector=".main-dashboard",
            delay=2000,  # Wait 2 seconds
            block_ads=True
        )

# Run the async function
asyncio.run(capture_screenshots())
```

### Sync Client (Simple Usage)

```python
from src.client import WebSSClientSync

# Initialize client
client = WebSSClientSync("https://webss-latest.onrender.com")

# Health check
health = client.health_check()
print(f"Status: {health['status']}")

# Capture screenshot
result = client.capture_screenshot(
    url="https://news.ycombinator.com",
    width=1200,
    height=800,
    full_page=True
)

if result['success']:
    print(f"Captured {result['url']}")
    print(f"Size: {result['size']}")
    # Access base64 data: result['data']
```

### Client Features

- **Connection Management**: Automatic session handling
- **Error Handling**: Comprehensive exception handling
- **File Operations**: Direct save-to-file functionality
- **Flexible Configuration**: All API parameters supported
- **Type Hints**: Full typing support for better IDE integration

## Deployment Options

### 🌐 Cloud Platforms

#### Render (Current Live Demo)
**One-click deployment** with automatic HTTPS and global CDN:

1. **Fork this repository**
2. **Connect to Render**:
   - Visit [Render Dashboard](https://render.com)
   - Create new "Web Service"
   - Connect your GitHub fork
3. **Configure service**:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium --with-deps`
   - **Start Command**: `python src/server.py`
   - **Health Check Path**: `/health`
   - **Environment**: Add any custom environment variables
4. **Deploy**: Automatic deployment on git push

#### Other Cloud Platforms
Similar setup works on:
- **Railway**: Auto-detects Python, add Playwright install to build
- **Fly.io**: Use provided Dockerfile for deployment
- **Google Cloud Run**: Deploy container with Cloud Build
- **AWS App Runner**: Deploy from container or source code
- **DigitalOcean App Platform**: Connect GitHub and configure build commands

### 🐳 Docker Deployment

#### Quick Start with Pre-built Images
```bash
# Run latest stable version
docker run -p 8000:8000 ghcr.io/burhancodes/webss:latest

# Run with custom port
docker run -e PORT=3000 -p 3000:3000 ghcr.io/burhancodes/webss:latest
```

#### Docker Compose (Recommended)
```bash
# Production deployment with GHCR image
docker-compose -f docker-compose.ghcr.yml up -d

# Local development with build
docker-compose up -d
```

#### Available Docker Tags
- `ghcr.io/burhancodes/webss:latest` - Latest stable release

Multi-architecture support: `linux/amd64`, `linux/arm64`

### 🔧 Manual Deployment

For VPS or dedicated servers:

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv \
    wget curl git \
    libglib2.0-0 libnss3 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxdamage1

# Clone and setup
git clone https://github.com/Burhanverse/webss.git
cd webss
./scripts/setup.sh

# Run production server
./scripts/run.sh prod
```

### ⚙️ Automated CI/CD

The project includes GitHub Actions for:
- **Automated Testing**: Run test suite on PRs
- **Docker Building**: Multi-arch container builds
- **GHCR Publishing**: Auto-publish to GitHub Container Registry
- **Security Scanning**: Container vulnerability checks

**Workflow Triggers:**
- Push to `main` branch → Build and publish `:main` tag
- Create release tag → Build and publish `:latest` and version tags
- Pull requests → Test and build (no publish)

## Performance & Optimization

### Built-in Optimizations

1. **Smart Resource Blocking**: 
   - Blocks ads, trackers, and social media scripts
   - Reduces page load time by 40-60%
   - Configurable allow/block lists

2. **Browser Pool Management**:
   - Reuses browser instances across requests
   - Configurable concurrent browser limit
   - Automatic cleanup and memory management

3. **Network Optimization**:
   - Waits for `networkidle` before capture
   - Configurable timeouts and delays
   - HTTP/2 and compression support

4. **Memory Efficiency**:
   - In-memory image processing (no disk I/O)
   - Automatic browser context isolation
   - Garbage collection optimization

### Performance Tuning

```env
# Adjust based on your server resources
MAX_CONCURRENT_BROWSERS=5        # Memory usage: ~200MB per browser
RATE_LIMIT_REQUESTS=10          # Requests per second
RATE_LIMIT_PERIOD=1             # Time window

# Browser optimization
BROWSER_TIMEOUT=30000           # Page load timeout
DEFAULT_DELAY=0                 # Default wait before capture

# Server optimization  
WORKERS=1                       # Uvicorn workers (CPU cores)
THREADS=6                       # Connection handling threads
BACKLOG=1024                    # Connection queue size
```

### Monitoring & Debugging

#### Health Monitoring
```bash
# Basic health check
curl https://webss-latest.onrender.com/

# Detailed browser status
curl https://webss-latest.onrender.com/health
```

#### Debug Mode
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python src/server.py

# Test with verbose client
python src/client.py https://example.com
```

#### Common Performance Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| High memory usage | Too many concurrent browsers | Reduce `MAX_CONCURRENT_BROWSERS` |
| Slow screenshots | Large/complex pages | Enable `block_ads`, reduce viewport size |
| Timeout errors | Slow loading sites | Increase `timeout` parameter |
| Rate limiting | Too many requests | Adjust `RATE_LIMIT_REQUESTS` |

## Use Cases & Examples

### 1. Website Monitoring
```python
# Monitor website changes
async def monitor_website():
    async with WebSSClient() as client:
        result = await client.capture_screenshot(
            url="https://status.example.com",
            full_page=True,
            selector=".status-board"
        )
        # Compare with previous screenshot
```

### 2. Social Media Previews
```python
# Generate social media preview images
async def generate_preview():
    async with WebSSClient() as client:
        result = await client.capture_screenshot(
            url="https://blog.example.com/post/123",
            width=1200, height=630,  # Twitter/Facebook optimal
            selector=".post-preview",
            format="jpeg", quality=85
        )
```

### 3. Mobile Testing
```python
# Test responsive design
async def mobile_test():
    async with WebSSClient() as client:
        # iPhone viewport
        result = await client.capture_screenshot(
            url="https://app.example.com",
            width=375, height=812,
            mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"
        )
```

### 4. Authenticated Screenshots
```python
# Screenshot protected pages
async def auth_screenshot():
    async with WebSSClient() as client:
        result = await client.capture_screenshot(
            url="https://dashboard.example.com",
            headers={"Authorization": "Bearer YOUR_TOKEN"},
            cookies=[{
                "name": "session_id",
                "value": "abc123xyz",
                "domain": "dashboard.example.com"
            }]
        )
```

## Testing & Quality Assurance

### Test Suite
The project includes comprehensive tests covering:

```bash
# Run all tests
./scripts/run.sh test

# Run specific test categories
python -m pytest tests/test_api.py::TestScreenshotAPI::test_single_screenshot_basic -v
python -m pytest tests/test_api.py::TestScreenshotAPI::test_single_screenshot_binary -v
python -m pytest tests/test_api.py::TestScreenshotAPI::test_health_check -v
```

### Test Coverage
- ✅ Basic screenshot functionality
- ✅ Multiple output formats (PNG, JPEG, WebP)
- ✅ Binary and base64 responses
- ✅ Health check endpoints
- ✅ Error handling and validation
- ✅ Mobile viewport simulation
- ✅ Element-specific screenshots
- ✅ Custom headers and cookies

### API Validation
The API uses Pydantic for request/response validation:
- Automatic input validation
- Type checking and conversion
- Clear error messages
- OpenAPI schema generation

## Security Considerations

### Input Validation
- URL validation (HTTP/HTTPS only)
- Parameter range validation
- CSS selector sanitization
- Header and cookie validation

### Browser Security
- Sandboxed browser execution
- No file system access
- Blocked external downloads
- Disabled plugins and extensions

### Network Security
- HTTPS support with error handling
- Configurable CORS policies
- Request timeout limits
- Rate limiting protection

### Container Security
- Non-root user execution
- Minimal attack surface
- Regular base image updates
- Security scanning in CI/CD

## Troubleshooting

### Common Issues

#### Browser Initialization Errors
```bash
# Error: Browser executable not found
playwright install chromium --with-deps

# Error: Permission denied
chmod -R 755 /ms-playwright/
```

#### Memory Issues
```bash
# Reduce concurrent browsers
export MAX_CONCURRENT_BROWSERS=2

# Monitor memory usage
docker stats webss-api
```

#### Network Connectivity
```bash
# Test outbound connectivity
curl -I https://example.com

# Check DNS resolution
nslookup example.com
```

#### Container Issues
```bash
# Check container logs
docker logs webss-api

# Restart with fresh state
docker-compose down && docker-compose up -d
```

### Debug Logging

Enable detailed logging for troubleshooting:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env file
LOG_LEVEL=DEBUG

# View structured logs
tail -f logs/webss.log | jq '.'
```

### Health Monitoring

```bash
# Check basic health (live demo)
curl https://webss-latest.onrender.com/

# Check detailed health with browser status (live demo)  
curl https://webss-latest.onrender.com/health

# Local development
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Performance Debugging

Monitor key metrics:
- Response times per request
- Memory usage per browser instance
- Queue length for rate limiting
- Error rates and timeout frequency

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/webss.git
cd webss

# Create feature branch
git checkout -b feature/your-feature-name

# Setup development environment
./scripts/setup.sh

# Install additional dev dependencies
pip install black isort flake8 mypy
```

### Code Standards
- **Formatting**: Use `black` for code formatting
- **Imports**: Use `isort` for import sorting  
- **Linting**: Use `flake8` for style checking
- **Type Hints**: Use `mypy` for type checking
- **Testing**: Add tests for new features

### Contribution Process
1. **Fork** the repository
2. **Create** a feature branch
3. **Add** comprehensive tests
4. **Ensure** all tests pass: `./scripts/run.sh test`
5. **Format** code: `black src/ tests/`
6. **Submit** a pull request

### Areas for Contribution
- 🌍 Internationalization support
- 🔌 Plugin system for custom processing
- 📊 Metrics and monitoring endpoints
- 🚀 Performance optimizations
- 📝 Documentation improvements
- 🧪 Additional test coverage

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support & Community

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/Burhanverse/webss/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/Burhanverse/webss/discussions)
- **📚 Documentation**: [API Docs](https://webss-latest.onrender.com/docs)
- **🔍 Troubleshooting**: Check the troubleshooting section above

---

**Made with ❤️ by [Burhanverse](https://github.com/Burhanverse)**

*WebSS provides a modern solution for website screenshot automation with a focus on performance, reliability, and ease of use.*

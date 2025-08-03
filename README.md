# WebSS - Website Screenshot API

A robust Python API for capturing website screenshots using Playwright, similar to gowitness but with more features and flexibility.

## Features

- **Fast Screenshot Capture**: Powered by Playwright for reliable browser automation
- **Multiple Formats**: PNG, JPEG, WebP support with quality control
- **Mobile Support**: Mobile viewport simulation with device presets
- **Full Page Screenshots**: Capture entire page content beyond viewport
- **Element Screenshots**: Target specific CSS selectors
- **Advanced Options**: Custom headers, cookies, user agents, delays
- **Ad Blocking**: Built-in ad and tracker blocking
- **Rate Limiting**: Configurable rate limiting and concurrent request control
- **In-Memory Processing**: No file storage, direct data return (base64 or binary)
- **Production Ready**: Waitress WSGI server, structured logging, health checks
- **Docker Support**: Ready for containerization
- **Comprehensive API**: RESTful endpoints with OpenAPI documentation

## Project Structure

```
webss/
├── src/
│   ├── main.py          # Main FastAPI application
│   ├── server.py        # Production server with Waitress
│   ├── client.py        # Python client library
│   └── config.py        # Configuration settings
├── tests/
│   └── test_api.py      # API tests
├── scripts/
│   ├── setup.sh         # Setup script
│   └── run.sh           # Run script
├── requirements.txt     # Python dependencies (no version locking)
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # This file
```

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd webss

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Start the Server

```bash
# Development mode
./scripts/run.sh dev

# Production mode
./scripts/run.sh prod

# Run tests
./scripts/run.sh test
```

### 3. Test the API

```bash
# Using curl
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

## API Endpoints

### Single Screenshot
```http
POST /screenshot
```

**Request Body:**
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
  "user_agent": "Custom User Agent",
  "headers": {"Authorization": "Bearer token"},
  "cookies": [{"name": "session", "value": "abc123", "domain": "example.com"}],
  "selector": ".main-content",
  "mobile": false,
  "disable_animations": true,
  "block_ads": true,
  "output_format": "base64"
}
```

**Response (base64 format):**
```json
{
  "success": true,
  "url": "https://example.com",
  "size": {"width": 1920, "height": 1080},
  "format": "png",
  "timestamp": "2025-08-03T14:22:00.000Z",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Response (binary format):**
Returns raw image data with appropriate Content-Type header.

### Health Check
```http
GET /                         # Basic health status
GET /health                   # Detailed health check with browser status
```

## Configuration

### Environment Variables

Create a `.env` file:

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

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=1

# Browser Configuration
BROWSER_HEADLESS=true
MAX_CONCURRENT_BROWSERS=5
```

### Screenshot Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Target URL to screenshot |
| `width` | integer | 1920 | Viewport width (320-3840) |
| `height` | integer | 1080 | Viewport height (240-2160) |
| `format` | string | "png" | Image format (png/jpeg/webp) |
| `quality` | integer | null | JPEG quality (1-100) |
| `full_page` | boolean | false | Capture full page |
| `delay` | integer | 0 | Wait time in ms (0-30000) |
| `timeout` | integer | 30000 | Page load timeout (5000-120000) |
| `user_agent` | string | null | Custom user agent |
| `headers` | object | null | Custom HTTP headers |
| `cookies` | array | null | Cookies to set |
| `selector` | string | null | CSS selector for element screenshot |
| `mobile` | boolean | false | Use mobile viewport |
| `disable_animations` | boolean | true | Disable CSS animations |
| `block_ads` | boolean | true | Block ads and trackers |
| `output_format` | string | "base64" | Output format (base64/binary) |

## Python Client

### Async Client

```python
from src.client import WebSSClient

async def main():
    async with WebSSClient("http://localhost:8000") as client:
        # Single screenshot (base64)
        result = await client.capture_screenshot(
            url="https://example.com",
            width=1920,
            height=1080,
            full_page=True,
            output_format="base64"
        )
        
        if result['success']:
            print(f"Screenshot captured: {len(result['data'])} chars")
        
        # Save screenshot to file
        success = await client.save_screenshot(
            url="https://example.com",
            filename="screenshot.png",
            width=1920,
            height=1080
        )
        
        if success:
            print("Screenshot saved to file")
```

### Sync Client

```python
from src.client import WebSSClientSync

client = WebSSClientSync("http://localhost:8000")

# Single screenshot
result = client.capture_screenshot("https://example.com")
print(result)
```

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Build manually
docker build -t webss .
docker run -p 8000:8000 webss
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run production server
python src/server.py
```

## Performance Tips

1. **Rate Limiting**: Adjust `RATE_LIMIT_REQUESTS` based on your server capacity
2. **Concurrent Limits**: Set `MAX_CONCURRENT_BROWSERS` based on available memory
3. **Resource Blocking**: Enable `block_ads` to speed up page loads
4. **Timeouts**: Adjust timeouts based on target websites
5. **Memory Management**: No file storage means lower disk I/O but higher memory usage

## Key Differences from gowitness

| Feature | WebSS | gowitness |
|---------|-------|-----------|
| Language | Python | Go |
| Browser Engine | Chromium (Playwright) | Chromium (Chrome DevTools) |
| API | REST API | CLI + Web UI |
| Storage | In-memory only | File-based |
| Output Formats | Base64 + Binary | File only |
| Element Screenshots | ✅ | ❌ |
| Custom Headers/Cookies | ✅ | ✅ |
| Ad Blocking | ✅ | ❌ |
| Rate Limiting | ✅ | ❌ |
| Production Server | ✅ Waitress | ❌ |
| Docker Support | ✅ | ✅ |

## Troubleshooting

### Common Issues

1. **Browser crashes**: Increase memory or reduce concurrent browsers
2. **Timeout errors**: Increase timeout values for slow websites
3. **Memory issues**: Monitor memory usage as screenshots are processed in-memory
4. **Network errors**: Verify outbound internet connectivity

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/main.py
```

### Health Monitoring

```bash
# Check basic health
curl http://localhost:8000/

# Check detailed health with browser status
curl http://localhost:8000/health
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `/docs`

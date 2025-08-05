# WebSS API Documentation

Complete API reference and usage examples for WebSS Website Screenshot API.

## Endpoints

### Screenshot Endpoint
```http
POST /screenshot
```

Capture a website screenshot with various customization options.

### Health Check Endpoints
```http
GET /                         # Basic service status
GET /health                   # Detailed health with browser status
```

## Request Parameters

### Basic Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `url` | string | required | Valid HTTP/HTTPS URL | Website URL to screenshot |
| `width` | integer | 1920 | 320-3840 | Viewport width in pixels |
| `height` | integer | 1080 | 240-2160 | Viewport height in pixels |
| `format` | string | "png" | png, jpeg, webp | Image format |
| `quality` | integer | null | 1-100 | JPEG quality (JPEG only) |
| `full_page` | boolean | false | - | Capture entire scrollable page |
| `selector` | string | null | CSS selector | Screenshot specific element only |
| `mobile` | boolean | false | - | Mobile viewport simulation |
| `timeout` | integer | 30000 | 5000-120000 | Page load timeout (ms) |
| `delay` | integer | 0 | 0-30000 | Wait time before capture (ms) |
| `user_agent` | string | null | - | Custom User-Agent header |
| `headers` | object | null | - | Custom HTTP headers |
| `cookies` | array | null | - | Browser cookies to set |
| `disable_animations` | boolean | true | - | Disable CSS animations |
| `block_ads` | boolean | true | - | Block ads and tracking scripts |
| `block_images` | boolean | false | - | Block images (not recommended for screenshots) |
| `output_format` | string | "base64" | base64, binary | Response format |

### Heavy Site Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `smart_wait` | boolean | true | - | Enable intelligent content readiness detection |
| `aggressive_wait` | boolean | false | - | Extra patient retry strategies for heavy sites |
| `wait_for_network_idle` | boolean | true | - | Wait for network requests to finish |
| `extra_wait_time` | integer | 0 | 0-15000 | Additional wait time after page load (ms) |

## Request Examples

### Basic Screenshot
```json
{
  "url": "https://example.com"
}
```

### Advanced Screenshot
```json
{
  "url": "https://github.com",
  "width": 1920,
  "height": 1080,
  "format": "jpeg",
  "quality": 85,
  "full_page": true,
  "mobile": false,
  "block_ads": true,
  "disable_animations": true
}
```

### Heavy Site (YouTube, Facebook, Reddit)
```json
{
  "url": "https://www.youtube.com",
  "aggressive_wait": true,
  "smart_wait": true,
  "wait_for_network_idle": true,
  "timeout": 60000,
  "extra_wait_time": 5000,
  "block_ads": true
}
```

### Mobile Screenshot
```json
{
  "url": "https://github.com",
  "width": 375,
  "height": 812,
  "mobile": true,
  "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
}
```

### Element Screenshot
```json
{
  "url": "https://news.ycombinator.com",
  "selector": ".titleline",
  "width": 1200,
  "height": 800
}
```

### Authenticated Screenshot
```json
{
  "url": "https://dashboard.example.com",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  },
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123xyz",
      "domain": "dashboard.example.com"
    }
  ]
}
```

## Response Format

### Success Response (Base64)
```json
{
  "success": true,
  "url": "https://example.com",
  "size": {
    "width": 1920,
    "height": 1080
  },
  "format": "png",
  "timestamp": "2025-08-05T14:22:00.000Z",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### Success Response (Binary)
When `output_format: "binary"` is used, the response is raw image data with appropriate `Content-Type` header (e.g., `image/png`, `image/jpeg`).

### Error Response
```json
{
  "success": false,
  "url": "https://example.com",
  "size": {
    "width": 0,
    "height": 0
  },
  "format": "png",
  "timestamp": "2025-08-05T14:22:00.000Z",
  "error": "Page load timeout exceeded"
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "browser": "healthy",
  "timestamp": "2025-08-05T14:22:00.000Z",
  "version": "1.0.3"
}
```

## cURL Examples

### Basic Screenshot
```bash
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

### Heavy Site with Full Options
```bash
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.youtube.com",
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "quality": 85,
    "aggressive_wait": true,
    "smart_wait": true,
    "timeout": 60000,
    "extra_wait_time": 5000
  }'
```

### Binary Response
```bash
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://github.com",
    "output_format": "binary"
  }' \
  --output screenshot.png
```

### Mobile Screenshot
```bash
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://github.com",
    "width": 375,
    "height": 812,
    "mobile": true
  }'
```

## Python Client Examples

### Async Client (Recommended)
```python
import asyncio
from src.client import WebSSClient

async def main():
    async with WebSSClient("https://webss-latest.onrender.com") as client:
        # Basic screenshot
        result = await client.capture_screenshot(
            url="https://github.com",
            width=1920,
            height=1080
        )
        
        if result['success']:
            print(f"Screenshot captured: {result['size']}")
        
        # Heavy site screenshot
        result = await client.capture_screenshot(
            url="https://www.youtube.com",
            aggressive_wait=True,
            smart_wait=True,
            timeout=60000
        )
        
        # Save to file
        success = await client.save_screenshot(
            url="https://example.com",
            filename="example.png",
            width=1200,
            height=800
        )

asyncio.run(main())
```

### Synchronous Client
```python
from src.client import WebSSClientSync

client = WebSSClientSync("https://webss-latest.onrender.com")

# Basic screenshot
result = client.capture_screenshot(
    url="https://example.com",
    format="jpeg",
    quality=85
)

if result['success']:
    # Decode base64 data
    import base64
    image_data = base64.b64decode(result['data'])
    
    with open('screenshot.jpg', 'wb') as f:
        f.write(image_data)
```

## Error Handling

### Common Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| `Page load timeout exceeded` | Site took too long to load | Increase `timeout` parameter |
| `Element with selector 'X' not found` | CSS selector didn't match | Verify selector or remove it |
| `Failed to load URL: 404` | URL not accessible | Check URL validity |
| `Browser initialization failed` | Server browser issue | Retry request or check server status |

### Python Error Handling
```python
import asyncio
from src.client import WebSSClient

async def robust_screenshot():
    async with WebSSClient("https://webss-latest.onrender.com") as client:
        try:
            result = await client.capture_screenshot(
                url="https://heavy-site.com",
                aggressive_wait=True,
                timeout=60000
            )
            
            if not result['success']:
                print(f"Screenshot failed: {result.get('error')}")
                return None
                
            return result['data']
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
```

## Rate Limits

- **Default**: 5 requests per second
- **Concurrent**: 5 browser instances maximum
- **Timeout**: 120 seconds maximum per request

## Best Practices

### For Heavy Sites
1. Use `aggressive_wait: true`
2. Set `timeout: 60000` or higher
3. Enable `smart_wait` and `wait_for_network_idle`
4. Add `extra_wait_time: 5000-10000`
5. Keep `block_ads: true`

### For Performance
1. Use `block_ads: true` always
2. Set `disable_animations: true`
3. Use `format: "jpeg"` with quality for smaller files
4. Avoid `full_page: true` unless necessary
5. Use appropriate viewport sizes

### For Reliability
1. Implement retry logic in your code
2. Handle both success/error responses
3. Use reasonable timeouts
4. Monitor API health endpoint

## Environment Configuration

When running your own instance, configure these environment variables:

```env
# Server
PORT=8000
HOST=0.0.0.0

# Performance
DEFAULT_DELAY=8000
RATE_LIMIT_REQUESTS=5
MAX_CONCURRENT_BROWSERS=5

# Browser
BROWSER_TIMEOUT=30000
BROWSER_HEADLESS=true

# Logging
LOG_LEVEL=INFO
```

## Interactive API Documentation

For interactive testing and detailed schema documentation, visit:
- **Live API Docs**: [https://webss-latest.onrender.com/docs](https://webss-latest.onrender.com/docs)

The interactive docs allow you to:
- Test API endpoints directly in the browser
- See detailed request/response schemas
- Try different parameter combinations
- Download OpenAPI specifications

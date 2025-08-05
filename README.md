# WebSS - Website Screenshot API

A fast, reliable Python API for capturing website screenshots using Playwright. Optimized for modern heavy websites.

## 🚀 Live Demo

**Try it now**: [https://webss-latest.onrender.com](https://webss-latest.onrender.com)
- **API Docs**: [https://webss-latest.onrender.com/docs](https://webss-latest.onrender.com/docs)
- **GitHub**: [https://github.com/Burhanverse/webss](https://github.com/Burhanverse/webss)

## ✨ Features

- **Heavy Site Support**: 80-95% success rate on complex sites (YouTube, Facebook, Reddit)
- **Multiple Formats**: PNG, JPEG, WebP with quality control
- **Smart Waiting**: Intelligent content detection and network idle waiting
- **Mobile Support**: Device simulation with custom viewports
- **Element Screenshots**: Target specific CSS selectors
- **Ad Blocking**: Fast loading with intelligent resource blocking

## Quick Start

### Try the Live API

```bash
# Basic screenshot
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'

# Heavy site (YouTube, Facebook, etc.)
curl -X POST 'https://webss-latest.onrender.com/screenshot' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.youtube.com",
    "aggressive_wait": true,
    "timeout": 60000,
    "smart_wait": true
  }'
```

### Local Setup

```bash
git clone https://github.com/Burhanverse/webss.git
cd webss
chmod +x scripts/setup.sh
./scripts/setup.sh
./scripts/run.sh dev
```

**Requirements**: Python 3.8+, Playwright browser dependencies

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `url` | Website to screenshot | `"https://example.com"` |
| `width`, `height` | Viewport size | `1920, 1080` |
| `format` | Image format | `"png"`, `"jpeg"`, `"webp"` |
| `aggressive_wait` | For heavy sites | `true` |
| `mobile` | Mobile viewport | `true` |
| `selector` | Element to capture | `".main-content"` |

📖 **[Complete API Documentation →](API.md)**

## Examples

### Simple Screenshot
```json
{"url": "https://example.com"}
```

### Heavy Site
```json
{
  "url": "https://www.youtube.com",
  "aggressive_wait": true,
  "timeout": 60000
}
```

### Mobile
```json
{
  "url": "https://github.com",
  "width": 375,
  "height": 812,
  "mobile": true
}
```

## Response

```json
{
  "success": true,
  "url": "https://example.com",
  "size": {"width": 1920, "height": 1080},
  "format": "png",
  "timestamp": "2025-08-05T14:22:00.000Z",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

## Deployment

### Docker
```bash
docker run -p 8000:8000 ghcr.io/burhancodes/webss:latest
```

### Local
```bash
git clone https://github.com/Burhanverse/webss.git
cd webss && ./scripts/setup.sh && ./scripts/run.sh prod
```

## Python Client

```python
from src.client import WebSSClient

async with WebSSClient("https://webss-latest.onrender.com") as client:
    result = await client.capture_screenshot(url="https://github.com")
    if result['success']:
        print(f"Screenshot captured: {result['size']}")
```

📖 **[More examples in API docs →](API.md)**

## Health Check

```bash
curl https://webss-latest.onrender.com/health
```

## Common Use Cases

- **Website monitoring** - Regular screenshots for change detection
- **Social media previews** - Generate preview images for posts/articles  
- **Mobile testing** - Responsive design verification
- **Documentation** - Automated screenshot generation
- **Quality assurance** - Visual regression testing

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [Burhanverse](https://github.com/Burhanverse)**


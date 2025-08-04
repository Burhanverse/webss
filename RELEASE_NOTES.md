# WebSS Release Notes

## Version 1.0.1 - Heavy Site Optimization
*Released: August 4, 2025*

🚀 **Improved support for heavy sites with automatic delay optimization**

### 🆕 New Features
- **Automatic Delay for Heavy Sites**: Added 5-second minimum delay before screenshots to ensure sites like YouTube fully load
- **Smart Delay Logic**: Uses maximum of user-specified delay or default minimum (5000ms)
- **Enhanced Logging**: Detailed logging of applied delays for debugging
- **Configurable Default**: New `DEFAULT_DELAY` environment variable for customization

### 🔧 Technical Improvements
- Updated configuration system with new `default_delay` setting
- Enhanced delay application in both base64 and binary response paths
- Improved API documentation with delay behavior explanation
- Updated setup scripts and environment templates

---

## Version 1.0.0 - Initial Release
*Released: August 4, 2025*

🎉 **First stable release of WebSS - Website Screenshot API**

WebSS is a Python API for capturing website screenshots using Playwright, built with FastAPI for high performance and reliability.

### 🚀 Live Demo
- **API Base URL**: https://webss-latest.onrender.com
- **Interactive Documentation**: https://webss-latest.onrender.com/docs
- **Health Check**: https://webss-latest.onrender.com/health

---

## ✨ Key Features

### Screenshot Capabilities
- **Multiple Output Formats**: PNG, JPEG, WebP with quality control
- **Flexible Output**: Base64 encoded strings or raw binary data
- **Full Page Screenshots**: Capture entire page content beyond viewport
- **Element-Specific Screenshots**: Target specific CSS selectors
- **Mobile Viewport Support**: Device simulation with touch and scale factor
- **Custom Viewport Sizes**: Configurable from 320x240 to 3840x2160 pixels

### Advanced Browser Control
- **Custom User Agents**: Simulate different browsers and devices
- **HTTP Headers**: Set custom headers for authentication or API keys
- **Cookie Management**: Set cookies for authenticated sessions
- **JavaScript Control**: Configurable JavaScript execution
- **Animation Disabling**: Speed up captures by disabling CSS animations
- **Network Timing**: Wait for network idle or custom delays (0-30s)

### Performance & Security
- **Built-in Ad Blocking**: Block ads, trackers, and unnecessary resources
- **Rate Limiting**: Configurable request throttling (default: 10 req/sec)
- **Concurrent Control**: Manage multiple browser instances
- **Memory Optimization**: In-memory processing, no file storage
- **SSL Support**: Handle HTTPS errors gracefully
- **Timeout Management**: Configurable page load timeouts (5s-120s)

### Production Features
- **FastAPI Framework**: High-performance async API with automatic OpenAPI docs
- **Structured Logging**: JSON-formatted logs with request tracing
- **Health Monitoring**: Detailed health checks including browser status
- **CORS Support**: Configurable cross-origin resource sharing
- **Environment Configuration**: Full .env support with Pydantic validation
- **Docker Ready**: Multi-architecture container support (amd64/arm64)
- **CI/CD Pipeline**: Automated builds and deployments via GitHub Actions

---

## 🔧 Technical Specifications

### API Endpoints
- `POST /screenshot` - Capture website screenshots
- `GET /` - Basic health check
- `GET /health` - Detailed health check with browser status

### Supported Parameters
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `url` | string | required | HTTP/HTTPS | Target website URL |
| `width` | integer | 1920 | 320-3840 | Viewport width |
| `height` | integer | 1080 | 240-2160 | Viewport height |
| `format` | string | "png" | png/jpeg/webp | Image format |
| `quality` | integer | null | 1-100 | JPEG quality |
| `full_page` | boolean | false | - | Capture full page |
| `delay` | integer | 0 | 0-30000 | Wait time (ms) |
| `timeout` | integer | 30000 | 5000-120000 | Load timeout (ms) |
| `mobile` | boolean | false | - | Mobile simulation |
| `block_ads` | boolean | true | - | Block ads/trackers |
| `output_format` | string | "base64" | base64/binary | Response format |

### Browser Engine
- **Playwright**: Latest Chromium with full JavaScript support
- **Security**: Sandboxed execution, no file system access
- **Performance**: Optimized browser arguments for container environments

---

## 📦 Distribution

### Docker Images
- **Registry**: GitHub Container Registry (GHCR)
- **Base Image**: `ghcr.io/burhancodes/webss:latest`
- **Architectures**: linux/amd64, linux/arm64
- **Size**: ~800MB (includes Chromium browser)

### Python Package
- **Requirements**: Python 3.8+
- **Dependencies**: FastAPI, Playwright, Uvicorn, Pydantic, Pillow
- **Installation**: `pip install -r requirements.txt && playwright install chromium`

---

## 🚀 Deployment Options

### Cloud Platforms
- ✅ **Render** (Live demo deployment)
- ✅ **Railway** 
- ✅ **Fly.io**
- ✅ **Google Cloud Run**
- ✅ **AWS App Runner**
- ✅ **DigitalOcean App Platform**

### Container Orchestration
- ✅ **Docker Compose**
- ✅ **Kubernetes**
- ✅ **Docker Swarm**

### Local Development
- ✅ **Virtual Environment**
- ✅ **Development Scripts**
- ✅ **Auto-reload Support**

---

## 🧪 Testing & Quality

### Test Coverage
- ✅ Basic screenshot functionality
- ✅ Multiple output formats (PNG, JPEG, WebP)
- ✅ Binary and base64 responses
- ✅ Health check endpoints
- ✅ Error handling and validation
- ✅ Mobile viewport simulation
- ✅ Element-specific screenshots
- ✅ Custom headers and cookies

### Code Quality
- **Type Hints**: Full typing support with mypy
- **API Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Auto-generated OpenAPI/Swagger docs

---

## 🔒 Security Features

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

### Container Security
- Non-root user execution
- Minimal attack surface
- Regular security scanning in CI/CD

---

## 📖 Documentation & Support

### Resources
- **README**: Comprehensive setup and usage guide
- **API Docs**: Interactive Swagger/OpenAPI documentation
- **Python Client**: Both async and sync client libraries included
- **Examples**: Real-world use cases and code samples

### Support Channels
- **Issues**: [GitHub Issues](https://github.com/Burhanverse/webss/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Burhanverse/webss/discussions)
- **Documentation**: [Live API Docs](https://webss-latest.onrender.com/docs)

---

## 🛠️ Known Limitations

1. **Memory Usage**: ~200MB per concurrent browser instance
2. **Browser Startup**: Initial cold start may take 2-3 seconds
3. **Resource Blocking**: Ad blocking rules are predefined (not customizable)
4. **File Storage**: No persistent storage - all processing in-memory

---

## 🔮 Roadmap

### Planned Features
- 🌍 Internationalization support
- 🔌 Plugin system for custom processing
- 📊 Metrics and monitoring endpoints
- 🚀 Performance optimizations
- 📝 Enhanced documentation
- 🧪 Additional test coverage

---

## 🙏 Acknowledgments

- **Playwright Team**: For the excellent browser automation framework
- **FastAPI**: For the high-performance web framework
- **Render**: For hosting the live demo
- **Contributors**: All community members who provided feedback

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [Burhanverse](https://github.com/Burhanverse)**

*WebSS v1.0.0 provides a modern solution for website screenshot automation with a focus on performance, reliability, and ease of use.*

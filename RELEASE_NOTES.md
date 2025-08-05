# WebSS Release Notes

## Version 1.0.5 - Modular Architecture
*Released: August 5, 2025*

- Split main.py into focused modules in `src/core/` directory
- Enhanced image loading for YouTube and The Verge
- Added `block_images` parameter for better compatibility
- Improved code organization and maintainability

---

## Version 1.0.4 - Heavy Site Support
*Released: August 5, 2025*

- Smart waiting for heavy sites (YouTube, Facebook, Reddit)
- Added 4 new API parameters: `smart_wait`, `wait_for_network_idle`, `aggressive_wait`, `extra_wait_time`
- Framework detection for React/Angular/Vue
- Progressive retry system with 6 strategies
- Default delay increased to 8000ms

---

## Version 1.0.3 - Navigation Improvements
*Released: August 5, 2025*

- Multi-strategy navigation with 4 wait strategies
- Enhanced bot detection evasion
- Intelligent timeout management with retry logic
- Ultimate fallback navigation for problematic sites
- Improved error recovery and logging

---

## Version 1.0.2 - Performance & Reliability
*Released: August 4, 2025*

- Enhanced ad/tracker blocking with pattern-based filtering
- Fallback navigation strategy for timeout handling
- Facebook domain unblocked for social media content
- Improved error handling for slow websites

---

## Version 1.0.1 - Heavy Site Optimization
*Released: August 4, 2025*

- Automatic 5-second delay for heavy sites
- Smart delay logic with configurable defaults
- Enhanced logging and debugging
- Improved support for resource-intensive websites

---

## Version 1.0.0 - Initial Release
*Released: August 4, 2025*

First stable release of WebSS - Website Screenshot API built with FastAPI and Playwright.

### Key Features
- Multiple output formats (PNG, JPEG, WebP)
- Full page and element-specific screenshots
- Mobile viewport simulation
- Custom user agents and headers
- Built-in ad blocking and rate limiting
- Docker support with multi-architecture builds
- Live demo at https://webss-latest.onrender.com

### API Endpoints
- `POST /screenshot` - Capture website screenshots
- `GET /` - Basic health check
- `GET /health` - Detailed health check

### Supported Parameters
- URL, width, height, format, quality
- Full page, delay, timeout, mobile mode
- Block ads, custom output format
- Range validation and security features

Built with FastAPI, Playwright, and modern Python tooling.

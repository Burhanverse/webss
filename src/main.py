import asyncio
import logging
import base64
from typing import Optional, Dict, Any
from io import BytesIO
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field, field_validator
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from asyncio_throttle import Throttler
from datetime import datetime
from PIL import Image
from config import Settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize settings
settings = Settings()

# Pydantic models
class ScreenshotRequest(BaseModel):
    url: HttpUrl
    width: int = Field(default=1920, ge=320, le=3840, description="Viewport width")
    height: int = Field(default=1080, ge=240, le=2160, description="Viewport height")
    format: str = Field(default="png", pattern="^(png|jpeg|webp)$", description="Image format")
    quality: Optional[int] = Field(default=None, ge=1, le=100, description="JPEG quality (1-100)")
    full_page: bool = Field(default=False, description="Capture full page")
    delay: int = Field(default=0, ge=0, le=30000, description="Wait time in milliseconds (minimum 2000ms applied for heavy sites)")
    timeout: int = Field(default=30000, ge=5000, le=120000, description="Page load timeout")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Custom headers")
    cookies: Optional[list] = Field(default=None, description="Cookies to set")
    selector: Optional[str] = Field(default=None, description="CSS selector to screenshot specific element")
    mobile: bool = Field(default=False, description="Use mobile viewport")
    disable_animations: bool = Field(default=True, description="Disable CSS animations")
    block_ads: bool = Field(default=True, description="Block ads and tracking")
    output_format: str = Field(default="base64", pattern="^(base64|binary)$", description="Output format")
    wait_for_network_idle: bool = Field(default=True, description="Wait for network to be idle")
    smart_wait: bool = Field(default=True, description="Enable smart waiting for content readiness")
    aggressive_wait: bool = Field(default=False, description="Use aggressive waiting for very heavy sites")
    extra_wait_time: int = Field(default=0, ge=0, le=15000, description="Extra wait time after page load")

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, v, info):
        if v is not None and info.data.get('format') != 'jpeg':
            raise ValueError('Quality parameter only applies to JPEG format')
        return v

class ScreenshotResponse(BaseModel):
    success: bool
    url: str
    size: Dict[str, int]
    format: str
    timestamp: datetime
    data: Optional[str] = Field(default=None, description="Base64 encoded image data")
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="WebSS - Website Screenshot API",
    description="A robust Python API for capturing website screenshots using Playwright",
    version="1.0.4"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global browser instance and throttler
browser: Optional[Browser] = None
throttler = Throttler(rate_limit=settings.rate_limit_requests, period=settings.rate_limit_period)

class ScreenshotService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        
    async def init_browser(self):
        """Initialize Playwright browser with optimized settings for heavy sites"""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-web-security',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-blink-features=AutomationControlled',
                    '--no-default-browser-check',
                    '--disable-sync',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-component-update',
                    '--disable-client-side-phishing-detection',
                    '--disable-hang-monitor',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost',
                    '--disable-domain-reliability',
                    '--disable-component-extensions-with-background-pages',
                    # Additional args for heavy sites
                    '--memory-pressure-off',
                    '--disable-background-networking',
                    '--disable-breakpad',
                    '--disable-features=VizDisplayCompositor',
                    '--max_old_space_size=4096',
                    '--aggressive-cache-discard',
                    '--enable-features=NetworkService'
                ]
            )
            logger.info("Browser initialized with heavy site optimizations")
    
    async def create_context(self, request: ScreenshotRequest) -> BrowserContext:
        """Create browser context with custom settings optimized for heavy sites"""
        await self.init_browser()
        
        # Enhanced user agent for better compatibility
        default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        
        context_options = {
            "viewport": {
                "width": request.width,
                "height": request.height
            },
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "user_agent": request.user_agent or default_user_agent,
            # Enhanced context options for heavy sites
            "bypass_csp": True,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "geolocation": {"longitude": -74.0059, "latitude": 40.7128},
            "permissions": ["geolocation"],
        }
            
        if request.mobile:
            context_options.update({
                "is_mobile": True,
                "has_touch": True,
                "device_scale_factor": 2
            })
            
        context = await self.browser.new_context(**context_options)
        
        # Set extra headers with better defaults
        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        if request.headers:
            default_headers.update(request.headers)
        
        await context.set_extra_http_headers(default_headers)
            
        # Set cookies
        if request.cookies:
            await context.add_cookies(request.cookies)
            
        # Configure resource blocking based on request
        if request.block_ads:
            await context.route("**/*", self._smart_resource_handler)
            
        return context
    
    async def _navigate_with_retries(self, page: Page, url: str, timeout: int, request: ScreenshotRequest, context: str = "") -> Any:
        """Enhanced navigation with sophisticated retry logic for heavy sites"""
        
        # Progressive wait strategies - start conservative, get more aggressive
        wait_strategies = [
            {"wait_until": "domcontentloaded", "timeout_multiplier": 1.0, "extra_wait": 2000},
            {"wait_until": "networkidle", "timeout_multiplier": 1.2, "extra_wait": 3000},
            {"wait_until": "load", "timeout_multiplier": 1.0, "extra_wait": 4000},
            {"wait_until": "commit", "timeout_multiplier": 0.8, "extra_wait": 5000},
        ]
        
        # For aggressive wait mode, add more patient strategies
        if request.aggressive_wait:
            wait_strategies.extend([
                {"wait_until": "networkidle", "timeout_multiplier": 2.0, "extra_wait": 8000},
                {"wait_until": "domcontentloaded", "timeout_multiplier": 2.5, "extra_wait": 10000},
            ])
        
        max_retries = 3 if request.aggressive_wait else 2
        
        for attempt in range(max_retries):
            for strategy_idx, strategy in enumerate(wait_strategies):
                try:
                    # Calculate timeout for this attempt
                    base_timeout = timeout * strategy["timeout_multiplier"]
                    current_timeout = base_timeout if attempt == 0 else min(base_timeout * 0.7, 20000)
                    
                    logger.info(
                        f"{context}Navigation attempt",
                        url=url,
                        strategy=strategy["wait_until"],
                        attempt=attempt + 1,
                        strategy_index=strategy_idx + 1,
                        timeout=current_timeout,
                        aggressive_mode=request.aggressive_wait
                    )
                    
                    # Navigate with current strategy
                    response = await page.goto(
                        url,
                        timeout=current_timeout,
                        wait_until=strategy["wait_until"]
                    )
                    
                    # Additional wait after navigation
                    if strategy["extra_wait"] > 0:
                        await page.wait_for_timeout(strategy["extra_wait"])
                    
                    # Smart content readiness checks
                    if request.smart_wait:
                        await self._wait_for_content_readiness(page, url, context)
                    
                    # Network idle check for SPAs
                    if request.wait_for_network_idle and strategy["wait_until"] != "networkidle":
                        try:
                            await page.wait_for_load_state("networkidle", timeout=5000)
                            logger.info(f"{context}Network idle achieved", url=url)
                        except Exception as e:
                            logger.warning(f"{context}Network idle timeout (non-critical)", url=url, error=str(e))
                    
                    logger.info(
                        f"{context}Navigation successful",
                        url=url,
                        strategy=strategy["wait_until"],
                        attempt=attempt + 1,
                        status=response.status if response else "no_response"
                    )
                    return response
                    
                except Exception as e:
                    logger.warning(
                        f"{context}Navigation attempt failed",
                        url=url,
                        strategy=strategy["wait_until"],
                        attempt=attempt + 1,
                        strategy_index=strategy_idx + 1,
                        error=str(e)
                    )
                    
                    # Progressive delay between strategy attempts
                    await asyncio.sleep(min(1 + strategy_idx * 0.5, 3))
            
            # Delay between full retry attempts
            if attempt < max_retries - 1:
                retry_delay = 2 + attempt * 2
                logger.info(f"{context}Waiting before retry attempt", delay=retry_delay)
                await asyncio.sleep(retry_delay)
        
        # Final desperate fallback - minimal requirements
        try:
            logger.info(f"{context}Final fallback: minimal navigation", url=url)
            response = await page.goto(url, timeout=15000, wait_until="commit")
            
            # Give it a reasonable chance to load content
            await page.wait_for_timeout(8000)
            
            # Try one more smart wait
            if request.smart_wait:
                try:
                    await self._wait_for_content_readiness(page, url, context, timeout=10000)
                except:
                    pass
            
            logger.info(f"{context}Final fallback succeeded", url=url)
            return response
            
        except Exception as e:
            logger.error(
                f"{context}All navigation attempts failed including fallback",
                url=url,
                error=str(e),
                total_attempts=max_retries * len(wait_strategies) + 1
            )
            raise e
    
    async def _wait_for_content_readiness(self, page: Page, url: str, context: str, timeout: int = 8000):
        """Smart waiting for content readiness indicators"""
        try:
            # Wait for common indicators that content is ready
            ready_indicators = [
                "document.readyState === 'complete'",
                "window.jQuery && jQuery.active === 0",  # jQuery
                "!window.angular || window.getAllAngularTestabilities().findIndex(x=>!x.isStable()) === -1",  # Angular
                "!window.React || window.React",  # React presence
                "!window.Vue || window.Vue"  # Vue presence
            ]
            
            # Custom content readiness check
            check_script = f"""
                () => {{
                    // Basic readiness
                    if (document.readyState !== 'complete') return false;
                    
                    // Check for common loading indicators
                    const loadingSelectors = [
                        '[class*="loading"]', '[class*="spinner"]', '[class*="loader"]',
                        '.loading', '.spinner', '.loader', '#loading', '#spinner',
                        '[data-loading="true"]', '[aria-busy="true"]'
                    ];
                    
                    for (const selector of loadingSelectors) {{
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {{
                            if (el.offsetParent !== null) return false; // visible loading indicator
                        }}
                    }}
                    
                    // Check if major frameworks are done
                    if (window.jQuery && window.jQuery.active > 0) return false;
                    
                    // Look for signs of dynamic content loading
                    const images = document.querySelectorAll('img[src]');
                    let loadedImages = 0;
                    images.forEach(img => {{
                        if (img.complete) loadedImages++;
                    }});
                    
                    // If more than 80% of images are loaded, consider ready
                    if (images.length > 0 && loadedImages / images.length < 0.8) return false;
                    
                    return true;
                }}
            """
            
            # Wait for content to be ready
            await page.wait_for_function(check_script, timeout=timeout)
            logger.info(f"{context}Content readiness achieved", url=url)
            
        except Exception as e:
            # Non-critical failure
            logger.info(f"{context}Content readiness check timeout (continuing)", url=url, error=str(e))
    
    async def _smart_resource_handler(self, route, request):
        """Smart resource blocking that preserves functionality while improving performance"""
        url = request.url.lower()
        resource_type = request.resource_type
        
        # Critical domains to block (ads, analytics, trackers)
        blocked_domains = {
            'googletagmanager.com', 'google-analytics.com', 'googlesyndication.com',
            'doubleclick.net', 'outbrain.com', 'taboola.com', 'amazon-adsystem.com',
            'scorecardresearch.com', 'quantserve.com', 'chartbeat.com', 'parsely.com',
            'krxd.net', 'adsystem.com', 'ads.yahoo.com', 'advertising.com',
            'facebook.com/tr', 'connect.facebook.net', 'analytics.twitter.com',
            'hotjar.com', 'fullstory.com', 'mouseflow.com', 'crazyegg.com',
            'optimizely.com', 'mixpanel.com', 'segment.com', 'amplitude.com'
        }
        
        # Block known problematic patterns
        blocked_patterns = [
            'analytics', 'tracking', 'advertisement', 'ads.', '/ads/', 
            'doubleclick', 'googlesyndication', 'googleadservices',
            'facebook.com/tr', 'twitter.com/i/adsct', 'linkedin.com/li',
            'tiktok.com/i18n/pixel', 'snapchat.com/p'
        ]
        
        # Always block these resource types (non-essential for screenshots)
        always_block_types = {'other'}
        
        # Conditionally block these (only if they match ad patterns)
        conditional_block_types = {'font', 'media', 'image'}
        
        # Check for blocked domains
        if any(domain in url for domain in blocked_domains):
            await route.abort()
            return
            
        # Check for blocked patterns
        if any(pattern in url for pattern in blocked_patterns):
            await route.abort()
            return
            
        # Block always-blocked types
        if resource_type in always_block_types:
            await route.abort()
            return
            
        # For media/fonts/images, only block if they're from ad-related URLs
        if resource_type in conditional_block_types:
            # Allow if it's from the main domain or CDN
            try:
                from urllib.parse import urlparse
                request_domain = urlparse(request.url).netloc
                page_domain = urlparse(route.request.frame.url).netloc
                
                # Allow same domain or common CDNs
                allowed_domains = {
                    page_domain,
                    f"cdn.{page_domain}",
                    f"static.{page_domain}",
                    'cdn.jsdelivr.net', 'unpkg.com', 'cdnjs.cloudflare.com',
                    'fonts.googleapis.com', 'fonts.gstatic.com',
                    'ajax.googleapis.com', 'code.jquery.com'
                }
                
                if not any(allowed in request_domain for allowed in allowed_domains):
                    # Block media from unknown domains that might be ads
                    if any(ad_indicator in url for ad_indicator in ['ad', 'ads', 'banner', 'popup']):
                        await route.abort()
                        return
                        
            except Exception:
                # If parsing fails, allow the request
                pass
            
        # Allow everything else
        await route.continue_()
    
    async def capture_screenshot(self, request: ScreenshotRequest) -> ScreenshotResponse:
        """Enhanced screenshot capture with robust handling for heavy sites"""
        start_time = datetime.now()
        context = None
        page = None
        
        try:
            async with throttler:
                context = await self.create_context(request)
                page = await context.new_page()
                
                # Enhanced page setup
                await self._setup_page_for_heavy_sites(page, request)
                
                # Navigate with enhanced retry logic
                response = await self._navigate_with_retries(
                    page, 
                    str(request.url), 
                    request.timeout,
                    request,
                    ""
                )
                
                if not response or response.status >= 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to load URL: {response.status if response else 'No response'}"
                    )
                
                # Smart delay calculation
                effective_delay = await self._calculate_smart_delay(page, request)
                if effective_delay > 0:
                    logger.info(
                        "Applying smart delay",
                        url=str(request.url),
                        delay=effective_delay,
                        user_delay=request.delay,
                        default_delay=settings.default_delay,
                        extra_wait=request.extra_wait_time
                    )
                    await page.wait_for_timeout(effective_delay)
                
                # Final content readiness check
                await self._final_content_check(page, request)
                
                # Prepare screenshot options
                screenshot_options = {
                    "type": request.format,
                    "full_page": request.full_page
                }
                
                if request.format == "jpeg" and request.quality:
                    screenshot_options["quality"] = request.quality
                
                # Take screenshot with retry logic
                screenshot_bytes = await self._take_screenshot_with_retry(
                    page, request, screenshot_options
                )
                
                # Get image dimensions
                with Image.open(BytesIO(screenshot_bytes)) as img:
                    size = {"width": img.width, "height": img.height}
                
                # Prepare response data
                response_data = None
                if request.output_format == "base64":
                    response_data = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                logger.info(
                    "Screenshot captured successfully",
                    url=str(request.url),
                    duration=(datetime.now() - start_time).total_seconds(),
                    size=size,
                    aggressive_mode=request.aggressive_wait,
                    smart_wait=request.smart_wait
                )
                
                return ScreenshotResponse(
                    success=True,
                    url=str(request.url),
                    size=size,
                    format=request.format,
                    timestamp=datetime.now(),
                    data=response_data
                )
                
        except Exception as e:
            logger.error(
                "Screenshot capture failed",
                url=str(request.url),
                error=str(e),
                duration=(datetime.now() - start_time).total_seconds(),
                aggressive_mode=getattr(request, 'aggressive_wait', False)
            )
            
            return ScreenshotResponse(
                success=False,
                url=str(request.url),
                size={"width": 0, "height": 0},
                format=request.format,
                timestamp=datetime.now(),
                error=str(e)
            )
            
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
    
    async def _setup_page_for_heavy_sites(self, page: Page, request: ScreenshotRequest):
        """Setup page with optimizations for heavy sites"""
        
        # Enhanced animation disabling
        if request.disable_animations:
            await page.add_style_tag(content="""
                *, *::before, *::after {
                    animation-duration: 0.001s !important;
                    animation-delay: 0s !important;
                    transition-duration: 0.001s !important;
                    transition-delay: 0s !important;
                    scroll-behavior: auto !important;
                }
                
                /* Disable common loading animations */
                .loading, .loader, .spinner, [class*="loading"], [class*="spinner"] {
                    animation: none !important;
                    opacity: 0 !important;
                }
                
                /* Speed up fade-ins */
                [class*="fade"], [class*="slide"] {
                    transition: opacity 0.001s !important;
                    opacity: 1 !important;
                }
            """)
        
        # Add console error monitoring for debugging
        page.on("console", lambda msg: 
            logger.warning("Console error", message=msg.text) 
            if msg.type == "error" else None
        )
        
        # Handle page errors
        page.on("pageerror", lambda error: 
            logger.warning("Page error", error=str(error))
        )
    
    async def _calculate_smart_delay(self, page: Page, request: ScreenshotRequest) -> int:
        """Calculate smart delay based on page characteristics and user preferences"""
        
        # Base delay calculation
        base_delay = max(request.delay, settings.default_delay)
        
        # Check page complexity if smart_wait is enabled
        if request.smart_wait:
            try:
                # Analyze page complexity
                complexity_script = """
                    () => {
                        const metrics = {
                            scriptCount: document.querySelectorAll('script').length,
                            styleCount: document.querySelectorAll('link[rel="stylesheet"], style').length,
                            imageCount: document.querySelectorAll('img').length,
                            iframeCount: document.querySelectorAll('iframe').length,
                            hasReact: !!window.React,
                            hasAngular: !!window.angular || !!window.ng,
                            hasVue: !!window.Vue,
                            hasJQuery: !!window.jQuery,
                            domNodes: document.querySelectorAll('*').length
                        };
                        
                        // Calculate complexity score
                        let score = 0;
                        score += Math.min(metrics.scriptCount * 0.5, 20);
                        score += Math.min(metrics.styleCount * 0.3, 10);
                        score += Math.min(metrics.imageCount * 0.1, 10);
                        score += metrics.iframeCount * 2;
                        score += (metrics.hasReact || metrics.hasAngular || metrics.hasVue) ? 15 : 0;
                        score += Math.min(metrics.domNodes * 0.01, 15);
                        
                        return { metrics, score };
                    }
                """
                
                result = await page.evaluate(complexity_script)
                complexity_score = result.get('score', 0)
                
                # Adjust delay based on complexity
                if complexity_score > 50:  # Very complex site
                    base_delay = max(base_delay, 8000)
                elif complexity_score > 30:  # Moderately complex
                    base_delay = max(base_delay, 5000)
                elif complexity_score > 15:  # Somewhat complex
                    base_delay = max(base_delay, 3000)
                
                logger.info(
                    "Page complexity analysis",
                    url=str(request.url),
                    complexity_score=complexity_score,
                    metrics=result.get('metrics', {}),
                    calculated_delay=base_delay
                )
                
            except Exception as e:
                logger.warning("Complexity analysis failed", error=str(e))
        
        # Add extra wait time if specified
        total_delay = base_delay + request.extra_wait_time
        
        # Cap the maximum delay
        return min(total_delay, 30000)
    
    async def _final_content_check(self, page: Page, request: ScreenshotRequest):
        """Final check to ensure content is ready for screenshot"""
        
        if not request.smart_wait:
            return
        
        try:
            # Wait for images to load
            await page.wait_for_function("""
                () => {
                    const images = Array.from(document.images);
                    return images.length === 0 || images.every(img => img.complete);
                }
            """, timeout=5000)
            
            # Check for lazy loading completion
            await page.wait_for_function("""
                () => {
                    // Check for common lazy loading indicators
                    const lazyElements = document.querySelectorAll(
                        '[data-src], [loading="lazy"], .lazy, .lazyload, .lazyloading'
                    );
                    
                    for (const el of lazyElements) {
                        if (el.classList.contains('lazyloading')) return false;
                        if (el.hasAttribute('data-src') && !el.src) return false;
                    }
                    
                    return true;
                }
            """, timeout=3000)
            
        except Exception as e:
            # Non-critical failures
            logger.info("Final content check timeout (non-critical)", error=str(e))
    
    async def _take_screenshot_with_retry(self, page: Page, request: ScreenshotRequest, options: dict) -> bytes:
        """Take screenshot with retry logic"""
        
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                if request.selector:
                    element = await page.query_selector(request.selector)
                    if not element:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Element with selector '{request.selector}' not found"
                        )
                    screenshot_bytes = await element.screenshot(**options)
                else:
                    screenshot_bytes = await page.screenshot(**options)
                
                return screenshot_bytes
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                    
                logger.warning(
                    f"Screenshot attempt {attempt + 1} failed, retrying",
                    error=str(e)
                )
                await asyncio.sleep(1 + attempt)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

# Initialize service
screenshot_service = ScreenshotService()

@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup"""
    await screenshot_service.init_browser()
    logger.info("WebSS API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await screenshot_service.cleanup()
    logger.info("WebSS API shut down")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "WebSS - Website Screenshot API",
        "version": "1.0.4",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/screenshot", response_model=ScreenshotResponse)
async def capture_screenshot(request: ScreenshotRequest):
    """Capture a website screenshot"""
    try:
        result = await screenshot_service.capture_screenshot(request)
        
        # If binary output is requested, return raw image data
        if request.output_format == "binary" and result.success:
            # We need to recreate the screenshot for binary response
            # This is a simplified approach - in production you might want to optimize this
            context = None
            page = None
            try:
                context = await screenshot_service.create_context(request)
                page = await context.new_page()
                
                # Enhanced page setup for binary mode
                await screenshot_service._setup_page_for_heavy_sites(page, request)
                
                # Navigate with enhanced retry logic
                response = await screenshot_service._navigate_with_retries(
                    page,
                    str(request.url),
                    request.timeout,
                    request,
                    "Binary mode: "
                )
                
                # Smart delay calculation and application
                effective_delay = await screenshot_service._calculate_smart_delay(page, request)
                if effective_delay > 0:
                    await page.wait_for_timeout(effective_delay)
                
                # Final content readiness check
                await screenshot_service._final_content_check(page, request)
                
                screenshot_options = {"type": request.format, "full_page": request.full_page}
                if request.format == "jpeg" and request.quality:
                    screenshot_options["quality"] = request.quality
                
                if request.selector:
                    element = await page.query_selector(request.selector)
                    if element:
                        screenshot_bytes = await element.screenshot(**screenshot_options)
                    else:
                        raise HTTPException(status_code=400, detail="Element not found")
                else:
                    screenshot_bytes = await page.screenshot(**screenshot_options)
                
                media_type = f"image/{request.format}"
                return Response(content=screenshot_bytes, media_type=media_type)
                
            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()
        
        return result
        
    except Exception as e:
        logger.error("Screenshot endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test browser initialization
        await screenshot_service.init_browser()
        browser_status = "healthy" if screenshot_service.browser else "unhealthy"
        
        return {
            "status": "healthy",
            "browser": browser_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.4"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )

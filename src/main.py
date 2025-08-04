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
    version="1.0.3"
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
throttler = Throttler(rate_limit=10, period=1)

class ScreenshotService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        
    async def init_browser(self):
        """Initialize Playwright browser"""
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
                    '--disable-component-extensions-with-background-pages'
                ]
            )
            logger.info("Browser initialized")
    
    async def create_context(self, request: ScreenshotRequest) -> BrowserContext:
        """Create browser context with custom settings"""
        await self.init_browser()
        
        context_options = {
            "viewport": {
                "width": request.width,
                "height": request.height
            },
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }
        
        if request.user_agent:
            context_options["user_agent"] = request.user_agent
            
        if request.mobile:
            context_options.update({
                "is_mobile": True,
                "has_touch": True,
                "device_scale_factor": 2
            })
            
        context = await self.browser.new_context(**context_options)
        
        # Set extra headers
        if request.headers:
            await context.set_extra_http_headers(request.headers)
            
        # Set cookies
        if request.cookies:
            await context.add_cookies(request.cookies)
            
        # Block ads and tracking if requested
        if request.block_ads:
            await context.route("**/*", self._block_resource_handler)
            
        return context
    
    async def _navigate_with_retries(self, page: Page, url: str, timeout: int, context: str = "") -> Any:
        """Navigate to URL with multiple strategies and retry logic"""
        wait_strategies = ["networkidle", "domcontentloaded", "load", "commit"]
        max_retries = 2
        
        for attempt in range(max_retries):
            for strategy in wait_strategies:
                try:
                    # Use shorter timeout for retries to fail faster
                    current_timeout = timeout if attempt == 0 else min(timeout // 2, 15000)
                    
                    logger.info(
                        f"{context}Attempting page load",
                        url=url,
                        strategy=strategy,
                        attempt=attempt + 1,
                        timeout=current_timeout
                    )
                    
                    response = await page.goto(
                        url,
                        timeout=current_timeout,
                        wait_until=strategy
                    )
                    
                    logger.info(
                        f"{context}Page loaded successfully",
                        url=url,
                        strategy=strategy,
                        attempt=attempt + 1
                    )
                    return response
                    
                except Exception as e:
                    logger.warning(
                        f"{context}Strategy '{strategy}' failed",
                        url=url,
                        strategy=strategy,
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    
                    # Short delay between strategy attempts
                    await asyncio.sleep(1)
        
        # Final fallback: try with no wait condition and very short timeout
        try:
            logger.info(f"{context}Final fallback: attempting with no wait condition", url=url)
            response = await page.goto(url, timeout=10000)  # 10 second timeout, no wait condition
            logger.info(f"{context}Final fallback succeeded", url=url)
            return response
        except Exception as e:
            logger.error(
                f"{context}All navigation attempts failed including final fallback",
                url=url,
                error=str(e)
            )
            raise e
    
    async def _block_resource_handler(self, route, request):
        """Block ads, trackers, and unnecessary resources"""
        blocked_domains = {
            'googletagmanager.com', 'google-analytics.com', 'googlesyndication.com',
            'doubleclick.net', 'outbrain.com', 'taboola.com', 'amazon-adsystem.com',
            'scorecardresearch.com', 'quantserve.com', 'chartbeat.com', 'parsely.com',
            'krxd.net', 'adsystem.com', 'ads.yahoo.com', 'advertising.com',
            'bing.com/maps', 'hotjar.com', 'fullstory.com', 'mouseflow.com'
        }
        
        # More aggressive blocking for better performance
        blocked_types = {'font', 'media', 'other'}
        
        url = request.url
        resource_type = request.resource_type
        
        # Block known ad/tracking domains
        if any(domain in url for domain in blocked_domains):
            await route.abort()
            return
            
        # Block certain resource types for faster loading
        if resource_type in blocked_types:
            await route.abort()
            return
            
        # Block specific problematic patterns
        if any(pattern in url.lower() for pattern in ['analytics', 'tracking', 'advertisement', 'doubleclick']):
            await route.abort()
            return
            
        await route.continue_()
    
    async def capture_screenshot(self, request: ScreenshotRequest) -> ScreenshotResponse:
        """Capture screenshot and return data directly"""
        start_time = datetime.now()
        context = None
        page = None
        
        try:
            async with throttler:
                context = await self.create_context(request)
                page = await context.new_page()
                
                # Disable animations if requested
                if request.disable_animations:
                    await page.add_style_tag(content="""
                        *, *::before, *::after {
                            animation-duration: 0s !important;
                            animation-delay: 0s !important;
                            transition-duration: 0s !important;
                            transition-delay: 0s !important;
                        }
                    """)
                
                # Navigate to URL with multiple fallback strategies and retries
                response = await self._navigate_with_retries(
                    page, 
                    str(request.url), 
                    request.timeout,
                    ""
                )
                
                if not response or response.status >= 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to load URL: {response.status if response else 'No response'}"
                    )
                
                # Apply delay - use either user-specified delay or default minimum delay
                # This ensures heavy sites like YouTube have time to fully load
                effective_delay = max(request.delay, settings.default_delay)
                if effective_delay > 0:
                    logger.info(
                        "Applying delay before screenshot",
                        url=str(request.url),
                        delay=effective_delay,
                        user_delay=request.delay,
                        default_delay=settings.default_delay
                    )
                    await page.wait_for_timeout(effective_delay)
                
                # Prepare screenshot options
                screenshot_options = {
                    "type": request.format,
                    "full_page": request.full_page
                }
                
                if request.format == "jpeg" and request.quality:
                    screenshot_options["quality"] = request.quality
                
                # Take screenshot of specific element or full page
                if request.selector:
                    element = await page.query_selector(request.selector)
                    if not element:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Element with selector '{request.selector}' not found"
                        )
                    screenshot_bytes = await element.screenshot(**screenshot_options)
                else:
                    screenshot_bytes = await page.screenshot(**screenshot_options)
                
                # Get image dimensions
                with Image.open(BytesIO(screenshot_bytes)) as img:
                    size = {"width": img.width, "height": img.height}
                
                # Prepare response data
                response_data = None
                if request.output_format == "base64":
                    response_data = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                logger.info(
                    "Screenshot captured",
                    url=str(request.url),
                    duration=(datetime.now() - start_time).total_seconds(),
                    size=size
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
                "Screenshot failed",
                url=str(request.url),
                error=str(e),
                duration=(datetime.now() - start_time).total_seconds()
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
        "version": "1.0.3",
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
                
                if request.disable_animations:
                    await page.add_style_tag(content="""
                        *, *::before, *::after {
                            animation-duration: 0s !important;
                            animation-delay: 0s !important;
                            transition-duration: 0s !important;
                            transition-delay: 0s !important;
                        }
                    """)
                
                # Navigate with multiple fallback strategies and retries
                response = await screenshot_service._navigate_with_retries(
                    page,
                    str(request.url),
                    request.timeout,
                    "Binary mode: "
                )
                
                # Apply delay - use either user-specified delay or default minimum delay
                # This ensures heavy sites like YouTube have time to fully load
                effective_delay = max(request.delay, settings.default_delay)
                if effective_delay > 0:
                    await page.wait_for_timeout(effective_delay)
                
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
            "version": "1.0.3"
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

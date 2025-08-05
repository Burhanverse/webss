"""
Screenshot service with enhanced capabilities for heavy sites
"""

import asyncio
import base64
from typing import Optional
from io import BytesIO
from datetime import datetime
import structlog
from fastapi import HTTPException
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from PIL import Image

from .models import ScreenshotRequest, ScreenshotResponse
from .resource_handler import ResourceHandler
from .navigation import NavigationManager
from .content_checker import ContentChecker

logger = structlog.get_logger()


class ScreenshotService:
    """Enhanced screenshot service with robust handling for heavy sites"""
    
    def __init__(self, settings):
        self.browser: Optional[Browser] = None
        self.settings = settings
        self.resource_handler = ResourceHandler()
        self.navigation_manager = NavigationManager()
        self.content_checker = ContentChecker()
        
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
            await context.route("**/*", lambda route, req: self.resource_handler.handle_request(route, req, request))
            
        return context
    
    async def setup_page_for_heavy_sites(self, page: Page, request: ScreenshotRequest):
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
    
    async def take_screenshot_with_retry(self, page: Page, request: ScreenshotRequest, options: dict) -> bytes:
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
    
    async def capture_screenshot(self, request: ScreenshotRequest) -> ScreenshotResponse:
        """Enhanced screenshot capture with robust handling for heavy sites"""
        start_time = datetime.now()
        context = None
        page = None
        
        try:
            context = await self.create_context(request)
            page = await context.new_page()
            
            # Enhanced page setup
            await self.setup_page_for_heavy_sites(page, request)
            
            # Navigate with enhanced retry logic
            response = await self.navigation_manager.navigate_with_retries(
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
            effective_delay = await self.content_checker.calculate_smart_delay(page, request, self.settings)
            if effective_delay > 0:
                logger.info(
                    "Applying smart delay",
                    url=str(request.url),
                    delay=effective_delay,
                    user_delay=request.delay,
                    default_delay=self.settings.default_delay,
                    extra_wait=request.extra_wait_time
                )
                await page.wait_for_timeout(effective_delay)
            
            # Final content readiness check
            await self.content_checker.final_content_check(page, request, str(request.url))
            
            # Prepare screenshot options
            screenshot_options = {
                "type": request.format,
                "full_page": request.full_page
            }
            
            if request.format == "jpeg" and request.quality:
                screenshot_options["quality"] = request.quality
            
            # Take screenshot with retry logic
            screenshot_bytes = await self.take_screenshot_with_retry(
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
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

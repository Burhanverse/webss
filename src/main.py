import asyncio
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from asyncio_throttle import Throttler
from datetime import datetime

from config import Settings
from core.models import ScreenshotRequest, ScreenshotResponse
from core.screenshot_service import ScreenshotService

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

# Global throttler and service
throttler = Throttler(rate_limit=settings.rate_limit_requests, period=settings.rate_limit_period)
screenshot_service = ScreenshotService(settings)


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
        async with throttler:
            result = await screenshot_service.capture_screenshot(request)
        
        # If binary output is requested, return raw image data
        if request.output_format == "binary" and result.success:
            # We need to recreate the screenshot for binary response
            context = None
            page = None
            try:
                async with throttler:
                    context = await screenshot_service.create_context(request)
                    page = await context.new_page()
                    
                    # Enhanced page setup for binary mode
                    await screenshot_service.setup_page_for_heavy_sites(page, request)
                    
                    # Navigate with enhanced retry logic
                    response = await screenshot_service.navigation_manager.navigate_with_retries(
                        page,
                        str(request.url),
                        request.timeout,
                        request,
                        "Binary mode: "
                    )
                    
                    # Smart delay calculation and application
                    effective_delay = await screenshot_service.content_checker.calculate_smart_delay(
                        page, request, settings
                    )
                    if effective_delay > 0:
                        await page.wait_for_timeout(effective_delay)
                    
                    # Final content readiness check
                    await screenshot_service.content_checker.final_content_check(page, request, str(request.url))
                    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )

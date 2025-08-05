"""
Navigation utilities for enhanced page loading
"""

import asyncio
import structlog
from typing import Any
from playwright.async_api import Page

logger = structlog.get_logger()


class NavigationManager:
    """Handles enhanced navigation with retry logic for heavy sites"""
    
    def __init__(self):
        pass
    
    async def navigate_with_retries(self, page: Page, url: str, timeout: int, request, context: str = "") -> Any:
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
                    
                    // Enhanced image loading detection
                    const allImages = document.querySelectorAll('img');
                    let loadedImages = 0;
                    let totalImages = 0;
                    
                    allImages.forEach(img => {{
                        totalImages++;
                        // Check multiple conditions for loaded images
                        if (img.complete && img.naturalHeight !== 0) {{
                            loadedImages++;
                        }} else if (img.src && img.src.startsWith('data:')) {{
                            // Data URLs are immediately available
                            loadedImages++;
                        }} else if (!img.src && !img.dataset.src) {{
                            // Images without src are probably placeholders
                            loadedImages++;
                        }}
                    }});
                    
                    // Be more lenient - if more than 70% of images are loaded or very few images
                    if (totalImages > 3 && loadedImages / totalImages < 0.7) return false;
                    
                    return true;
                }}
            """
            
            # Wait for content to be ready
            await page.wait_for_function(check_script, timeout=timeout)
            logger.info(f"{context}Content readiness achieved", url=url)
            
        except Exception as e:
            # Non-critical failure
            logger.info(f"{context}Content readiness check timeout (continuing)", url=url, error=str(e))

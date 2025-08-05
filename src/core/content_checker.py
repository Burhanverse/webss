"""
Content checking utilities for enhanced image and lazy loading detection
"""

import structlog
from playwright.async_api import Page

logger = structlog.get_logger()


class ContentChecker:
    """Handles content readiness checking for screenshots"""
    
    def __init__(self):
        pass
    
    async def final_content_check(self, page: Page, request, url: str):
        """Enhanced final check to ensure content is ready for screenshot"""
        
        if not request.smart_wait:
            return
        
        try:
            # Enhanced image loading wait
            await page.wait_for_function("""
                () => {
                    const images = Array.from(document.images);
                    if (images.length === 0) return true;
                    
                    let loadedCount = 0;
                    images.forEach(img => {
                        // More comprehensive image loading check
                        if (img.complete && img.naturalHeight !== 0) {
                            loadedCount++;
                        } else if (img.src && img.src.startsWith('data:')) {
                            loadedCount++;
                        } else if (!img.src && !img.dataset.src) {
                            // Empty images are considered "loaded"
                            loadedCount++;
                        }
                    });
                    
                    // Be more lenient - 70% threshold for heavy sites
                    return loadedCount / images.length >= 0.7;
                }
            """, timeout=8000)
            
            # Enhanced lazy loading detection
            await page.wait_for_function("""
                () => {
                    // Check for various lazy loading patterns
                    const lazySelectors = [
                        '[data-src]', '[loading="lazy"]', '.lazy', '.lazyload', 
                        '.lazyloading', '[data-lazy]', '[data-original]',
                        '.lozad', '.lazy-loaded', '.lazy-loading'
                    ];
                    
                    for (const selector of lazySelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            // Check if still in loading state
                            if (el.classList.contains('lazyloading') || 
                                el.classList.contains('lazy-loading')) {
                                return false;
                            }
                            
                            // Check if data-src exists but src is missing
                            if (el.hasAttribute('data-src') && !el.src && 
                                el.getBoundingClientRect().top < window.innerHeight + 200) {
                                return false;
                            }
                        }
                    }
                    
                    return true;
                }
            """, timeout=5000)
            
            # Wait for YouTube specific content
            if 'youtube.com' in str(url) or 'youtu.be' in str(url):
                await page.wait_for_function("""
                    () => {
                        // Wait for YouTube thumbnails specifically
                        const thumbnails = document.querySelectorAll('img[src*="ytimg.com"], img[src*="ggpht.com"]');
                        if (thumbnails.length === 0) return true;
                        
                        let loadedThumbnails = 0;
                        thumbnails.forEach(thumb => {
                            if (thumb.complete && thumb.naturalHeight > 0) {
                                loadedThumbnails++;
                            }
                        });
                        
                        return loadedThumbnails / thumbnails.length >= 0.8;
                    }
                """, timeout=6000)
            
            logger.info("Enhanced final content check completed successfully")
            
        except Exception as e:
            # Non-critical failures
            logger.info("Enhanced content check timeout (non-critical)", error=str(e))
    
    async def calculate_smart_delay(self, page: Page, request, settings) -> int:
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

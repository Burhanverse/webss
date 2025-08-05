"""
Resource handler for smart ad blocking and image preservation
"""

import structlog
from urllib.parse import urlparse

logger = structlog.get_logger()


class ResourceHandler:
    """Handles smart resource blocking for web pages"""
    
    def __init__(self):
        # Critical domains to block (ads, analytics, trackers)
        self.blocked_domains = {
            'googletagmanager.com', 'google-analytics.com', 'googlesyndication.com',
            'doubleclick.net', 'outbrain.com', 'taboola.com', 'amazon-adsystem.com',
            'scorecardresearch.com', 'quantserve.com', 'chartbeat.com', 'parsely.com',
            'krxd.net', 'adsystem.com', 'ads.yahoo.com', 'advertising.com',
            'facebook.com/tr', 'connect.facebook.net', 'analytics.twitter.com',
            'hotjar.com', 'fullstory.com', 'mouseflow.com', 'crazyegg.com',
            'optimizely.com', 'mixpanel.com', 'segment.com', 'amplitude.com'
        }
        
        # More specific ad patterns to avoid blocking legitimate content
        self.blocked_patterns = [
            'googletagmanager', 'google-analytics', 'googlesyndication', 'googleadservices',
            'doubleclick.net', '/gtm.js', '/analytics.js', '/ga.js',
            'facebook.com/tr', 'twitter.com/i/adsct', 'linkedin.com/li',
            'tiktok.com/i18n/pixel', 'snapchat.com/p', '/pixel.gif',
            'outbrain.com', 'taboola.com', 'amazon-adsystem.com'
        ]
        
        # Known content domains to always allow
        self.trusted_image_domains = {
            # YouTube domains
            'i.ytimg.com', 'yt3.ggpht.com', 'yt3.googleusercontent.com',
            # Google domains
            'lh3.googleusercontent.com', 'lh4.googleusercontent.com', 'lh5.googleusercontent.com',
            # Media CDNs
            'media.giphy.com', 'i.imgur.com', 'imgur.com',
            # News sites
            'cdn.vox-cdn.com', 'duet-cdn.vox-cdn.com', 'chorus-cdn.net',
            # Social media
            'scontent.fbcdn.net', 'pbs.twimg.com', 'abs.twimg.com',
            # Common CDNs
            'cloudfront.net', 'fastly.com', 'jsdelivr.net', 'unpkg.com'
        }
        
        # Always block these resource types (non-essential for screenshots)
        self.always_block_types = {'other'}
        
        # Explicit ad indicators for images
        self.explicit_ad_indicators = [
            '/ad/', '/ads/', '/banner/', '/popup/', 
            'advertisement', 'adnxs.com', 'adsystem.com',
            'googlesyndication', 'doubleclick'
        ]
    
    async def handle_request(self, route, request, screenshot_request):
        """Enhanced smart resource blocking that preserves images while blocking ads"""
        url = request.url.lower()
        resource_type = request.resource_type
        
        # If image blocking is explicitly disabled, allow all images
        if resource_type in {'image', 'media'} and screenshot_request.block_images == False:
            await route.continue_()
            return
        
        # Check for blocked domains first
        if any(domain in url for domain in self.blocked_domains):
            await route.abort()
            return
            
        # Check for specific ad patterns (more precise)
        if any(pattern in url for pattern in self.blocked_patterns):
            await route.abort()
            return
            
        # Block only non-essential types
        if resource_type in self.always_block_types:
            await route.abort()
            return
            
        # Enhanced logic for images and media - be very permissive
        if resource_type in {'image', 'media'}:
            await self._handle_image_request(route, request, url)
            return
        
        # For fonts and stylesheets, be permissive
        if resource_type in {'font', 'stylesheet'}:
            await self._handle_asset_request(route, request, url)
            return
        
        # Allow everything else by default (be permissive)
        await route.continue_()
    
    async def _handle_image_request(self, route, request, url):
        """Handle image requests with enhanced filtering"""
        try:
            request_domain = urlparse(request.url).netloc
            page_domain = urlparse(route.request.frame.url).netloc
            
            # Always allow images from trusted domains
            if any(trusted in request_domain for trusted in self.trusted_image_domains):
                await route.continue_()
                return
            
            # Allow same domain images
            if request_domain == page_domain or request_domain.endswith(f'.{page_domain}'):
                await route.continue_()
                return
            
            # Only block if URL contains very specific ad indicators
            if any(indicator in url for indicator in self.explicit_ad_indicators):
                await route.abort()
                return
            
            # Default: allow all other images
            await route.continue_()
            return
            
        except Exception:
            # If parsing fails, allow the request (be permissive)
            await route.continue_()
            return
    
    async def _handle_asset_request(self, route, request, url):
        """Handle font and stylesheet requests"""
        try:
            request_domain = urlparse(request.url).netloc
            
            if any(blocked_domain in request_domain for blocked_domain in self.blocked_domains):
                await route.abort()
                return
                
        except Exception:
            pass
        
        await route.continue_()

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "WebSS - Website Screenshot API"
    api_version: str = "1.0.0"
    api_description: str = "A robust Python API for capturing website screenshots using Playwright"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    
    # Waitress Configuration
    threads: int = 6
    backlog: int = 1024
    connection_limit: int = 1000
    
    # Browser Configuration
    browser_headless: bool = True
    browser_timeout: int = 30000
    max_concurrent_browsers: int = 5
    
    # Screenshot Configuration
    default_width: int = 1920
    default_height: int = 1080
    default_format: str = "png"
    max_screenshot_width: int = 3840
    max_screenshot_height: int = 2160
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 1
    
    # Security
    allowed_origins: List[str] = ["*"]
    max_request_timeout: int = 120000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Browser launch arguments
BROWSER_ARGS = [
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
    '--disable-default-apps',
    '--disable-sync',
    '--disable-extensions'
]

# Blocked domains for ad/tracking blocking
BLOCKED_DOMAINS = {
    'googletagmanager.com',
    'google-analytics.com', 
    'googlesyndication.com',
    'doubleclick.net',
    'facebook.com',
    'twitter.com',
    'linkedin.com',
    'outbrain.com',
    'taboola.com',
    'amazon-adsystem.com',
    'scorecardresearch.com',
    'quantserve.com',
    'adsystem.com',
    'ads.yahoo.com',
    'advertising.com'
}

# Blocked resource types
BLOCKED_RESOURCE_TYPES = {
    'font', 
    'media', 
    'other',
    'websocket'
}

# Mobile device presets
MOBILE_DEVICES = {
    "iphone": {
        "width": 375,
        "height": 812,
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    },
    "android": {
        "width": 360,
        "height": 640,
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
    },
    "tablet": {
        "width": 768,
        "height": 1024,
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    }
}

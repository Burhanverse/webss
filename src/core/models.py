"""
Pydantic models for WebSS API
"""

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, field_validator


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
    block_images: bool = Field(default=False, description="Block images (not recommended for screenshots)")
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

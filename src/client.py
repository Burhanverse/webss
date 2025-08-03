import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
import base64

class WebSSClient:
    """Client for WebSS Screenshot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        async with self.session.get(f"{self.base_url}/") as response:
            return await response.json()
    
    async def capture_screenshot(
        self,
        url: str,
        width: int = 1920,
        height: int = 1080,
        format: str = "png",
        quality: Optional[int] = None,
        full_page: bool = False,
        delay: int = 0,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[list] = None,
        selector: Optional[str] = None,
        mobile: bool = False,
        disable_animations: bool = True,
        block_ads: bool = True,
        output_format: str = "base64"
    ) -> Dict[str, Any]:
        """Capture a screenshot"""
        
        payload = {
            "url": url,
            "width": width,
            "height": height,
            "format": format,
            "full_page": full_page,
            "delay": delay,
            "timeout": timeout,
            "mobile": mobile,
            "disable_animations": disable_animations,
            "block_ads": block_ads,
            "output_format": output_format
        }
        
        # Add optional parameters
        if quality is not None:
            payload["quality"] = quality
        if user_agent:
            payload["user_agent"] = user_agent
        if headers:
            payload["headers"] = headers
        if cookies:
            payload["cookies"] = cookies
        if selector:
            payload["selector"] = selector
        
        async with self.session.post(
            f"{self.base_url}/screenshot",
            json=payload
        ) as response:
            if output_format == "binary":
                if response.status == 200:
                    content = await response.read()
                    return {
                        "success": True,
                        "url": url,
                        "format": format,
                        "binary_data": content,
                        "size": len(content)
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"API Error: {error_data}")
            else:
                result = await response.json()
                if response.status != 200:
                    raise Exception(f"API Error: {result}")
                return result
    
    async def save_screenshot(
        self,
        url: str,
        filename: str,
        **kwargs
    ) -> bool:
        """Capture and save screenshot to file"""
        kwargs["output_format"] = "binary"
        result = await self.capture_screenshot(url, **kwargs)
        
        if result.get("success"):
            with open(filename, 'wb') as f:
                f.write(result["binary_data"])
            return True
        return False

# Synchronous client for non-async usage
class WebSSClientSync:
    """Synchronous client for WebSS Screenshot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def _run_async(self, coro):
        """Run async function in sync context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    async def _async_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make async HTTP request"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, **kwargs) as response:
                return await response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return self._run_async(self._async_request("GET", "/"))
    
    def capture_screenshot(self, url: str, **kwargs) -> Dict[str, Any]:
        """Capture a screenshot"""
        payload = {"url": url, **kwargs}
        return self._run_async(
            self._async_request("POST", "/screenshot", json=payload)
        )

# CLI interface
async def main():
    """Example usage of the client"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python client.py <url> [options]")
        return
    
    url = sys.argv[1]
    
    async with WebSSClient() as client:
        try:
            # Health check
            health = await client.health_check()
            print(f"API Status: {health['status']}")
            
            # Capture screenshot
            print(f"Capturing screenshot of {url}...")
            result = await client.capture_screenshot(
                url=url,
                width=1920,
                height=1080,
                full_page=True,
                format="png",
                output_format="base64"
            )
            
            if result['success']:
                print(f"Screenshot captured successfully!")
                print(f"Size: {result['size']}")
                print(f"Format: {result['format']}")
                print(f"Base64 data length: {len(result['data'])} characters")
                
                # Save base64 data to file
                if result.get('data'):
                    image_data = base64.b64decode(result['data'])
                    filename = f"screenshot_{int(asyncio.get_event_loop().time())}.{result['format']}"
                    with open(filename, 'wb') as f:
                        f.write(image_data)
                    print(f"Saved to: {filename}")
            else:
                print(f"Failed: {result['error']}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

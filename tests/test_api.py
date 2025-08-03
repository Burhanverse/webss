import pytest
import asyncio
from httpx import AsyncClient
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app

# Test configuration
TEST_URL = "https://httpbin.org/html"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestScreenshotAPI:
    """Test cases for the screenshot API"""
    
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "WebSS" in data["service"]
    
    async def test_detailed_health_check(self, client):
        """Test detailed health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "browser" in data
    
    async def test_single_screenshot_basic(self, client):
        """Test basic screenshot capture"""
        payload = {
            "url": TEST_URL,
            "width": 1024,
            "height": 768,
            "format": "png",
            "output_format": "base64"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["url"] == TEST_URL
        assert data["format"] == "png"
        assert data["size"]["width"] > 0
        assert data["size"]["height"] > 0
        assert data["data"] is not None
        assert len(data["data"]) > 0
    
    async def test_single_screenshot_binary(self, client):
        """Test binary screenshot output"""
        payload = {
            "url": TEST_URL,
            "width": 800,
            "height": 600,
            "format": "png",
            "output_format": "binary"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0
    
    async def test_single_screenshot_jpeg_quality(self, client):
        """Test JPEG screenshot with quality setting"""
        payload = {
            "url": TEST_URL,
            "width": 800,
            "height": 600,
            "format": "jpeg",
            "quality": 80,
            "output_format": "base64"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["format"] == "jpeg"
    
    async def test_single_screenshot_full_page(self, client):
        """Test full page screenshot"""
        payload = {
            "url": TEST_URL,
            "width": 1200,
            "height": 800,
            "format": "png",
            "full_page": True,
            "output_format": "base64"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        # Full page screenshots are typically taller
        assert data["size"]["height"] >= 800
    
    async def test_single_screenshot_mobile(self, client):
        """Test mobile viewport screenshot"""
        payload = {
            "url": TEST_URL,
            "width": 375,
            "height": 812,
            "format": "png",
            "mobile": True,
            "output_format": "base64"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    async def test_single_screenshot_with_delay(self, client):
        """Test screenshot with delay"""
        payload = {
            "url": TEST_URL,
            "width": 1024,
            "height": 768,
            "format": "png",
            "delay": 1000,  # 1 second delay
            "output_format": "base64"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    async def test_invalid_url(self, client):
        """Test screenshot with invalid URL"""
        payload = {
            "url": "not-a-valid-url",
            "width": 1024,
            "height": 768,
            "format": "png"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 422  # Validation error
    
    async def test_invalid_dimensions(self, client):
        """Test screenshot with invalid dimensions"""
        payload = {
            "url": TEST_URL,
            "width": 100,  # Too small
            "height": 5000,  # Too large
            "format": "png"
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 422  # Validation error
    
    async def test_invalid_format(self, client):
        """Test screenshot with invalid format"""
        payload = {
            "url": TEST_URL,
            "width": 1024,
            "height": 768,
            "format": "gif"  # Not supported
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 422  # Validation error
    
    async def test_quality_without_jpeg(self, client):
        """Test quality parameter with non-JPEG format"""
        payload = {
            "url": TEST_URL,
            "width": 1024,
            "height": 768,
            "format": "png",
            "quality": 80  # Should cause validation error
        }
        
        response = await client.post("/screenshot", json=payload)
        assert response.status_code == 422  # Validation error

class TestScreenshotValidation:
    """Test input validation"""
    
    async def test_url_validation(self, client):
        """Test URL validation"""
        test_cases = [
            {"url": "invalid-url", "should_pass": False},
            {"url": "http://example.com", "should_pass": True},
            {"url": "https://example.com", "should_pass": True},
            {"url": "ftp://example.com", "should_pass": False},  # Only HTTP/HTTPS
        ]
        
        for case in test_cases:
            payload = {
                "url": case["url"],
                "width": 1024,
                "height": 768,
                "format": "png"
            }
            
            response = await client.post("/screenshot", json=payload)
            if case["should_pass"]:
                assert response.status_code in [200, 400]  # 400 for connection errors
            else:
                assert response.status_code == 422
    
    async def test_dimension_validation(self, client):
        """Test dimension validation"""
        test_cases = [
            {"width": 319, "height": 768, "should_pass": False},  # Too small width
            {"width": 3841, "height": 768, "should_pass": False},  # Too large width
            {"width": 1024, "height": 239, "should_pass": False},  # Too small height
            {"width": 1024, "height": 2161, "should_pass": False},  # Too large height
            {"width": 1024, "height": 768, "should_pass": True},  # Valid
        ]
        
        for case in test_cases:
            payload = {
                "url": TEST_URL,
                "width": case["width"],
                "height": case["height"],
                "format": "png"
            }
            
            response = await client.post("/screenshot", json=payload)
            if case["should_pass"]:
                assert response.status_code == 200
            else:
                assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

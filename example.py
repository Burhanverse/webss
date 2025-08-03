#!/usr/bin/env python3
"""
Example usage script for WebSS API
Demonstrates various screenshot capture scenarios
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from client import WebSSClient, WebSSClientSync

async def demo_async_client():
    """Demonstrate async client usage"""
    print("=== Async Client Demo ===")
    
    async with WebSSClient("http://localhost:8000") as client:
        try:
            # Health check
            health = await client.health_check()
            print(f"API Status: {health['status']}")
            
            # Basic screenshot
            print("\n1. Basic screenshot (base64)...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/html",
                width=1200,
                height=800,
                format="png",
                output_format="base64"
            )
            
            if result['success']:
                print(f"✓ Screenshot captured: {result['size']}")
                print(f"  Base64 data length: {len(result['data'])} characters")
            else:
                print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            
            # Full page screenshot
            print("\n2. Full page screenshot...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/html",
                width=1920,
                height=1080,
                format="png",
                full_page=True,
                output_format="base64"
            )
            
            if result['success']:
                print(f"✓ Full page screenshot: {result['size']}")
            
            # Mobile screenshot
            print("\n3. Mobile screenshot...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/html",
                width=375,
                height=812,
                format="png",
                mobile=True,
                output_format="base64"
            )
            
            if result['success']:
                print(f"✓ Mobile screenshot: {result['size']}")
            
            # JPEG with quality
            print("\n4. JPEG with quality...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/html",
                width=1024,
                height=768,
                format="jpeg",
                quality=85,
                output_format="base64"
            )
            
            if result['success']:
                print(f"✓ JPEG screenshot: {result['size']}")
            
            # Save to file
            print("\n5. Save to file...")
            success = await client.save_screenshot(
                url="https://httpbin.org/html",
                filename="example_screenshot.png",
                width=1200,
                height=800,
                format="png",
                full_page=True
            )
            
            if success:
                print("✓ Screenshot saved to example_screenshot.png")
            else:
                print("✗ Failed to save screenshot")
                
        except Exception as e:
            print(f"Error: {e}")

def demo_sync_client():
    """Demonstrate sync client usage"""
    print("\n=== Sync Client Demo ===")
    
    client = WebSSClientSync("http://localhost:8000")
    
    try:
        # Health check
        health = client.health_check()
        print(f"API Status: {health['status']}")
        
        # Basic screenshot
        print("\n1. Basic sync screenshot...")
        result = client.capture_screenshot(
            url="https://httpbin.org/html",
            width=800,
            height=600,
            format="png",
            output_format="base64"
        )
        
        if result['success']:
            print(f"✓ Sync screenshot captured: {result['size']}")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")

async def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n=== Advanced Features Demo ===")
    
    async with WebSSClient("http://localhost:8000") as client:
        try:
            # Custom headers and user agent
            print("\n1. Custom headers and user agent...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/headers",
                width=1200,
                height=800,
                user_agent="WebSS-Bot/1.0",
                headers={"X-Custom-Header": "WebSS-Test"},
                output_format="base64"
            )
            
            if result['success']:
                print("✓ Screenshot with custom headers captured")
            
            # With delay
            print("\n2. Screenshot with delay...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/delay/1",
                width=1200,
                height=800,
                delay=2000,  # 2 second delay after page load
                timeout=45000,  # 45 second timeout
                output_format="base64"
            )
            
            if result['success']:
                print("✓ Screenshot with delay captured")
            
            # Ad blocking disabled
            print("\n3. Screenshot without ad blocking...")
            result = await client.capture_screenshot(
                url="https://httpbin.org/html",
                width=1200,
                height=800,
                block_ads=False,
                output_format="base64"
            )
            
            if result['success']:
                print("✓ Screenshot without ad blocking captured")
                
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main demo function"""
    print("WebSS API Demo")
    print("==============")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Run async demos
    asyncio.run(demo_async_client())
    asyncio.run(demo_advanced_features())
    
    # Run sync demo
    demo_sync_client()
    
    print("\n=== Demo Complete ===")
    print("Check the generated files:")
    print("- example_screenshot.png")

if __name__ == "__main__":
    main()

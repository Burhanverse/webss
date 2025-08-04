import os
import sys
from pathlib import Path
import uvicorn
import structlog

# Add current directory to path to import main
sys.path.insert(0, str(Path(__file__).parent))
from main import app

logger = structlog.get_logger()

def run_with_uvicorn():
    """Run the FastAPI app with Uvicorn ASGI server"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))  # Use workers instead of threads for ASGI
    
    logger.info(
        "Starting WebSS API with Uvicorn",
        host=host,
        port=port,
        workers=workers
    )
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        # Performance tuning
        backlog=1024,
        # Security
        limit_max_requests=1000,
        # Timeouts
        timeout_keep_alive=30,
        # Connection handling
        limit_concurrency=1000,
        # Access logging
        access_log=True,
        # Use production settings
        log_level="info"
    )

if __name__ == "__main__":
    run_with_uvicorn()

import os
import sys
from pathlib import Path
from waitress import serve
import structlog

# Add current directory to path to import main
sys.path.insert(0, str(Path(__file__).parent))
from main import app

logger = structlog.get_logger()

def run_with_waitress():
    """Run the FastAPI app with Waitress WSGI server"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    threads = int(os.getenv("THREADS", 6))
    
    logger.info(
        "Starting WebSS API with Waitress",
        host=host,
        port=port,
        threads=threads
    )
    
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        url_scheme="http",
        # Performance tuning
        backlog=1024,
        recv_bytes=65536,
        send_bytes=65536,
        # Security
        max_request_header_size=8192,
        max_request_body_size=104857600,  # 100MB
        # Timeouts
        cleanup_interval=30,
        channel_timeout=120,
        # Connection handling
        connection_limit=1000,
        # Enable keepalive
        asyncore_use_poll=True,
    )

if __name__ == "__main__":
    run_with_waitress()

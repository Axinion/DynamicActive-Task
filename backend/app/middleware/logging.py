"""
Request logging middleware for K12 LMS API.
Logs method, path, status, and latency for all requests.
"""

import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing and status information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started - ID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate latency
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed - ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Latency: {process_time:.3f}s"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate latency for failed requests
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed - ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Latency: {process_time:.3f}s"
            )
            
            # Re-raise the exception
            raise

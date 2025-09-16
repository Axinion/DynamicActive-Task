"""
Rate limiting middleware for K12 LMS API.
Implements token bucket algorithm for rate limiting sensitive endpoints.
"""

import time
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        now = time.time()
        
        # Refill tokens based on time elapsed
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm."""
    
    def __init__(self, app, rate_limit_config: Optional[Dict[str, Dict]] = None):
        super().__init__(app)
        self.rate_limit_config = rate_limit_config or {
            "/api/auth/login": {
                "capacity": 5,  # 5 requests
                "refill_rate": 1.0,  # 1 request per second
                "window": 60  # 1 minute window
            },
            "/api/auth/register": {
                "capacity": 3,  # 3 requests
                "refill_rate": 0.5,  # 1 request per 2 seconds
                "window": 60  # 1 minute window
            }
        }
        self.buckets: Dict[str, TokenBucket] = {}
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique key for client (IP address)."""
        client_ip = request.client.host if request.client else "unknown"
        return f"{client_ip}:{request.url.path}"
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request."""
        path = request.url.path
        
        # Check if this path has rate limiting configured
        if path in self.rate_limit_config:
            config = self.rate_limit_config[path]
            client_key = self._get_client_key(request)
            
            # Get or create token bucket for this client and path
            if client_key not in self.buckets:
                self.buckets[client_key] = TokenBucket(
                    capacity=config["capacity"],
                    refill_rate=config["refill_rate"]
                )
            
            bucket = self.buckets[client_key]
            
            # Check if request is allowed
            if not bucket.consume():
                logger.warning(
                    f"Rate limit exceeded for {client_key} on {path}"
                )
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "detail": f"Too many requests. Limit: {config['capacity']} requests per {config['window']} seconds",
                        "retry_after": config["window"]
                    }
                )
        
        # Process request
        response = await call_next(request)
        return response

"""
Rate limiting middleware to prevent abuse.
"""
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting per user."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.request_counts = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health check and metrics
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get user identifier (user_id or IP address)
        if hasattr(request.state, "user"):
            identifier = str(request.state.user.id)
        else:
            identifier = request.client.host if request.client else "unknown"
        
        current_time = time.time()
        
        # Clean old requests outside the window
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if current_time - req_time < self.window_size
        ]
        
        # Check if rate limit exceeded
        if len(self.request_counts[identifier]) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded",
                identifier=identifier,
                path=request.url.path,
                requests_in_window=len(self.request_counts[identifier])
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed.",
                        "retry_after": self.window_size,
                        "timestamp": ""
                    }
                },
                headers={"Retry-After": str(self.window_size)}
            )
        
        # Add current request to the count
        self.request_counts[identifier].append(current_time)
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_counts[identifier])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_size)
        )
        
        return response

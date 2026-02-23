"""
Cache Control Middleware to prevent browser caching of API responses.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add Cache-Control headers to all API responses.
    
    This prevents browsers from caching API responses, ensuring users
    always get fresh data when creating/updating entities.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add cache control headers to prevent caching
        # Only apply to API endpoints (not static files)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response

"""
Logging middleware for request/response tracking.
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import request_id_var, user_id_var, client_id_var, project_id_var, StructuredLogger

logger = StructuredLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Store request_id in request state for access in handlers
        request.state.request_id = request_id
        
        # Extract user info from request if available
        if hasattr(request.state, "user"):
            user = request.state.user
            user_id_var.set(str(user.id))
            client_id_var.set(str(user.client_id))
        
        # Record start time
        start_time = time.time()
        
        # Log incoming request
        logger.debug(
            f"Incoming request: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(exc)
            )
            raise
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        logger.log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        # Log slow requests
        if duration_ms > 2000:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                status_code=response.status_code
            )
        
        return response

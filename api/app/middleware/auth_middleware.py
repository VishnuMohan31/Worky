"""
Authentication middleware for JWT token validation.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status
from jose import JWTError, jwt
from sqlalchemy import select
from app.core.config import settings
from app.models.user import User
from app.db.base import async_session_maker
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens and attach user to request."""
    
    # Paths that don't require authentication
    EXEMPT_PATHS = [
        "/",
        "/health",
        "/api/v1/auth/login",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics"
    ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip authentication for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": "MISSING_TOKEN",
                        "message": "Authentication token is missing",
                        "timestamp": ""
                    }
                }
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            
            if not user_id:
                raise JWTError("Invalid token payload")
            
            # Fetch user from database
            async with async_session_maker() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={
                            "error": {
                                "code": "USER_NOT_FOUND",
                                "message": "User not found",
                                "timestamp": ""
                            }
                        }
                    )
                
                if not user.is_active:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "error": {
                                "code": "USER_INACTIVE",
                                "message": "User account is inactive",
                                "timestamp": ""
                            }
                        }
                    )
                
                # Attach user to request state
                request.state.user = user
                
                logger.debug(
                    "User authenticated",
                    user_id=str(user.id),
                    role=user.role,
                    client_id=str(user.client_id)
                )
        
        except JWTError as e:
            logger.warning(
                "Invalid JWT token",
                error=str(e),
                path=request.url.path
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Authentication token is invalid or expired",
                        "timestamp": ""
                    }
                }
            )
        except Exception as e:
            logger.error(
                "Authentication error",
                error=str(e),
                path=request.url.path
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "AUTH_ERROR",
                        "message": "Authentication failed",
                        "timestamp": ""
                    }
                }
            )
        
        return await call_next(request)

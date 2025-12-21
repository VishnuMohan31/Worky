"""
Custom exception classes and exception handlers for the Worky API.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WorkyException(Exception):
    """Base exception class for Worky application errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundException(WorkyException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} with ID {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class AccessDeniedException(WorkyException):
    """Exception raised when user doesn't have permission to access a resource."""
    
    def __init__(self, message: str = "You do not have permission to access this resource"):
        super().__init__(
            code="ACCESS_DENIED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ValidationException(WorkyException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {}
        )


class ConflictException(WorkyException):
    """Exception raised when there's a conflict with existing data."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details or {}
        )


class DatabaseException(WorkyException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceException(WorkyException):
    """Exception raised when external service calls fail."""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service_name}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name}
        )


async def worky_exception_handler(request: Request, exc: WorkyException) -> JSONResponse:
    """Handle WorkyException and return formatted JSON response."""
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the exception
    logger.error(
        f"WorkyException: {exc.code} - {exc.message}",
        extra={
            "request_id": request_id,
            "code": exc.code,
            "error_message": exc.message,  # Changed from "message" to "error_message"
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions and return formatted JSON response."""
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the exception with full traceback
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {},
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )

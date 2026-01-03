"""
Main FastAPI application with middleware and exception handlers.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, StructuredLogger
from app.core.exceptions import (
    WorkyException,
    worky_exception_handler,
    generic_exception_handler
)
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.api.v1.router import api_router
import asyncio

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    environment=settings.ENVIRONMENT
)
logger = StructuredLogger(__name__)

# Create FastAPI app
# Disable API docs in production for security
docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Worky Project Management Platform API",
    docs_url=docs_url,
    redoc_url=redoc_url
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=500)

# CORS middleware - MUST be added LAST so it wraps all other middleware
# This ensures CORS headers are added to all responses, including errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Exception handlers
app.add_exception_handler(WorkyException, worky_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add handler for Pydantic validation errors to log them
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors and log them for debugging."""
    errors = exc.errors()
    error_details = []
    for error in errors:
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Get request body if available (only for POST/PUT/PATCH)
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            request_body = body.decode('utf-8') if body else None
        except Exception:
            pass
    
    logger.error(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "validation_errors": error_details,
            "request_body": request_body,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_details,
            "message": "Validation error: " + "; ".join([f"{e['field']}: {e['message']}" for e in error_details])
        }
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Add basic stub endpoints to prevent 500 errors (these will be overridden by the router)
# The real endpoints are in the router, but they might fail due to missing tables or dependencies


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(
        "Application starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )
    
    # Initialize chat service
    try:
        from app.services.chat_service import get_chat_service
        chat_service = get_chat_service()
        await chat_service.initialize()
        logger.info("Chat service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chat service: {str(e)}", exc_info=True)
        logger.warning("Chat endpoints may not function properly")
    
    # Sprint background job is disabled - sprints are now created manually
    # Initialize sprint background job (lazy import to avoid circular dependencies)
    # try:
    #     from app.services.sprint_background_job import sprint_background_job
    #     await sprint_background_job.initialize()
    #     
    #     # Run initial sprint generation
    #     asyncio.create_task(sprint_background_job.ensure_sprints_for_all_projects())
    #     
    #     # Start periodic sprint generation (runs every hour)
    #     asyncio.create_task(sprint_background_job.run_periodically(interval_minutes=60))
    #     
    #     logger.info("Sprint background job started")
    # except Exception as e:
    #     logger.error(f"Failed to start sprint background job: {str(e)}", exc_info=True)
    logger.info("Sprint background job is disabled - sprints must be created manually")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Application shutting down")
    
    # Cleanup chat service
    try:
        from app.services.chat_service import get_chat_service
        chat_service = get_chat_service()
        # Close connections
        if hasattr(chat_service.session_service, 'close'):
            await chat_service.session_service.close()
        if hasattr(chat_service.llm_service, 'close'):
            await chat_service.llm_service.close()
        logger.info("Chat service cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up chat service: {str(e)}")
    
    # Sprint background job is disabled
    # Stop sprint background job
    # try:
    #     from app.services.sprint_background_job import sprint_background_job
    #     sprint_background_job.stop()
    #     await sprint_background_job.close()
    #     logger.info("Sprint background job stopped")
    # except Exception as e:
    #     logger.error(f"Error stopping sprint background job: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint."""
    response = {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "health": "/health"
    }
    # Only expose docs URL in non-production environments
    if settings.ENVIRONMENT != "production":
        response["docs"] = "/docs"
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "worky-api",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8007,
        log_level="info"
    )

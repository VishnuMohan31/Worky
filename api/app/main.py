"""
Main FastAPI application with middleware and exception handlers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Worky Project Management Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# CORS middleware - MUST be added LAST so it wraps all other middleware
# This ensures CORS headers are added to all responses, including errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Exception handlers
app.add_exception_handler(WorkyException, worky_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(
        "Application starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.DEBUG and "development" or "production"
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
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


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

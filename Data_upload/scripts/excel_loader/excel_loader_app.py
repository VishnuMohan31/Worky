"""
Excel Loader FastAPI Application

This module provides a FastAPI-based REST API for importing Excel files containing
hierarchical project data into the Worky database. It handles file uploads, validation,
and orchestrates the import process.

Requirements: 1.1, 1.3, 7.1
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from dotenv import load_dotenv

# Add workspace root and api directory to path for module imports
workspace_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, workspace_root)
sys.path.insert(0, os.path.join(workspace_root, 'api'))

from import_orchestrator import ImportOrchestrator, ImportResponse

# Load environment variables
load_dotenv()

# Configure logging using Worky's structured logging
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'api'))

try:
    from app.core.logging import setup_logging, StructuredLogger
    
    # Setup structured logging
    log_file = os.getenv("EXCEL_LOADER_LOG_FILE", "logs/excel_loader.log")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    environment = os.getenv("ENVIRONMENT", "development")
    
    setup_logging(log_level=log_level, log_file=log_file, environment=environment)
    logger = StructuredLogger("excel_loader")
    
except ImportError:
    # Fallback to basic logging if Worky logging not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.warning("Worky structured logging not available, using basic logging")

# Helper function to log with optional structured data
def log_info(message: str, **kwargs):
    """Log info message with optional structured data."""
    try:
        logger.info(message, **kwargs)
    except TypeError:
        logger.info(message)

def log_warning(message: str, **kwargs):
    """Log warning message with optional structured data."""
    try:
        logger.warning(message, **kwargs)
    except TypeError:
        logger.warning(message)

def log_error(message: str, **kwargs):
    """Log error message with optional structured data."""
    try:
        logger.error(message, **kwargs)
    except TypeError:
        logger.error(message)

# Configuration
class Config:
    """Application configuration."""
    APP_NAME = "Excel Data Loader"
    APP_VERSION = "1.0.0"
    
    # Database configuration (reuse from main API)
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5437"))
    DATABASE_NAME = os.getenv("DATABASE_NAME", "worky")
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
    
    # File upload limits
    EXCEL_UPLOAD_MAX_SIZE = int(os.getenv("EXCEL_UPLOAD_MAX_SIZE", 50 * 1024 * 1024))  # 50MB
    EXCEL_IMPORT_TIMEOUT = int(os.getenv("EXCEL_IMPORT_TIMEOUT", 300))  # 5 minutes
    
    # CORS origins
    CORS_ORIGINS = [
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3000",
        "http://localhost:8007",
    ]
    
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


config = Config()

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Excel Data Loader for Worky Project Management Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Database setup
engine = create_async_engine(
    config.database_url,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Database dependency
async def get_db() -> AsyncSession:
    """
    Database session dependency.
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Validation helpers
def validate_file_type(filename: str) -> bool:
    """
    Validate that the file is an Excel file.
    
    Args:
        filename: Name of the uploaded file
    
    Returns:
        bool: True if valid Excel file
    """
    allowed_extensions = {'.xlsx', '.xls'}
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """
    Validate that the file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
    
    Returns:
        bool: True if within size limit
    """
    return file_size <= config.EXCEL_UPLOAD_MAX_SIZE


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "excel-loader",
        "version": config.APP_VERSION
    }


@app.post("/api/import", response_model=ImportResponse)
async def import_excel_data(
    file: UploadFile = File(..., description="Excel file to import (.xlsx or .xls)"),
    db: AsyncSession = Depends(get_db)
) -> ImportResponse:
    """
    Import project data from an Excel file.
    
    This endpoint accepts an Excel file upload and imports the hierarchical project data
    into the Worky database. The Excel file should contain sheets for Projects, Usecases,
    Userstories, Tasks, and Subtasks.
    
    Args:
        file: Uploaded Excel file
        db: Database session (injected)
    
    Returns:
        ImportResponse: Import results with summary, warnings, and errors
    
    Raises:
        HTTPException: If file validation fails or import encounters critical errors
    
    Requirements: 1.1, 1.3, 7.1
    """
    temp_file_path: Optional[str] = None
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .xlsx and .xls files are allowed."
            )
        
        log_info(
            f"Received file upload: {file.filename}",
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if not validate_file_size(file_size):
            max_size_mb = config.EXCEL_UPLOAD_MAX_SIZE / (1024 * 1024)
            log_warning(
                f"File size exceeds limit: {file_size / (1024 * 1024):.2f}MB > {max_size_mb:.0f}MB",
                filename=file.filename,
                file_size_mb=file_size / (1024 * 1024),
                max_size_mb=max_size_mb
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB"
            )
        
        log_info(
            f"File validated successfully",
            filename=file.filename,
            file_size_kb=file_size / 1024,
            file_size_mb=file_size / (1024 * 1024)
        )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=Path(file.filename).suffix,
            delete=False
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        log_info(
            f"Saved temporary file",
            temp_file_path=temp_file_path,
            filename=file.filename
        )
        
        # Create orchestrator and process import
        orchestrator = ImportOrchestrator(db)
        
        log_info(
            "Starting import process",
            filename=file.filename,
            file_size_kb=file_size / 1024
        )
        result = await orchestrator.import_from_file(temp_file_path)
        
        # Log results with structured data
        if result.success:
            log_info(
                f"Import completed successfully",
                filename=file.filename,
                duration_seconds=result.duration_seconds,
                total_records=sum(result.summary.values()),
                summary=result.summary,
                warnings_count=len(result.warnings),
                errors_count=len(result.errors)
            )
            
            # Log warnings if any
            if result.warnings:
                for warning in result.warnings:
                    log_warning(f"Import warning: {warning}", filename=file.filename)
        else:
            log_error(
                f"Import failed",
                filename=file.filename,
                duration_seconds=result.duration_seconds,
                errors_count=len(result.errors),
                warnings_count=len(result.warnings)
            )
            
            # Log each error
            for error in result.errors:
                log_error(f"Import error: {error}", filename=file.filename)
        
        # Return appropriate status code based on success
        if not result.success:
            # Return 500 for import failures but still return the detailed response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=result.model_dump()
            )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error during import: {str(e)}"
        try:
            logger.error(error_msg, exc_info=True)
        except TypeError:
            logger.error(error_msg)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": error_msg,
                "summary": {},
                "warnings": [],
                "errors": [error_msg],
                "duration_seconds": 0.0
            }
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                log_info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                log_warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    startup_msg = (
        f"{config.APP_NAME} v{config.APP_VERSION} starting up - "
        f"DB: {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}, "
        f"Max file size: {config.EXCEL_UPLOAD_MAX_SIZE / (1024 * 1024):.0f}MB, "
        f"Timeout: {config.EXCEL_IMPORT_TIMEOUT}s"
    )
    log_info(
        startup_msg,
        app_name=config.APP_NAME,
        app_version=config.APP_VERSION,
        database_host=config.DATABASE_HOST,
        database_port=config.DATABASE_PORT,
        database_name=config.DATABASE_NAME,
        max_file_size_mb=config.EXCEL_UPLOAD_MAX_SIZE / (1024 * 1024),
        import_timeout_seconds=config.EXCEL_IMPORT_TIMEOUT
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    shutdown_msg = f"{config.APP_NAME} shutting down"
    log_info(shutdown_msg, app_name=config.APP_NAME)
    
    # Close database engine
    await engine.dispose()
    log_info("Database connections closed")


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

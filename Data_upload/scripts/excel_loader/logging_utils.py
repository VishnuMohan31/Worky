"""
Logging utilities for Excel Loader

Provides helper functions that work with both structured and basic Python logging.
Configures logging using the existing Worky logging setup.

Requirements: 1.4, 3.2, 6.4
"""

import logging
import sys
import os
from typing import Optional

# Try to import structured logger from Worky API
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'api'))
    from app.core.logging import StructuredLogger, setup_logging
    USE_STRUCTURED_LOGGING = True
except ImportError:
    USE_STRUCTURED_LOGGING = False
    setup_logging = None


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the Excel Loader using Worky's logging setup.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    if USE_STRUCTURED_LOGGING and setup_logging:
        # Use Worky's structured logging
        setup_logging(
            log_level=log_level,
            log_file=log_file,
            environment=os.getenv('ENVIRONMENT', 'development')
        )
    else:
        # Fall back to basic Python logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file) if log_file else logging.NullHandler()
            ]
        )


def get_logger(name: str):
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically module name)
    
    Returns:
        Logger instance (structured or basic)
    """
    if USE_STRUCTURED_LOGGING:
        return StructuredLogger(name)
    else:
        return logging.getLogger(name)


def log_info(logger_instance, message: str, **kwargs):
    """
    Log INFO level message with optional structured data.
    
    Use for:
    - Import progress updates
    - Successful operations
    - Record counts
    
    Args:
        logger_instance: Logger instance
        message: Log message
        **kwargs: Optional structured data (ignored for basic logger)
    """
    try:
        logger_instance.info(message, **kwargs)
    except TypeError:
        logger_instance.info(message)


def log_warning(logger_instance, message: str, **kwargs):
    """
    Log WARNING level message with optional structured data.
    
    Use for:
    - Unmapped columns
    - Missing user references
    - Data quality issues
    - Non-critical errors
    
    Args:
        logger_instance: Logger instance
        message: Log message
        **kwargs: Optional structured data (ignored for basic logger)
    """
    try:
        logger_instance.warning(message, **kwargs)
    except TypeError:
        logger_instance.warning(message)


def log_error(logger_instance, message: str, exc_info=False, **kwargs):
    """
    Log ERROR level message with optional structured data.
    
    Use for:
    - Import failures
    - Database errors
    - File processing errors
    - Critical validation failures
    
    Args:
        logger_instance: Logger instance
        message: Log message
        exc_info: Whether to include exception info
        **kwargs: Optional structured data (ignored for basic logger)
    """
    try:
        logger_instance.error(message, exc_info=exc_info, **kwargs)
    except TypeError:
        logger_instance.error(message, exc_info=exc_info)


def log_debug(logger_instance, message: str, **kwargs):
    """
    Log DEBUG level message with optional structured data.
    
    Use for:
    - Detailed processing information
    - Individual record processing
    - Cache hits/misses
    
    Args:
        logger_instance: Logger instance
        message: Log message
        **kwargs: Optional structured data (ignored for basic logger)
    """
    try:
        logger_instance.debug(message, **kwargs)
    except TypeError:
        logger_instance.debug(message)


def log_import_progress(logger_instance, entity_type: str, current: int, total: int, **kwargs):
    """
    Log import progress for an entity type.
    
    Args:
        logger_instance: Logger instance
        entity_type: Type of entity being imported
        current: Current record number
        total: Total records to import
        **kwargs: Additional context
    """
    percentage = (current / total * 100) if total > 0 else 0
    message = f"Importing {entity_type}: {current}/{total} ({percentage:.1f}%)"
    
    context = {
        'entity_type': entity_type,
        'current': current,
        'total': total,
        'percentage': percentage,
        **kwargs
    }
    
    log_info(logger_instance, message, **context)


def log_import_summary(logger_instance, duration_seconds: float, summary: dict, warnings_count: int, errors_count: int):
    """
    Log final import summary with all statistics.
    
    Args:
        logger_instance: Logger instance
        duration_seconds: Total import duration
        summary: Dictionary of entity counts
        warnings_count: Number of warnings
        errors_count: Number of errors
    """
    total_records = sum(summary.values())
    message = f"Import completed in {duration_seconds:.2f}s: {total_records} total records"
    
    context = {
        'duration_seconds': duration_seconds,
        'total_records': total_records,
        'warnings_count': warnings_count,
        'errors_count': errors_count,
        **summary
    }
    
    if errors_count > 0:
        log_error(logger_instance, message, **context)
    elif warnings_count > 0:
        log_warning(logger_instance, message, **context)
    else:
        log_info(logger_instance, message, **context)

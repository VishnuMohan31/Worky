"""
Structured logging configuration for the Worky API.
"""
import logging
import json
import sys
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')
client_id_var: ContextVar[str] = ContextVar('client_id', default='')
project_id_var: ContextVar[str] = ContextVar('project_id', default='')


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes context variables."""
    
    def __init__(self, *args, environment: str = "development", **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = environment
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp (ISO 8601 format with Z suffix)
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Add service info
        log_record['service'] = 'worky-api'
        log_record['environment'] = self.environment
        log_record['level'] = record.levelname
        
        # Add context variables (only if set)
        request_id = request_id_var.get()
        if request_id:
            log_record['request_id'] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_record['user_id'] = user_id
        
        client_id = client_id_var.get()
        if client_id:
            log_record['client_id'] = client_id
        
        project_id = project_id_var.get()
        if project_id:
            log_record['project_id'] = project_id
        
        # Add message
        log_record['message'] = record.getMessage()
        
        # Add extra fields from record (avoid overwriting reserved logging fields)
        reserved_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 
            'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 
            'thread', 'threadName', 'processName', 'process', 'message', 'exc_info', 
            'exc_text', 'stack_info', 'getMessage', 'extra'
        }
        
        for key, value in record.__dict__.items():
            if key not in reserved_fields:
                log_record[key] = value


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, environment: str = "development") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        environment: Environment name (development, production, etc.)
    """
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        environment=environment
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class StructuredLogger:
    """Structured logger with context-aware logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(self, level: str, message: str, **context: Any) -> None:
        """Internal logging method with context."""
        # Extract special logging parameters
        exc_info = context.pop('exc_info', None)
        stack_info = context.pop('stack_info', None)
        stacklevel = context.pop('stacklevel', 1)
        
        # Pass remaining context as extra
        self.logger.log(
            getattr(logging, level.upper()),
            message,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=context
        )
    
    def debug(self, message: str, **context: Any) -> None:
        """Log debug message."""
        self._log("DEBUG", message, **context)
    
    def info(self, message: str, **context: Any) -> None:
        """Log info message."""
        self._log("INFO", message, **context)
    
    def warning(self, message: str, **context: Any) -> None:
        """Log warning message."""
        self._log("WARNING", message, **context)
    
    def error(self, message: str, **context: Any) -> None:
        """Log error message."""
        self._log("ERROR", message, **context)
    
    def critical(self, message: str, **context: Any) -> None:
        """Log critical message."""
        self._log("CRITICAL", message, **context)
    
    def log_activity(
        self,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        **context: Any
    ) -> None:
        """Log user activity."""
        log_context = {
            "action": action,
            **context
        }
        if entity_type:
            log_context["entity_type"] = entity_type
        if entity_id:
            log_context["entity_id"] = entity_id
        
        self.info(
            f"User activity: {action}",
            **log_context
        )
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **context: Any
    ) -> None:
        """Log API request."""
        self.info(
            f"API request: {method} {path}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **context
        )
    
    def log_database_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        **context: Any
    ) -> None:
        """Log database query."""
        if duration_ms > 1000:  # Log slow queries
            self.warning(
                f"Slow database query: {query_type} on {table}",
                query_type=query_type,
                table=table,
                duration_ms=duration_ms,
                **context
            )
        else:
            self.debug(
                f"Database query: {query_type} on {table}",
                query_type=query_type,
                table=table,
                duration_ms=duration_ms,
                **context
            )


# Create default logger instance
logger = StructuredLogger(__name__)

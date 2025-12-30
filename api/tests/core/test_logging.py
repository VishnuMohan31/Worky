"""
Tests for structured logging system.
"""
import json
import logging
from io import StringIO
from app.core.logging import (
    StructuredLogger,
    setup_logging,
    request_id_var,
    user_id_var,
    client_id_var,
    project_id_var,
    CustomJsonFormatter
)


def test_structured_logger_basic():
    """Test basic structured logger functionality."""
    logger = StructuredLogger("test")
    
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CustomJsonFormatter(environment="test"))
    
    test_logger = logging.getLogger("test")
    test_logger.handlers = [handler]
    test_logger.setLevel(logging.INFO)
    
    # Log a message
    logger.info("Test message", key="value")
    
    # Get output
    output = stream.getvalue()
    assert output, "Log output should not be empty"
    
    # Parse JSON
    log_entry = json.loads(output.strip())
    
    # Verify required fields
    assert "timestamp" in log_entry
    assert "service" in log_entry
    assert "environment" in log_entry
    assert "level" in log_entry
    assert "message" in log_entry
    assert log_entry["service"] == "worky-api"
    assert log_entry["environment"] == "test"
    assert log_entry["level"] == "INFO"
    assert "Test message" in log_entry["message"]


def test_context_variables():
    """Test that context variables are included in logs."""
    logger = StructuredLogger("test")
    
    # Set context variables
    request_id_var.set("test-request-id")
    user_id_var.set("test-user-id")
    client_id_var.set("test-client-id")
    project_id_var.set("test-project-id")
    
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CustomJsonFormatter(environment="test"))
    
    test_logger = logging.getLogger("test")
    test_logger.handlers = [handler]
    test_logger.setLevel(logging.INFO)
    
    # Log a message
    logger.info("Test with context")
    
    # Parse output
    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    
    # Verify context variables
    assert log_entry["request_id"] == "test-request-id"
    assert log_entry["user_id"] == "test-user-id"
    assert log_entry["client_id"] == "test-client-id"
    assert log_entry["project_id"] == "test-project-id"
    
    # Clean up
    request_id_var.set("")
    user_id_var.set("")
    client_id_var.set("")
    project_id_var.set("")


def test_log_levels():
    """Test different log levels."""
    logger = StructuredLogger("test")
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CustomJsonFormatter(environment="test"))
    
    test_logger = logging.getLogger("test")
    test_logger.handlers = [handler]
    test_logger.setLevel(logging.DEBUG)
    
    # Test each level
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Parse all log entries
    output = stream.getvalue()
    log_entries = [json.loads(line) for line in output.strip().split('\n')]
    
    assert len(log_entries) == 5
    assert log_entries[0]["level"] == "DEBUG"
    assert log_entries[1]["level"] == "INFO"
    assert log_entries[2]["level"] == "WARNING"
    assert log_entries[3]["level"] == "ERROR"
    assert log_entries[4]["level"] == "CRITICAL"


def test_log_activity():
    """Test log_activity method."""
    logger = StructuredLogger("test")
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CustomJsonFormatter(environment="test"))
    
    test_logger = logging.getLogger("test")
    test_logger.handlers = [handler]
    test_logger.setLevel(logging.INFO)
    
    # Log activity
    logger.log_activity(
        action="create_task",
        entity_type="task",
        entity_id="task-123",
        task_name="Test Task"
    )
    
    # Parse output
    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    
    # Verify activity fields
    assert "User activity: create_task" in log_entry["message"]
    assert log_entry["extra"]["action"] == "create_task"
    assert log_entry["extra"]["entity_type"] == "task"
    assert log_entry["extra"]["entity_id"] == "task-123"
    assert log_entry["extra"]["task_name"] == "Test Task"


def test_log_api_request():
    """Test log_api_request method."""
    logger = StructuredLogger("test")
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(CustomJsonFormatter(environment="test"))
    
    test_logger = logging.getLogger("test")
    test_logger.handlers = [handler]
    test_logger.setLevel(logging.INFO)
    
    # Log API request
    logger.log_api_request(
        method="POST",
        path="/api/v1/tasks",
        status_code=201,
        duration_ms=125.5
    )
    
    # Parse output
    output = stream.getvalue()
    log_entry = json.loads(output.strip())
    
    # Verify request fields
    assert "API request: POST /api/v1/tasks" in log_entry["message"]
    assert log_entry["extra"]["method"] == "POST"
    assert log_entry["extra"]["path"] == "/api/v1/tasks"
    assert log_entry["extra"]["status_code"] == 201
    assert log_entry["extra"]["duration_ms"] == 125.5

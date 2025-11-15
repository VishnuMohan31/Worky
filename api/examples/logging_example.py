"""
Example demonstrating the structured logging system.

Run this script to see structured JSON logs in action.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.logging import (
    setup_logging,
    StructuredLogger,
    request_id_var,
    user_id_var,
    client_id_var,
    project_id_var
)
import uuid

# Setup logging
setup_logging(log_level="INFO", environment="example")

# Create logger
logger = StructuredLogger(__name__)

def simulate_api_request():
    """Simulate an API request with context."""
    # Set context variables (normally done by middleware)
    request_id_var.set(str(uuid.uuid4()))
    user_id_var.set("user-12345")
    client_id_var.set("client-67890")
    project_id_var.set("project-abcde")
    
    # Log incoming request
    logger.info(
        "Incoming API request",
        method="POST",
        path="/api/v1/tasks",
        query_params={"status": "active"}
    )
    
    # Log user activity
    logger.log_activity(
        action="create_task",
        entity_type="task",
        entity_id="task-xyz123",
        task_name="Implement structured logging",
        assigned_to="user-12345"
    )
    
    # Log database query
    logger.log_database_query(
        query_type="INSERT",
        table="tasks",
        duration_ms=45.2,
        rows_affected=1
    )
    
    # Log API response
    logger.log_api_request(
        method="POST",
        path="/api/v1/tasks",
        status_code=201,
        duration_ms=125.5
    )
    
    # Log a warning
    logger.warning(
        "Task deadline approaching",
        task_id="task-xyz123",
        days_remaining=2
    )
    
    # Clean up context
    request_id_var.set("")
    user_id_var.set("")
    client_id_var.set("")
    project_id_var.set("")


def simulate_error():
    """Simulate an error scenario."""
    request_id_var.set(str(uuid.uuid4()))
    
    try:
        # Simulate an error
        raise ValueError("Invalid task status")
    except Exception as e:
        logger.error(
            "Failed to create task",
            error=str(e),
            error_type=type(e).__name__,
            task_data={"name": "Test Task", "status": "invalid"}
        )
    
    request_id_var.set("")


def main():
    """Run logging examples."""
    print("=" * 80)
    print("Structured Logging Examples")
    print("=" * 80)
    print()
    
    print("Example 1: Simulating API Request")
    print("-" * 80)
    simulate_api_request()
    print()
    
    print("Example 2: Simulating Error")
    print("-" * 80)
    simulate_error()
    print()
    
    print("=" * 80)
    print("All logs are in JSON format for easy parsing and analysis!")
    print("=" * 80)


if __name__ == "__main__":
    main()

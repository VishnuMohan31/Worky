# Structured Logging System

## Overview

The Worky API implements a comprehensive structured logging system that outputs JSON-formatted logs with request tracking, context variables, and integration with external log aggregation systems like Loki.

## Features

- **JSON Output**: All logs are formatted as JSON for easy parsing and analysis
- **Request ID Tracking**: Every request gets a unique UUID for tracing across services
- **Context Variables**: Automatic inclusion of user_id, client_id, project_id when available
- **Structured Fields**: Consistent log structure with timestamp, service, environment, level, message, and context
- **File and Console Output**: Logs can be written to both console (stdout) and file
- **Volume Mounts**: Logs are persisted to host filesystem via Docker volumes

## Log Format

Each log entry follows this structure (as per Requirement 9.4):

```json
{
  "timestamp": "2025-11-13T10:30:45.123456Z",
  "service": "worky-api",
  "environment": "development",
  "level": "INFO",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid",
  "client_id": "client-uuid",
  "project_id": "project-uuid",
  "action": "create_task",
  "message": "Task created successfully",
  "duration": 125.5,
  "context": {
    "task_id": "task-uuid",
    "task_name": "Implement feature X"
  }
}
```

## Configuration

### Environment Variables

Configure logging via environment variables:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Optional: Write logs to file (in addition to console)
LOG_FILE=/app/logs/worky-api.log

# Environment name (included in every log entry)
ENVIRONMENT=development
```

### Docker Compose

The API service is configured with log volume mounts:

```yaml
api:
  volumes:
    - ./volumes/api-logs:/app/logs
  environment:
    LOG_LEVEL: INFO
    LOG_FILE: /app/logs/worky-api.log
    ENVIRONMENT: development
```

## Usage

### Basic Logging

```python
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)

# Simple log messages
logger.info("User logged in")
logger.warning("Rate limit approaching")
logger.error("Database connection failed")

# Log with context
logger.info(
    "Task created",
    task_id="task-123",
    task_name="Implement feature",
    assigned_to="user-456"
)
```

### Specialized Logging Methods

```python
# Log API requests (automatically called by middleware)
logger.log_api_request(
    method="POST",
    path="/api/v1/tasks",
    status_code=201,
    duration_ms=125.5
)

# Log user activity
logger.log_activity(
    action="create_task",
    entity_type="task",
    entity_id="task-123",
    task_name="Implement feature"
)

# Log database queries
logger.log_database_query(
    query_type="INSERT",
    table="tasks",
    duration_ms=45.2
)
```

### Context Variables

Context variables are automatically set by the logging middleware and included in all logs:

```python
from app.core.logging import request_id_var, user_id_var, client_id_var, project_id_var

# These are set automatically by middleware
request_id_var.set("550e8400-e29b-41d4-a716-446655440000")
user_id_var.set("user-uuid")
client_id_var.set("client-uuid")
project_id_var.set("project-uuid")

# All subsequent logs will include these values
logger.info("Processing request")  # Will include all context variables
```

## Middleware

### LoggingMiddleware

The `LoggingMiddleware` automatically:

1. Generates a unique request ID for each request
2. Extracts user and client information from authenticated requests
3. Logs incoming requests with method, path, and query parameters
4. Logs outgoing responses with status code and duration
5. Adds `X-Request-ID` header to responses
6. Detects and logs slow requests (>2 seconds)

Example log output from middleware:

```json
{
  "timestamp": "2025-11-13T10:30:45.123456Z",
  "service": "worky-api",
  "environment": "production",
  "level": "INFO",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "client_id": "client-456",
  "message": "API request: POST /api/v1/tasks",
  "method": "POST",
  "path": "/api/v1/tasks",
  "status_code": 201,
  "duration_ms": 125.5
}
```

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems (e.g., database queries)
- **INFO**: General informational messages (e.g., API requests, user actions)
- **WARNING**: Warning messages (e.g., slow queries, rate limit approaching)
- **ERROR**: Error messages (e.g., failed operations, exceptions)
- **CRITICAL**: Critical issues requiring immediate attention

## Integration with Loki

Logs can be shipped to Loki for centralized log aggregation:

1. Configure Loki URL in environment:
   ```bash
   LOKI_URL=http://loki:3100
   ```

2. Use Promtail or Docker logging driver to ship logs to Loki

3. Query logs in Grafana using LogQL:
   ```logql
   {service="worky-api"} | json | request_id="550e8400-e29b-41d4-a716-446655440000"
   ```

## Best Practices

1. **Use Appropriate Log Levels**: Don't log everything at INFO level
2. **Include Context**: Add relevant context variables to help with debugging
3. **Avoid Sensitive Data**: Never log passwords, tokens, or PII
4. **Use Structured Fields**: Add context as keyword arguments, not in the message string
5. **Log Exceptions**: Always log exceptions with full stack traces

```python
# Good
logger.info("Task created", task_id=task.id, user_id=user.id)

# Bad
logger.info(f"Task {task.id} created by user {user.id}")
```

## Troubleshooting

### Logs Not Appearing

1. Check LOG_LEVEL environment variable
2. Verify log file path is writable
3. Check Docker volume mounts are configured correctly

### Missing Context Variables

Context variables are only set by middleware for HTTP requests. For background tasks or CLI commands, you need to set them manually:

```python
from app.core.logging import request_id_var
import uuid

request_id_var.set(str(uuid.uuid4()))
```

### Performance Impact

Structured logging has minimal performance impact. However:

- Avoid logging in tight loops
- Use DEBUG level for verbose logging
- Consider log sampling for high-traffic endpoints

## Requirements Compliance

This implementation satisfies:

- **Requirement 9.3**: Records all CRUD operations with correlation IDs
- **Requirement 9.4**: Stores structured JSON logs with all required fields
- **Requirement 10.4**: Mounts logs as volumes outside Docker containers

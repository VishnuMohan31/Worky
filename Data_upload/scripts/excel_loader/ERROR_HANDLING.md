# Error Handling Documentation

## Overview

This document describes the comprehensive error handling strategy implemented in the Excel Data Loader. The error handling follows a layered approach with specific error types, structured responses, and detailed logging.

## Error Categories

### 1. File Errors

**Location**: `excel_parser.py`, `excel_loader_app.py`

**Types**:
- `FileNotFoundError`: File does not exist at specified path
- `PermissionError`: Insufficient permissions to read file
- `ValueError`: Invalid file format (not .xlsx or .xls)
- `Exception`: Corrupted or unreadable Excel file

**Handling**:
- Validate file path before processing
- Check file existence and readability
- Validate file type and size
- Return structured error response with HTTP 400/413 status
- Log error with full stack trace

**Example**:
```python
try:
    self.workbook = openpyxl.load_workbook(file_path, data_only=True)
except FileNotFoundError as e:
    error_msg = f"Excel file not found: {file_path}"
    logger.error(error_msg, exc_info=True)
    raise FileNotFoundError(error_msg) from e
```

### 2. Data Validation Errors

**Location**: `data_mapper.py`, `import_orchestrator.py`

**Types**:
- Missing required parent references
- Invalid data type conversions
- Out-of-range values (dates, numbers)
- Empty or malformed data

**Handling**:
- Collect as warnings when non-critical
- Use default values where appropriate
- Log conversion failures with row/column information
- Continue processing other records
- Set field to NULL on conversion failure

**Example**:
```python
try:
    converted_value = self._convert_value(db_field, value)
except Exception as e:
    logger.error(f"Error converting value for field '{db_field}': {str(e)}")
    mapped_data[db_field] = None  # Use NULL on conversion error
```

### 3. Database Errors

**Location**: `database_writer.py`, `hierarchy_builder.py`

**Types**:
- `IntegrityError`: Constraint violations (foreign keys, unique constraints)
- `SQLAlchemyError`: Connection failures, query errors
- Transaction deadlocks
- Timeout errors

**Handling**:
- Wrap all database operations in try-catch blocks
- Automatic transaction rollback on any error
- Detailed error logging with query context
- Return HTTP 500 status for database errors
- Preserve partial import counts for debugging

**Example**:
```python
try:
    await self.db.commit()
    logger.info("Transaction committed successfully")
except SQLAlchemyError as e:
    error_msg = f"Failed to commit transaction: {str(e)}"
    logger.error(error_msg, exc_info=True)
    await self.db.rollback()
    raise SQLAlchemyError(error_msg) from e
```

### 4. Business Logic Errors

**Location**: `hierarchy_builder.py`, `import_orchestrator.py`

**Types**:
- Unresolved user references
- Missing parent entities
- Invalid hierarchical relationships
- Circular dependencies

**Handling**:
- Log as warnings for non-critical issues
- Skip records with missing required parents
- Use default values for optional references
- Continue processing other records
- Include in warnings list in response

**Example**:
```python
user_id = await self.hierarchy.resolve_user_reference(user_name)
if not user_id:
    self.warnings.append(f"User '{user_name}' not found, assignment set to NULL")
    mapped_data['assigned_to'] = None
```

## Error Response Structure

All errors are returned in a structured format:

```python
{
    "success": false,
    "message": "Import failed: Database connection error",
    "summary": {
        "projects": 5,
        "usecases": 0,
        "user_stories": 0,
        "tasks": 0,
        "subtasks": 0
    },
    "warnings": [
        "User 'John Doe' not found, task assignment set to NULL",
        "Unmapped columns in projects: completion_percentage, custom_field"
    ],
    "errors": [
        "Failed to connect to database",
        "Transaction rolled back"
    ],
    "duration_seconds": 2.5
}
```

## Transaction Management

### Commit Strategy

1. All imports execute within a single database transaction
2. Transaction is committed only if ALL critical operations succeed
3. Warnings do not prevent commit
4. Errors trigger automatic rollback

### Rollback Strategy

1. Automatic rollback on any critical error
2. Rollback on commit failure
3. Nested try-catch to handle rollback failures
4. Log all rollback attempts and results

**Example**:
```python
try:
    await self.writer.commit_transaction()
except Exception as e:
    logger.error(f"Commit failed: {str(e)}")
    try:
        await self.writer.rollback_transaction()
    except Exception as rollback_error:
        logger.error(f"Rollback also failed: {str(rollback_error)}")
    raise
```

## Logging Strategy

### Log Levels

- **DEBUG**: Individual record processing, ID mappings, cache hits
- **INFO**: Import progress, sheet processing, transaction commits
- **WARNING**: Non-critical issues, unmapped columns, missing references
- **ERROR**: Critical failures, database errors, transaction rollbacks

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Exception Logging

All exceptions are logged with full stack traces using `exc_info=True`:

```python
logger.error(error_msg, exc_info=True)
```

## Error Recovery

### Partial Import Handling

- Each entity type (projects, usecases, etc.) is imported independently
- Failure in one entity type does not stop processing of others
- Partial import counts are tracked and reported
- Final decision to commit or rollback based on error severity

### Retry Strategy

- No automatic retries (to prevent duplicate data)
- User must fix issues and re-run import
- Transaction rollback ensures clean state for retry

## Validation Checks

### Pre-Import Validation

1. File path validation
2. File existence check
3. File type validation (.xlsx, .xls)
4. File size validation (max 50MB)
5. File readability check

### During Import Validation

1. Sheet existence checks
2. Header validation
3. Row data validation
4. Parent entity existence checks
5. Foreign key validation
6. Data type validation

### Post-Import Validation

1. Record count verification
2. Relationship integrity checks
3. Unmapped column reporting

## Error Messages

### User-Friendly Messages

All error messages are designed to be:
- Clear and actionable
- Include context (row number, column name, entity type)
- Suggest potential solutions where applicable
- Avoid technical jargon in user-facing messages

### Technical Messages

Detailed technical information is:
- Logged to application logs
- Included in error response for debugging
- Contains full stack traces
- Includes query context and parameters

## Testing Error Handling

### Unit Tests

Test individual error scenarios:
- Invalid file paths
- Corrupted Excel files
- Invalid data types
- Missing required fields
- Constraint violations

### Integration Tests

Test error propagation:
- Transaction rollback on errors
- Partial import handling
- Error response structure
- Logging output

### Edge Cases

Test boundary conditions:
- Empty files
- Very large files
- Missing sheets
- Circular references
- Duplicate records

## Best Practices

1. **Always use try-catch blocks** around external operations (file I/O, database, network)
2. **Log before raising** to ensure error is captured even if exception is caught upstream
3. **Use specific exception types** to enable targeted error handling
4. **Include context** in error messages (row numbers, entity names, field names)
5. **Clean up resources** in finally blocks (close files, connections)
6. **Validate early** to fail fast and provide clear feedback
7. **Use structured responses** for consistent error reporting
8. **Test error paths** as thoroughly as success paths

## Monitoring and Debugging

### Key Metrics

- Import success rate
- Average import duration
- Error frequency by type
- Warning frequency by type
- Records processed per second

### Debug Information

When debugging import issues, check:
1. Application logs for detailed error traces
2. Import response for summary and warnings
3. Database state (partial imports)
4. Excel file structure and data
5. Environment configuration

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| File not found | Incorrect path or file moved | Verify file path and permissions |
| Invalid file format | Wrong file type or corrupted | Ensure file is valid .xlsx |
| Database connection error | Database not running or wrong config | Check database status and connection string |
| Constraint violation | Duplicate data or invalid references | Review data for duplicates and valid references |
| Transaction timeout | Large file or slow database | Increase timeout or process in smaller batches |

## Requirements Coverage

This error handling implementation satisfies the following requirements:

- **Requirement 1.3**: File validation and error handling
- **Requirement 4.4**: Data type conversion error handling
- **Requirement 8.1**: Transaction management
- **Requirement 8.2**: Rollback on errors
- **Requirement 8.5**: Detailed error messages

## Future Enhancements

Potential improvements to error handling:

1. **Retry mechanism** with exponential backoff for transient errors
2. **Partial commit** option for large imports (commit per entity type)
3. **Error recovery** suggestions based on error type
4. **Validation report** before import (dry-run mode)
5. **Error aggregation** to group similar errors
6. **Email notifications** for import failures
7. **Metrics dashboard** for monitoring import health

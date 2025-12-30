# Excel Loader Logging Implementation

## Overview

The Excel Loader uses the existing Worky structured logging setup to provide comprehensive logging throughout the import process. All logs are output in JSON format for easy parsing and analysis.

## Requirements Addressed

- **Requirement 1.4**: Import progress feedback and logging
- **Requirement 3.2**: Unmapped column warnings
- **Requirement 6.4**: Unmatched user reference logging

## Logging Configuration

### Setup

Logging is configured automatically when the Excel Loader application starts. The configuration uses the Worky API's structured logging setup:

```python
from logging_utils import configure_logging

configure_logging(
    log_level="INFO",
    log_file="logs/excel_loader.log"
)
```

### Environment Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
- `EXCEL_LOADER_LOG_FILE`: Path to log file - default: logs/excel_loader.log
- `ENVIRONMENT`: Environment name (development, production) - default: development

## Log Levels

### INFO Level
Used for:
- Import progress updates (sheet processing, record counts)
- Successful operations (file loaded, transaction committed)
- Import summary with statistics
- Record counts by entity type

Example:
```json
{
  "timestamp": "2025-11-30T16:42:38.612228Z",
  "level": "INFO",
  "name": "import_orchestrator",
  "message": "Starting import from file: data.xlsx",
  "service": "worky-api",
  "environment": "development",
  "file_path": "data.xlsx",
  "file_size_mb": 2.5
}
```

### WARNING Level
Used for:
- Unmapped columns in Excel sheets
- Missing user references
- Data quality issues (invalid dates, conversion failures)
- Non-critical errors (skipped rows)
- Missing sheets

Example:
```json
{
  "timestamp": "2025-11-30T16:42:38.612579Z",
  "level": "WARNING",
  "name": "data_mapper",
  "message": "Unmapped columns in projects sheet: completion_percentage, extra_field",
  "service": "worky-api",
  "environment": "development",
  "entity_type": "projects",
  "unmapped_columns": ["completion_percentage", "extra_field"],
  "unmapped_count": 2
}
```

### ERROR Level
Used for:
- Import failures
- Database errors
- File processing errors
- Critical validation failures
- Transaction rollbacks

Example:
```json
{
  "timestamp": "2025-11-30T16:42:38.612622Z",
  "level": "ERROR",
  "name": "database_writer",
  "message": "Failed to insert project row 15: constraint violation",
  "service": "worky-api",
  "environment": "development",
  "entity_type": "projects",
  "row_number": 15,
  "exc_info": true
}
```

### DEBUG Level
Used for:
- Detailed processing information
- Individual record processing
- Cache hits/misses
- ID mappings

## Component Logging

### Excel Parser (`excel_parser.py`)

Logs:
- File loading and validation
- Sheet discovery and data extraction
- Row counts and column headers
- File errors and corruption issues

Key log messages:
- `"Loading Excel file: {file_path}"`
- `"Successfully loaded workbook with {count} sheets"`
- `"Sheet '{name}': Found {columns} columns, {rows} data rows"`
- `"Sheet '{name}' not found in workbook"`

### Data Mapper (`data_mapper.py`)

Logs:
- Column mapping operations
- Type conversion warnings
- Unmapped columns (WARNING level)
- Data validation issues

Key log messages:
- `"Unmapped columns in {entity_type} sheet: {columns}"`
- `"Failed to parse date string: '{value}'"`
- `"Failed to convert string to number: {value}"`

### Hierarchy Builder (`hierarchy_builder.py`)

Logs:
- Client and program creation/lookup
- User reference resolution
- ID mapping operations
- Missing user warnings (WARNING level)

Key log messages:
- `"Found existing client: {name}"`
- `"Created new client: {name}"`
- `"User reference not found: '{identifier}'"`
- `"Resolved user reference '{identifier}' to user ID: {id}"`

### Database Writer (`database_writer.py`)

Logs:
- Insert operations and batch processing
- Transaction commits and rollbacks
- Record counts by entity type
- Database errors (ERROR level)

Key log messages:
- `"Inserted {entity_type} with ID: {id}"`
- `"Processing batch {num}/{total} for {entity_type}"`
- `"Committing transaction"`
- `"Transaction rolled back"`

### Import Orchestrator (`import_orchestrator.py`)

Logs:
- Overall import progress
- Sheet processing status
- Import duration and statistics
- Final summary with all counts

Key log messages:
- `"Starting import from file: {file_path}"`
- `"Starting {entity_type} import"`
- `"{Entity_type} import completed: {count} records"`
- `"Import completed successfully in {duration}s"`

## Import Progress Logging

The orchestrator logs progress at multiple levels:

1. **File Level**: File size, sheet count
2. **Sheet Level**: Processing start/end, record counts
3. **Batch Level**: Batch processing progress (for large imports)
4. **Summary Level**: Final statistics with duration

Example progress sequence:
```
INFO: Starting import from file: data.xlsx (2.5MB, 5 sheets)
INFO: Starting projects import
INFO: Found 50 projects to import
INFO: Projects import completed: 50 records (2.3s)
INFO: Starting usecases import
INFO: Found 120 usecases to import
INFO: Usecases import completed: 120 records (3.1s)
...
INFO: Import completed successfully in 15.8s: 385 total records
```

## Unmapped Column Logging

Unmapped columns are logged at WARNING level with full details:

```json
{
  "level": "WARNING",
  "message": "Unmapped columns in projects sheet: completion_percentage, custom_field",
  "entity_type": "projects",
  "unmapped_columns": ["completion_percentage", "custom_field"],
  "unmapped_count": 2
}
```

This helps administrators:
- Identify columns that aren't being imported
- Update column mappings if needed
- Verify data completeness

## Missing User Reference Logging

When user references cannot be resolved, warnings are logged:

```json
{
  "level": "WARNING",
  "message": "User reference not found: 'john.doe@example.com'",
  "user_identifier": "john.doe@example.com",
  "lookup_type": "user_resolution"
}
```

Summary of unmatched users is also included in the import warnings list.

## Import Duration Logging

Every import logs its total duration:

```json
{
  "level": "INFO",
  "message": "Import completed successfully in 45.50s",
  "duration_seconds": 45.5,
  "total_records": 385,
  "summary": {
    "clients": 2,
    "programs": 2,
    "projects": 10,
    "usecases": 25,
    "user_stories": 50,
    "tasks": 100,
    "subtasks": 200
  }
}
```

## Log File Location

By default, logs are written to:
- **File**: `logs/excel_loader.log`
- **Console**: stdout (JSON format)

The log file path can be configured via the `EXCEL_LOADER_LOG_FILE` environment variable.

## Structured Logging Benefits

1. **Machine Readable**: JSON format for easy parsing
2. **Contextual**: Each log includes relevant context (entity_type, counts, etc.)
3. **Searchable**: Easy to filter by level, component, or context
4. **Consistent**: Same format as main Worky API logs
5. **Traceable**: Includes timestamps and service information

## Monitoring and Alerting

The structured logs can be used for:

1. **Performance Monitoring**: Track import durations
2. **Error Detection**: Alert on ERROR level logs
3. **Data Quality**: Monitor WARNING counts for data issues
4. **Usage Analytics**: Track import frequency and sizes
5. **Debugging**: Detailed context for troubleshooting

## Example Log Analysis Queries

Using `jq` to analyze logs:

```bash
# Count imports by status
cat logs/excel_loader.log | jq -r 'select(.message | contains("Import completed")) | .message'

# Find all warnings
cat logs/excel_loader.log | jq 'select(.level == "WARNING")'

# Get import durations
cat logs/excel_loader.log | jq 'select(.duration_seconds) | {duration: .duration_seconds, records: .total_records}'

# Find unmapped columns
cat logs/excel_loader.log | jq 'select(.unmapped_columns) | {entity: .entity_type, columns: .unmapped_columns}'

# Find missing user references
cat logs/excel_loader.log | jq 'select(.lookup_type == "user_resolution") | .user_identifier'
```

## Testing

Run the logging test suite to verify all logging is working:

```bash
python Data_upload/scripts/excel_loader/test_logging.py
```

This tests:
- Logging configuration
- Logger creation for all components
- All log levels (INFO, WARNING, ERROR, DEBUG)
- Import progress logging
- Import summary logging
- Component-specific logging

## Best Practices

1. **Use appropriate log levels**: INFO for progress, WARNING for data issues, ERROR for failures
2. **Include context**: Always add relevant context fields (entity_type, counts, IDs)
3. **Log at key points**: Start/end of operations, before/after critical steps
4. **Avoid sensitive data**: Don't log passwords, tokens, or PII
5. **Keep messages concise**: Clear, actionable messages
6. **Use structured data**: Add context as fields, not in message text

# Excel Data Loader Service

A FastAPI-based service for importing hierarchical project data from Excel files into the Worky database.

## Overview

The Excel Data Loader provides a REST API endpoint for bulk-importing project tracking data from Excel files. It handles:

- Multiple entity types (Projects, Usecases, User Stories, Tasks, Subtasks)
- Hierarchical relationships between entities
- Schema mapping and data type conversions
- Missing column handling with intelligent defaults
- User reference resolution
- Transaction-based imports (all-or-nothing)

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (Worky database)
- Access to the Worky database credentials

## Installation

1. **Navigate to the loader directory:**
   ```bash
   cd Data_upload/scripts/excel_loader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your database connection:
   ```env
   # Database Configuration
   DATABASE_HOST=localhost
   DATABASE_PORT=5437
   DATABASE_NAME=worky
   DATABASE_USER=worky_user
   DATABASE_PASSWORD=worky_password
   
   # File Upload Configuration
   EXCEL_UPLOAD_MAX_SIZE=52428800  # 50MB in bytes
   EXCEL_IMPORT_TIMEOUT=300        # 5 minutes
   ```

## Running the Service

### Option 1: Using the startup script (Recommended)

```bash
./Data_upload/scripts/start_loader.sh
```

The service will start on `http://localhost:8001` by default.

You can customize the port and host:
```bash
EXCEL_LOADER_PORT=8002 EXCEL_LOADER_HOST=0.0.0.0 ./Data_upload/scripts/start_loader.sh
```

### Option 2: Using Python directly

```bash
cd Data_upload/scripts/excel_loader
python excel_loader_app.py
```

### Option 3: Using uvicorn

```bash
cd Data_upload/scripts/excel_loader
uvicorn excel_loader_app:app --host 0.0.0.0 --port 8001 --reload
```

## Using the API

### Health Check

Check if the service is running:

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "service": "excel-loader",
  "version": "1.0.0"
}
```

### Import Excel File

#### Using curl:

```bash
curl -X POST http://localhost:8001/api/import \
  -F "file=@/path/to/your/file.xlsx" \
  -H "Content-Type: multipart/form-data"
```

#### Using the test script:

```bash
python Data_upload/scripts/excel_loader/test_import_endpoint.py \
  Data_upload/data/Project\ Tracking\ Automation.xlsx
```

#### Using Python requests:

```python
import requests

with open('path/to/file.xlsx', 'rb') as f:
    files = {'file': ('filename.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    response = requests.post('http://localhost:8001/api/import', files=files)
    result = response.json()
    print(result)
```

### Response Format

#### Successful Import (No Warnings)
```json
{
  "success": true,
  "message": "Import completed successfully. Imported 125 total records.",
  "summary": {
    "clients": 2,
    "programs": 2,
    "projects": 5,
    "usecases": 15,
    "user_stories": 30,
    "tasks": 50,
    "subtasks": 21
  },
  "warnings": [],
  "errors": [],
  "duration_seconds": 8.32
}
```

#### Successful Import (With Warnings)
```json
{
  "success": true,
  "message": "Import completed successfully with warnings. Imported 125 total records.",
  "summary": {
    "clients": 2,
    "programs": 2,
    "projects": 5,
    "usecases": 15,
    "user_stories": 30,
    "tasks": 50,
    "subtasks": 21
  },
  "warnings": [
    "Sheet 'Team Members' not found, skipping",
    "Unmapped columns in Projects sheet: completion_percentage, extra_field, custom_column",
    "Unmapped columns in Tasks sheet: completion_percentage",
    "User 'John Doe' not found in database, task T001 assignment set to NULL",
    "User 'jane.smith@example.com' not found in database, user story US005 owner set to NULL",
    "Row 15 in Tasks sheet: Invalid date format for 'due_date', using NULL",
    "Client 'New Client Corp' created automatically",
    "Program 'New Client Corp - Imported Projects' created automatically"
  ],
  "errors": [],
  "duration_seconds": 12.45
}
```

#### Failed Import (File Error)
```json
{
  "success": false,
  "message": "Import failed: Invalid Excel file",
  "summary": {},
  "warnings": [],
  "errors": [
    "Failed to read Excel file: File is not a zip file",
    "Please ensure the file is a valid .xlsx or .xls file"
  ],
  "duration_seconds": 0.12
}
```

#### Failed Import (Database Error)
```json
{
  "success": false,
  "message": "Import failed: Database connection error",
  "summary": {},
  "warnings": [],
  "errors": [
    "Failed to connect to database at localhost:5437",
    "Connection refused - ensure PostgreSQL is running",
    "Transaction rolled back - no changes made to database"
  ],
  "duration_seconds": 0.5
}
```

#### Failed Import (Data Validation Error)
```json
{
  "success": false,
  "message": "Import failed: Missing required sheet",
  "summary": {},
  "warnings": [
    "Sheet 'Instructions' found but not processed"
  ],
  "errors": [
    "Required sheet 'Projects' not found in Excel file",
    "Cannot proceed without Projects sheet",
    "Transaction rolled back - no changes made to database"
  ],
  "duration_seconds": 0.25
}
```

#### Failed Import (Referential Integrity Error)
```json
{
  "success": false,
  "message": "Import failed: Invalid parent reference",
  "summary": {
    "clients": 2,
    "programs": 2,
    "projects": 5
  },
  "warnings": [],
  "errors": [
    "Usecase UC001: Parent project 'P999' not found",
    "Cannot create child records without valid parent references",
    "Transaction rolled back - no changes made to database"
  ],
  "duration_seconds": 3.18
}
```

## Excel File Structure

The Excel file should contain the following sheets. The loader will process sheets in hierarchical order to maintain referential integrity.

### Required Sheets

#### Projects Sheet
**Required columns:**
- `project_name` - Name of the project
- `client_name` - Name of the client (will be created if doesn't exist)

**Optional columns:**
- `project_id` - Excel ID for referencing (auto-generated if missing)
- `descriptions` - Project description
- `project_manager` - Project manager name or email
- `status` - Project status (default: "Planning")
- `priority` - Project priority (default: "Medium")
- `start_date` - Project start date (various formats supported)
- `due_date` - Project end date (various formats supported)
- `created_date` - Creation date
- `completion_percentage` - Completion percentage (ignored, for reference only)

**Example:**
| project_id | project_name | client_name | descriptions | status | priority | start_date | due_date |
|------------|--------------|-------------|--------------|--------|----------|------------|----------|
| P001 | Website Redesign | Acme Corp | New website | Planning | High | 2024-01-15 | 2024-06-30 |

#### Usecases Sheet
**Required columns:**
- `usecase_name` - Name of the usecase
- `project_id` - Excel ID of the parent project (must match Projects sheet)

**Optional columns:**
- `usecase_id` - Excel ID for referencing (auto-generated if missing)
- `descriptions` - Usecase description
- `owner` - Owner name or email
- `status` - Usecase status (default: "Draft")
- `start_date` - Start date
- `due_date` - Due date
- `completion_percentage` - Completion percentage (ignored)

**Example:**
| usecase_id | project_id | usecase_name | descriptions | owner | status |
|------------|------------|--------------|--------------|-------|--------|
| UC001 | P001 | User Authentication | Login system | john@example.com | Draft |

#### Userstories Sheet
**Required columns:**
- `userstory_name` - Title of the user story
- `usecase_id` - Excel ID of the parent usecase (must match Usecases sheet)

**Optional columns:**
- `userstory_id` - Excel ID for referencing (auto-generated if missing)
- `project_id` - Project reference (for tracking, not used for linking)
- `description` - User story description
- `acceptance_criteria` - Acceptance criteria
- `owner` - Owner name or email
- `status` - Status (default: "Backlog")
- `start_date` - Start date
- `due_date` - Due date
- `completion_percentage` - Completion percentage (ignored)

**Example:**
| userstory_id | usecase_id | userstory_name | description | acceptance_criteria | owner | status |
|--------------|------------|----------------|-------------|---------------------|-------|--------|
| US001 | UC001 | Login Page | User login UI | User can login | jane@example.com | Backlog |

#### Tasks Sheet
**Required columns:**
- `task_name` - Title of the task
- `userstory_id` - Excel ID of the parent user story (must match Userstories sheet)

**Optional columns:**
- `task_id` - Excel ID for referencing (auto-generated if missing)
- `project_id` - Project reference (for tracking, not used for linking)
- `description` - Task description
- `owner` - Owner/assignee name or email
- `status` - Task status (default: "To Do")
- `priority` - Priority (default: "Medium")
- `start_date` - Start date
- `due_date` - Due date
- `completion_percentage` - Completion percentage (ignored)

**Example:**
| task_id | userstory_id | task_name | description | owner | status | priority |
|---------|--------------|-----------|-------------|-------|--------|----------|
| T001 | US001 | Design login form | Create UI mockup | designer@example.com | To Do | High |

#### Subtasks Sheet
**Required columns:**
- `subtask_name` - Title of the subtask
- `task_id` - Excel ID of the parent task (must match Tasks sheet)

**Optional columns:**
- `d` or `subtask_id` - Excel ID for referencing (auto-generated if missing)
- `project_id` - Project reference (for tracking, not used for linking)
- `description` - Subtask description
- `assigned to` or `assigned_to` - Assignee name or email
- `status` - Status (default: "To Do")
- `start_date` - Start date
- `due_date` - Due date
- `completion_percentage` - Completion percentage (ignored)
- `comments` - Additional comments
- `last_updated` - Last update timestamp
- `updated_by` - Last updater

**Example:**
| d | task_id | subtask_name | description | assigned to | status |
|---|---------|--------------|-------------|-------------|--------|
| ST001 | T001 | Create wireframe | Initial design | designer@example.com | To Do |

### Optional Sheets

The following sheets are ignored if present:
- `Subtasks_History` - Historical tracking data
- `Instructions` - Documentation
- `Team Members` - Team roster
- Any other sheets not listed above

### Important Notes

1. **Hierarchical Dependencies**: Sheets must be processed in order:
   - Projects (creates Clients and Programs automatically)
   - Usecases (requires Projects)
   - Userstories (requires Usecases)
   - Tasks (requires Userstories)
   - Subtasks (requires Tasks)

2. **ID Mapping**: Excel IDs (project_id, usecase_id, etc.) are used only for establishing relationships during import. The database will generate new UUIDs for all records.

3. **User References**: Names in `owner`, `assigned to`, `project_manager` columns are matched against existing users in the database by name or email (case-insensitive). Unmatched references will be set to NULL with a warning.

4. **Date Formats**: The loader supports multiple date formats:
   - ISO format: `2024-01-15`
   - US format: `01/15/2024`
   - European format: `15/01/2024`
   - Excel date numbers
   - Text dates: `January 15, 2024`

5. **Extra Columns**: Any columns not listed above will be ignored with a warning logged.

6. **Missing Columns**: Missing optional columns will use default values as specified.

## Features

### Intelligent Schema Mapping
- Automatically maps Excel column names to database fields
- Ignores unmapped columns (logs warnings)
- Applies default values for missing required fields

### Data Type Conversion
- Converts various date formats to database format
- Converts text numbers to numeric types
- Converts percentages to decimals
- Trims whitespace from text fields

### Hierarchical Relationship Management
- Creates clients and programs automatically
- Maintains parent-child relationships
- Resolves Excel IDs to database UUIDs
- Ensures referential integrity

### User Reference Resolution
- Matches user names to existing users (case-insensitive)
- Matches email addresses to users
- Sets NULL for unmatched references (with warnings)

### Transaction Safety
- All imports are transactional (all-or-nothing)
- Automatic rollback on errors
- No partial imports that leave database inconsistent

### Error Handling
- Validates file type (.xlsx, .xls only)
- Validates file size (max 50MB by default)
- Collects and reports warnings
- Collects and reports errors
- Provides detailed error messages

## API Documentation

Once the service is running, you can access:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## Troubleshooting

### Service won't start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'` or similar import errors

**Solution**: Install dependencies:
```bash
cd Data_upload/scripts/excel_loader
pip install -r requirements.txt
```

**Problem**: `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

**Solution**: Create the `.env` file:
```bash
cd Data_upload/scripts/excel_loader
cp .env.example .env
# Edit .env with your database credentials
```

**Problem**: `Address already in use` or `OSError: [Errno 48]`

**Solution**: Port 8001 is already in use. Either:
- Stop the other service using port 8001
- Use a different port: `EXCEL_LOADER_PORT=8002 ./Data_upload/scripts/start_loader.sh`

### Database connection errors

**Problem**: `Connection refused` or `could not connect to server`

**Solution**: Check your `.env` file and ensure:
- Database host and port are correct (default: `localhost:5437`)
- PostgreSQL is running: `docker ps` or `pg_isready -h localhost -p 5437`
- Network connectivity to database host

**Problem**: `FATAL: password authentication failed for user`

**Solution**: 
- Verify database credentials in `.env` file
- Ensure user has access to the database
- Check PostgreSQL `pg_hba.conf` for authentication settings

**Problem**: `FATAL: database "worky" does not exist`

**Solution**: Create the database or update `DATABASE_NAME` in `.env` to match existing database

### File upload fails

**Problem**: `413 Request Entity Too Large`

**Solution**: File exceeds size limit (default 50MB). Either:
- Reduce file size by removing unnecessary sheets or data
- Increase `EXCEL_UPLOAD_MAX_SIZE` in `.env` (value in bytes)
  ```env
  EXCEL_UPLOAD_MAX_SIZE=104857600  # 100MB
  ```

**Problem**: `400 Bad Request - Invalid file type`

**Solution**: Only `.xlsx` and `.xls` files are supported. Convert your file:
- Save as Excel Workbook (.xlsx) in Excel/LibreOffice
- Do not use CSV, ODS, or other formats

**Problem**: `422 Unprocessable Entity`

**Solution**: File parameter is missing or incorrect. Ensure:
- Using `multipart/form-data` content type
- File field name is `file`
- File is attached to request

### Import fails with errors

**Problem**: `Missing parent reference: project_id 'P001' not found`

**Solution**: Ensure Excel IDs in child records match parent records exactly:
- Check for typos in ID columns
- Ensure parent records exist in their respective sheets
- IDs are case-sensitive

Import processes sheets in this order:
1. Projects (creates clients/programs automatically)
2. Usecases (requires valid project_id from Projects sheet)
3. User Stories (requires valid usecase_id from Usecases sheet)
4. Tasks (requires valid userstory_id from Userstories sheet)
5. Subtasks (requires valid task_id from Tasks sheet)

**Problem**: `User 'John Doe' not found` warnings

**Solution**: This is a warning, not an error. The import will continue but:
- User assignments will be set to NULL
- Ensure user names/emails in Excel match existing users in database
- Check for typos or case differences
- Users must exist in database before import

**Problem**: `Transaction rolled back due to error`

**Solution**: A critical error occurred. Check the error messages:
- Database constraint violations (unique, foreign key, not null)
- Data type mismatches
- Missing required fields
- All changes are rolled back - database remains unchanged

**Problem**: `Invalid date format in row 15, column 'start_date'`

**Solution**: Date conversion failed. The loader will:
- Set the field to NULL
- Log a warning
- Continue processing
- Supported formats: ISO (2024-01-15), US (01/15/2024), European (15/01/2024)

### Import is slow

**Problem**: Large files take a long time to process

**Solution**: This is normal for large datasets (1000+ rows). The service:
- Uses batch inserts for performance (100 records per batch)
- Maintains transaction safety (all-or-nothing)
- Logs progress to stdout

Monitor the logs to see progress:
```bash
# Watch the logs in real-time
tail -f Data_upload/scripts/excel_loader/logs/excel_loader.log
```

**Performance tips:**
- Remove unnecessary sheets before import
- Remove empty rows and columns
- Split very large files into smaller batches
- Increase `EXCEL_LOADER_WORKERS` for parallel processing (use with caution)

### Import succeeds but data not visible in UI

**Problem**: Import reports success but data doesn't appear in Worky UI

**Solution**: Check the following:
1. Verify records in database:
   ```bash
   docker exec -it worky-db psql -U postgres -d worky -c "SELECT COUNT(*) FROM projects;"
   ```
2. Check if records have `is_deleted=false`
3. Verify user has permissions to view the data
4. Refresh the UI or clear browser cache
5. Check if records are associated with correct client/program

### Common Excel file issues

**Problem**: `Sheet 'Projects' not found`

**Solution**: Ensure sheet names match exactly (case-sensitive):
- Projects (not "Project" or "projects")
- Usecases (not "Use Cases" or "UseCases")
- Userstories (not "User Stories" or "UserStories")
- Tasks
- Subtasks

**Problem**: `Column 'project_name' not found in Projects sheet`

**Solution**: Ensure required columns exist with exact names:
- Check for extra spaces in column headers
- Column names are case-sensitive
- First row must contain headers

**Problem**: Import succeeds but many warnings about unmapped columns

**Solution**: This is informational only. Extra columns are ignored:
- Review warnings to ensure important columns aren't misspelled
- Remove unnecessary columns to reduce warnings
- Refer to "Excel File Structure" section for expected column names

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Excel Data Loader | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `ENVIRONMENT` | development | Environment (development/production) |
| `DATABASE_HOST` | localhost | PostgreSQL host |
| `DATABASE_PORT` | 5437 | PostgreSQL port |
| `DATABASE_NAME` | worky | Database name |
| `DATABASE_USER` | postgres | Database user |
| `DATABASE_PASSWORD` | postgres | Database password |
| `SERVICE_PORT` | 8001 | Service port |
| `SERVICE_HOST` | 0.0.0.0 | Service host |
| `EXCEL_UPLOAD_MAX_SIZE` | 52428800 | Max file size in bytes (50MB) |
| `EXCEL_IMPORT_TIMEOUT` | 300 | Import timeout in seconds (5 minutes) |
| `CORS_ORIGINS` | ["http://localhost:3007", ...] | Allowed CORS origins (JSON array) |
| `LOG_LEVEL` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FILE` | ./logs/excel_loader.log | Log file path |
| `EXCEL_LOADER_PORT` | 8001 | Alternative port variable (for startup script) |
| `EXCEL_LOADER_HOST` | 0.0.0.0 | Alternative host variable (for startup script) |
| `EXCEL_LOADER_WORKERS` | 1 | Number of uvicorn workers |

## Development

### Running Tests

Verify the application structure:
```bash
python Data_upload/scripts/excel_loader/verify_app.py
```

Test the import endpoint:
```bash
python Data_upload/scripts/excel_loader/test_import_endpoint.py <excel_file_path>
```

### Logging

The service logs to stdout with the following levels:
- `INFO`: Normal operations, progress updates
- `WARNING`: Non-critical issues (unmapped columns, missing users)
- `ERROR`: Critical errors, import failures

## Architecture

The service consists of several components:

1. **FastAPI Application** (`excel_loader_app.py`)
   - REST API endpoints
   - File upload handling
   - Request validation
   - Response formatting

2. **Import Orchestrator** (`import_orchestrator.py`)
   - Coordinates import process
   - Manages component lifecycle
   - Collects warnings and errors

3. **Excel Parser** (`excel_parser.py`)
   - Reads Excel files
   - Extracts sheet data
   - Handles missing sheets

4. **Data Mapper** (`data_mapper.py`)
   - Maps Excel columns to database fields
   - Converts data types
   - Applies default values

5. **Hierarchy Builder** (`hierarchy_builder.py`)
   - Creates/resolves clients and programs
   - Resolves user references
   - Manages ID mappings

6. **Database Writer** (`database_writer.py`)
   - Inserts records
   - Manages transactions
   - Tracks counts

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review the troubleshooting section
3. Verify your Excel file structure matches the expected format
4. Ensure database connectivity and credentials are correct

# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `Data_upload/scripts/excel_loader/`
  - Create `requirements.txt` with dependencies: fastapi, openpyxl, sqlalchemy, asyncpg, python-multipart, pydantic, python-dotenv
  - Create `.env.example` file with configuration variables
  - Create main application file `excel_loader_app.py`
  - _Requirements: 7.1, 7.4_

- [x] 2. Implement Data Mapper component
  - Create `data_mapper.py` with DataMapper class
  - Define COLUMN_MAPPINGS dictionary for all entity types (projects, usecases, user_stories, tasks, subtasks)
  - Define DEFAULT_VALUES dictionary for missing required fields
  - Implement `map_row()` method to transform Excel rows to database fields
  - Implement `convert_date()` method to handle multiple date formats
  - Implement `convert_number()` method to convert text to numeric types
  - Implement `convert_percentage()` method to convert percentages to decimals
  - Implement whitespace trimming for all text fields
  - Add logging for unmapped columns
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3. Implement Excel Parser component
  - Create `excel_parser.py` with ExcelParser class
  - Implement `__init__()` to load workbook using openpyxl
  - Implement `get_sheet_data()` to extract rows as list of dictionaries
  - Implement `get_available_sheets()` to list all sheet names
  - Handle missing sheets gracefully (return empty list)
  - Implement `close()` method to clean up resources
  - Add error handling for corrupted or invalid Excel files
  - _Requirements: 1.3, 3.1_

- [x] 4. Implement Hierarchy Builder component
  - Create `hierarchy_builder.py` with HierarchyBuilder class
  - Initialize id_mappings dictionary for tracking Excel ID to UUID mappings
  - Implement `get_or_create_client()` to find or create client by name
  - Implement `get_or_create_program()` to create default program for client
  - Implement `resolve_user_reference()` to find users by name/email (case-insensitive)
  - Implement `map_excel_id_to_db_id()` to store ID mappings
  - Implement `get_db_id_from_excel_id()` to retrieve mapped UUIDs
  - Add logging for unmatched user references
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4_

- [x] 5. Implement Database Writer component
  - Create `database_writer.py` with DatabaseWriter class
  - Initialize counts dictionary for tracking inserted records
  - Implement `insert_entity()` to insert single record and return UUID
  - Implement `batch_insert_entities()` for efficient bulk inserts
  - Implement `commit_transaction()` to commit all changes
  - Implement `rollback_transaction()` to rollback on errors
  - Implement `get_summary()` to return insertion counts
  - Add error handling for constraint violations
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 6. Implement Import Orchestrator component
  - Create `import_orchestrator.py` with ImportOrchestrator class
  - Initialize all component instances (parser, mapper, hierarchy, writer)
  - Implement `import_from_file()` main orchestration method
  - Implement `_import_projects()` to process Projects sheet
  - Implement `_import_usecases()` to process Usecases sheet
  - Implement `_import_user_stories()` to process Userstories sheet
  - Implement `_import_tasks()` to process Tasks sheet
  - Implement `_import_subtasks()` to process Subtasks sheet
  - Ensure correct hierarchical order (clients → programs → projects → usecases → user_stories → tasks → subtasks)
  - Collect warnings and errors throughout process
  - Generate ImportResponse with summary, warnings, and errors
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 8.5_

- [x] 7. Implement FastAPI application and endpoint
  - Create `excel_loader_app.py` with FastAPI app instance
  - Configure CORS for development
  - Implement database session dependency using existing config
  - Create ImportResponse Pydantic model
  - Implement POST `/api/import` endpoint with file upload
  - Add file validation (type, size limits)
  - Save uploaded file temporarily
  - Call ImportOrchestrator to process file
  - Clean up temporary file after processing
  - Return structured JSON response with results
  - Add error handling and appropriate HTTP status codes
  - _Requirements: 1.1, 1.3, 7.1_

- [x] 8. Create database models and utilities
  - Create `models.py` with Pydantic models for entity mappings (ProjectMapping, UsecaseMapping, etc.)
  - Create `db_utils.py` with database connection helper using existing config
  - Implement async session management
  - Add connection pooling configuration
  - _Requirements: 8.1_

- [x] 9. Implement comprehensive error handling
  - Add try-catch blocks for file operations
  - Add try-catch blocks for database operations
  - Implement transaction rollback on any error
  - Create structured error responses
  - Add detailed error logging
  - Handle specific error types (file errors, validation errors, database errors)
  - _Requirements: 1.3, 4.4, 8.1, 8.2, 8.5_

- [x] 10. Create README documentation
  - Create `Data_upload/scripts/README.md`
  - Document prerequisites (Python 3.9+, PostgreSQL access)
  - Provide step-by-step installation instructions
  - Document environment variable configuration
  - Provide exact command to run the loader service
  - Provide exact command to execute import via curl or Python
  - Document expected Excel file structure
  - Add troubleshooting section for common errors
  - Include example responses (success and error cases)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11. Add logging and monitoring
  - Configure logging using existing Worky logging setup
  - Add INFO level logs for import progress
  - Add WARNING level logs for data issues (unmapped columns, missing users)
  - Add ERROR level logs for failures
  - Log import duration and record counts
  - _Requirements: 1.4, 3.2, 6.4_

- [x] 12. Create startup script
  - Create `Data_upload/scripts/start_loader.sh` bash script
  - Add commands to activate virtual environment
  - Add command to start FastAPI with uvicorn
  - Make script executable
  - Add port configuration (default 8001)
  - _Requirements: 7.3_

- [ ] 13. Write unit tests
  - Create `tests/test_data_mapper.py` with tests for column mapping and type conversion
  - Create `tests/test_hierarchy_builder.py` with tests for client/program creation and user resolution
  - Create `tests/test_database_writer.py` with tests for insert operations
  - Create `tests/conftest.py` with test fixtures and database setup
  - _Requirements: All_

- [ ]* 14. Write integration tests
  - Create `tests/test_import_e2e.py` for end-to-end import testing
  - Create sample Excel file with test data
  - Test complete import flow
  - Verify database records and relationships
  - Test error scenarios (missing sheets, invalid data)
  - _Requirements: All_

- [x] 15. Test with actual Excel file
  - Run import with Project Tracking Automation.xlsx
  - Verify all sheets are processed
  - Check database for imported records
  - Validate parent-child relationships
  - Review warnings and errors
  - Verify data appears correctly in Worky UI
  - _Requirements: 1.1, 1.2, 1.5_

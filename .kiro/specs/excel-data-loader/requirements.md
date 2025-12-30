# Requirements Document

## Introduction

This feature enables administrators to bulk-load project tracking data from an Excel file into the Worky system. The Excel file contains hierarchical project data across multiple sheets (Projects, Usecases, Userstories, Tasks, Subtasks) that needs to be imported into the existing database schema. The loader must handle schema mismatches intelligently by filling missing required fields with appropriate defaults and ignoring extra columns.

## Glossary

- **Excel Loader**: The FastAPI-based service that reads Excel files and imports data into the Worky database
- **Worky System**: The existing project management platform with a hierarchical data structure
- **Admin User**: A user with administrative privileges who can execute data import operations
- **Schema Mapping**: The process of translating Excel column names to database field names
- **Default Value Strategy**: The approach for populating required database fields when Excel columns are missing

## Requirements

### Requirement 1

**User Story:** As an Admin, I want to load project tracking data from an Excel file, so that I can bulk-import existing project data into Worky

#### Acceptance Criteria

1. WHEN an Admin executes the loader script with a valid Excel file path, THE Excel Loader SHALL read all sheets (Projects, Usecases, Userstories, Tasks, Subtasks) and import the data into the corresponding database tables
2. WHEN the Excel file contains valid hierarchical data, THE Excel Loader SHALL maintain referential integrity by creating parent records before child records
3. IF the Excel file path is invalid or the file cannot be read, THEN THE Excel Loader SHALL display a clear error message and terminate without modifying the database
4. THE Excel Loader SHALL provide progress feedback showing which sheet is being processed and how many records have been imported
5. WHEN the import completes successfully, THE Excel Loader SHALL display a summary report showing the count of records imported for each entity type

### Requirement 2

**User Story:** As an Admin, I want the loader to handle missing required columns intelligently, so that I can import data even when the Excel structure doesn't perfectly match the database schema

#### Acceptance Criteria

1. WHEN a required database field has no corresponding Excel column, THE Excel Loader SHALL populate the field with an appropriate default value based on the field type and business logic
2. THE Excel Loader SHALL use "Medium" as the default priority for tasks and usecases when the priority column is missing
3. THE Excel Loader SHALL use "Planning" as the default status for projects and programs when the status column is missing
4. THE Excel Loader SHALL generate UUID values for all primary key fields
5. THE Excel Loader SHALL use the current timestamp for created_at and updated_at fields when not provided in the Excel file

### Requirement 3

**User Story:** As an Admin, I want the loader to ignore extra columns in the Excel file, so that I can use Excel files with additional tracking columns without causing import errors

#### Acceptance Criteria

1. WHEN the Excel file contains columns that do not map to database fields, THE Excel Loader SHALL skip those columns without raising errors
2. THE Excel Loader SHALL log a warning message listing all unmapped columns for each sheet
3. THE Excel Loader SHALL continue processing all mapped columns even when unmapped columns are present

### Requirement 4

**User Story:** As an Admin, I want the loader to handle data type conversions automatically, so that I don't need to manually format the Excel data to match database types

#### Acceptance Criteria

1. WHEN an Excel column contains date values in various formats, THE Excel Loader SHALL convert them to the appropriate database date/timestamp format
2. WHEN an Excel column contains numeric values stored as text, THE Excel Loader SHALL convert them to the appropriate numeric type (integer or decimal)
3. WHEN an Excel column contains percentage values, THE Excel Loader SHALL convert them to decimal format (e.g., "75%" becomes 0.75 or 75 based on database schema)
4. IF a data type conversion fails for a specific cell, THEN THE Excel Loader SHALL log the error with row and column information and use a default value or NULL as appropriate
5. THE Excel Loader SHALL trim whitespace from text values before inserting into the database

### Requirement 5

**User Story:** As an Admin, I want to create or reference existing clients and programs, so that the imported projects are properly organized within the Worky hierarchy

#### Acceptance Criteria

1. WHEN the Excel file contains a client_name that does not exist in the database, THE Excel Loader SHALL create a new client record with that name
2. WHEN the Excel file contains a client_name that already exists, THE Excel Loader SHALL reuse the existing client record
3. THE Excel Loader SHALL create a default program for each unique client to contain the imported projects
4. THE Excel Loader SHALL name the default program using the pattern "{client_name} - Imported Projects"
5. WHERE a program already exists with the same name, THE Excel Loader SHALL reuse that program

### Requirement 6

**User Story:** As an Admin, I want to map Excel user references to existing Worky users, so that task assignments and ownership are preserved during import

#### Acceptance Criteria

1. WHEN the Excel file contains user names in owner or assigned_to columns, THE Excel Loader SHALL attempt to match them to existing users by full_name or email
2. IF a user reference cannot be matched to an existing user, THEN THE Excel Loader SHALL set the assignment field to NULL and log a warning
3. THE Excel Loader SHALL perform case-insensitive matching for user names
4. THE Excel Loader SHALL log all unmatched user references in a summary report at the end of the import

### Requirement 7

**User Story:** As an Admin, I want a clear README with exact commands, so that I can execute the data load without needing to understand the implementation details

#### Acceptance Criteria

1. THE Excel Loader SHALL include a README.md file in the Data_upload/scripts directory
2. THE README SHALL contain step-by-step instructions for installing dependencies
3. THE README SHALL provide the exact command to execute the data load with the Excel file path
4. THE README SHALL document all environment variables and configuration requirements
5. THE README SHALL include troubleshooting guidance for common error scenarios

### Requirement 8

**User Story:** As an Admin, I want the loader to validate data before committing to the database, so that I can avoid partial imports that leave the database in an inconsistent state

#### Acceptance Criteria

1. THE Excel Loader SHALL use database transactions to ensure all-or-nothing imports
2. IF any critical error occurs during import, THEN THE Excel Loader SHALL roll back all changes and leave the database unchanged
3. THE Excel Loader SHALL validate that all required parent records exist before creating child records
4. THE Excel Loader SHALL validate that foreign key references are valid before inserting records
5. WHEN validation fails, THE Excel Loader SHALL display detailed error messages indicating which records failed and why

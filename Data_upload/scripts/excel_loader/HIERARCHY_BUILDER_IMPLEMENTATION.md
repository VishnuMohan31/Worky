# Hierarchy Builder Implementation

## Overview

The `HierarchyBuilder` component has been successfully implemented to manage parent-child relationships and reference resolution during the Excel import process.

## Implementation Details

### File Location
`Data_upload/scripts/excel_loader/hierarchy_builder.py`

### Class: HierarchyBuilder

#### Initialization
```python
def __init__(self, db_session: AsyncSession)
```

Initializes the hierarchy builder with:
- **db_session**: Async database session for queries and inserts
- **id_mappings**: Dictionary tracking Excel ID to database ID mappings for all entity types
- **_user_cache**: Cache for user lookups to avoid repeated queries
- **_client_cache**: Cache for client lookups
- **_program_cache**: Cache for program lookups

#### Core Methods

##### 1. get_or_create_client(client_name: str) -> str
- Performs case-insensitive lookup of client by name
- Creates new client if not found
- Returns client ID (string format like 'CLI001')
- Caches results to optimize repeated lookups
- Handles empty/None client names by using "Default Client"

**Requirements Satisfied**: 5.1, 5.2

##### 2. get_or_create_program(client_id: str, client_name: str) -> str
- Creates or retrieves program with naming pattern "{client_name} - Imported Projects"
- Performs case-insensitive lookup
- Returns program ID (string format like 'PRG001')
- Caches results for performance
- Sets default status to "Planning"

**Requirements Satisfied**: 5.3, 5.4, 5.5

##### 3. resolve_user_reference(user_identifier: str) -> Optional[str]
- Finds users by full_name or email (case-insensitive)
- Returns user ID if found, None otherwise
- Logs warning for unmatched user references
- Caches results (including failures) to avoid repeated queries
- Handles database errors gracefully

**Requirements Satisfied**: 6.1, 6.2, 6.3, 6.4

##### 4. map_excel_id_to_db_id(entity_type: str, excel_id: str, db_id: str) -> None
- Stores mapping from Excel ID to database ID
- Validates entity type and IDs
- Logs debug information for tracking
- Handles empty/None values gracefully

**Requirements Satisfied**: Task requirement for ID mapping storage

##### 5. get_db_id_from_excel_id(entity_type: str, excel_id: str) -> Optional[str]
- Retrieves database ID from Excel ID mapping
- Returns None if mapping doesn't exist
- Logs warning for missing mappings
- Validates entity type

**Requirements Satisfied**: Task requirement for ID mapping retrieval

#### Additional Helper Methods

##### get_mapping_summary() -> Dict[str, int]
- Returns count of mapped IDs by entity type
- Useful for import summary reporting

##### clear_caches() -> None
- Clears all internal caches
- Useful for testing or memory management

## Key Features

### 1. Caching Strategy
The implementation uses three levels of caching:
- **User cache**: Prevents repeated user lookups
- **Client cache**: Prevents repeated client lookups  
- **Program cache**: Prevents repeated program lookups

This significantly improves performance during large imports.

### 2. Case-Insensitive Matching
All lookups (clients, programs, users) use case-insensitive matching via SQLAlchemy's `func.lower()`.

### 3. Comprehensive Logging
- **INFO**: Successful creation/lookup of entities
- **WARNING**: Unmatched user references, missing mappings
- **ERROR**: Database errors, unexpected exceptions
- **DEBUG**: ID mappings, user resolutions

### 4. Error Handling
- Catches SQLAlchemy errors separately from general exceptions
- Logs detailed error information
- Caches failed lookups to avoid repeated queries
- Gracefully handles None/empty values

### 5. Database Integration
- Uses async SQLAlchemy sessions
- Properly flushes after inserts to get generated IDs
- Imports models locally to avoid circular dependencies
- Filters out soft-deleted records (is_deleted=False)

## Entity Type Support

The ID mapping system supports:
- clients
- programs
- projects
- usecases
- user_stories
- tasks
- subtasks
- users

## Usage Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from hierarchy_builder import HierarchyBuilder

async def import_project(db: AsyncSession, project_data: dict):
    builder = HierarchyBuilder(db)
    
    # Get or create client
    client_id = await builder.get_or_create_client("Acme Corp")
    
    # Get or create program
    program_id = await builder.get_or_create_program(client_id, "Acme Corp")
    
    # Resolve user reference
    user_id = await builder.resolve_user_reference("john.doe@example.com")
    
    # Map Excel ID to database ID
    builder.map_excel_id_to_db_id('projects', 'PRJ-001', 'PRJ123')
    
    # Later, retrieve the mapping
    db_id = builder.get_db_id_from_excel_id('projects', 'PRJ-001')
```

## Testing

A verification script has been created at:
`Data_upload/scripts/excel_loader/verify_hierarchy_builder.py`

Run with:
```bash
python Data_upload/scripts/excel_loader/verify_hierarchy_builder.py
```

The verification checks:
- ✓ All required methods exist
- ✓ Method signatures match design specification
- ✓ Async methods are properly declared
- ✓ Logging is implemented
- ✓ Unmatched user reference logging is present
- ✓ All methods have docstrings

## Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| 5.1 | `get_or_create_client()` - Creates new client if not exists |
| 5.2 | `get_or_create_client()` - Reuses existing client |
| 5.3 | `get_or_create_program()` - Creates default program |
| 5.4 | `get_or_create_program()` - Uses naming pattern |
| 5.5 | `get_or_create_program()` - Reuses existing program |
| 6.1 | `resolve_user_reference()` - Matches by name/email |
| 6.2 | `resolve_user_reference()` - Returns NULL and logs warning |
| 6.3 | `resolve_user_reference()` - Case-insensitive matching |
| 6.4 | `resolve_user_reference()` - Logs unmatched references |

## Next Steps

This component is ready to be integrated with:
1. **Import Orchestrator** - Will use HierarchyBuilder to manage relationships
2. **Database Writer** - Will use ID mappings to set foreign keys
3. **Excel Parser** - Will provide raw data for processing

## Notes

- The implementation uses string IDs (e.g., 'CLI001', 'PRG001') instead of UUIDs, matching the actual database schema
- All database operations are async for better performance
- The component is stateful (maintains caches and mappings) and should be instantiated once per import session
- Caches can be cleared if needed for memory management in very large imports

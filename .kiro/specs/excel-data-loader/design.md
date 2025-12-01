# Design Document

## Overview

The Excel Data Loader is a FastAPI-based service that enables administrators to bulk-import project tracking data from Excel files into the Worky database. The service reads hierarchical data from multiple Excel sheets (Projects, Usecases, Userstories, Tasks, Subtasks) and intelligently maps it to the existing database schema while handling missing columns, extra columns, and data type conversions.

The loader operates as a standalone FastAPI application in the `Data_upload/scripts` directory, separate from the main API but sharing the same database connection configuration. It provides a RESTful endpoint for triggering imports and uses database transactions to ensure data consistency.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Admin User     │
└────────┬────────┘
         │ HTTP POST /import
         ▼
┌─────────────────────────────────┐
│   FastAPI Excel Loader Service  │
│  ┌───────────────────────────┐  │
│  │  Import Endpoint          │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  Excel Parser             │  │
│  │  - openpyxl               │  │
│  │  - Sheet reader           │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  Data Mapper              │  │
│  │  - Column mapping         │  │
│  │  - Type conversion        │  │
│  │  - Default value strategy │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  Hierarchy Builder        │  │
│  │  - Parent-child linking   │  │
│  │  - Reference resolution   │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │  Database Writer          │  │
│  │  - Transaction management │  │
│  │  - Batch inserts          │  │
│  └───────────┬───────────────┘  │
└──────────────┼───────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   PostgreSQL Database (Worky)   │
└─────────────────────────────────┘
```

### Component Interaction Flow

1. Admin uploads Excel file via HTTP POST to `/api/import`
2. Excel Parser reads all sheets and extracts raw data
3. Data Mapper transforms Excel columns to database fields
4. Hierarchy Builder establishes parent-child relationships
5. Database Writer commits data in correct order within a transaction
6. Response returns import summary with counts and warnings

## Components and Interfaces

### 1. FastAPI Application (`excel_loader_app.py`)

**Purpose**: Main application entry point and HTTP endpoint definition

**Responsibilities**:
- Define FastAPI application and routes
- Handle file upload via multipart/form-data
- Coordinate the import process
- Return structured responses with import results

**Interface**:
```python
@app.post("/api/import")
async def import_excel_data(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
) -> ImportResponse
```

**Response Model**:
```python
class ImportResponse(BaseModel):
    success: bool
    message: str
    summary: Dict[str, int]  # Entity type -> count
    warnings: List[str]
    errors: List[str]
```

### 2. Excel Parser (`excel_parser.py`)

**Purpose**: Read and parse Excel file sheets

**Responsibilities**:
- Load Excel workbook using openpyxl
- Extract data from specific sheets
- Handle missing sheets gracefully
- Return structured data as list of dictionaries

**Key Methods**:
```python
class ExcelParser:
    def __init__(self, file_path: str):
        self.workbook = openpyxl.load_workbook(file_path)
    
    def get_sheet_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Extract all rows from a sheet as dictionaries"""
        
    def get_available_sheets(self) -> List[str]:
        """Return list of sheet names in workbook"""
    
    def close(self):
        """Close workbook"""
```

### 3. Data Mapper (`data_mapper.py`)

**Purpose**: Map Excel columns to database fields with type conversion

**Responsibilities**:
- Define column mapping rules for each entity type
- Convert data types (dates, numbers, percentages)
- Apply default values for missing required fields
- Trim whitespace and normalize text
- Log unmapped columns

**Key Methods**:
```python
class DataMapper:
    # Column mapping definitions
    COLUMN_MAPPINGS = {
        'projects': {
            'project_name': 'name',
            'descriptions': 'description',
            'client_name': '_client_name',  # Special handling
            'status': 'status',
            'priority': 'priority',
            # ... more mappings
        },
        # ... other entity types
    }
    
    DEFAULT_VALUES = {
        'projects': {
            'status': 'Planning',
            'priority': 'Medium',
        },
        # ... other entity types
    }
    
    def map_row(self, entity_type: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map Excel row to database fields"""
    
    def convert_date(self, value: Any) -> Optional[date]:
        """Convert various date formats to date object"""
    
    def convert_number(self, value: Any) -> Optional[float]:
        """Convert text numbers to float"""
    
    def convert_percentage(self, value: Any) -> Optional[float]:
        """Convert percentage to decimal"""
```

**Column Mapping Strategy**:

| Excel Column | Database Field | Conversion | Default |
|--------------|----------------|------------|---------|
| project_name | name | trim | - |
| descriptions | description | trim | "" |
| client_name | (lookup) | trim, lookup | "Default Client" |
| status | status | trim | "Planning" |
| priority | priority | trim | "Medium" |
| start_date | start_date | date parse | NULL |
| due_date | end_date | date parse | NULL |
| completion_percentage | (ignored) | - | - |

### 4. Hierarchy Builder (`hierarchy_builder.py`)

**Purpose**: Establish parent-child relationships and resolve references

**Responsibilities**:
- Create or lookup client records
- Create default programs for clients
- Link projects to programs
- Link usecases to projects
- Link user stories to usecases
- Link tasks to user stories
- Link subtasks to tasks
- Resolve user references by name/email
- Maintain ID mapping for Excel IDs to database UUIDs

**Key Methods**:
```python
class HierarchyBuilder:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.id_mappings = {
            'clients': {},
            'programs': {},
            'projects': {},
            'usecases': {},
            'user_stories': {},
            'tasks': {},
            'users': {}
        }
    
    async def get_or_create_client(self, client_name: str) -> UUID:
        """Get existing client or create new one"""
    
    async def get_or_create_program(self, client_id: UUID, client_name: str) -> UUID:
        """Get or create default program for client"""
    
    async def resolve_user_reference(self, user_name: str) -> Optional[UUID]:
        """Find user by name or email (case-insensitive)"""
    
    async def map_excel_id_to_db_id(self, entity_type: str, excel_id: str, db_id: UUID):
        """Store mapping from Excel ID to database UUID"""
    
    async def get_db_id_from_excel_id(self, entity_type: str, excel_id: str) -> Optional[UUID]:
        """Retrieve database UUID from Excel ID"""
```

### 5. Database Writer (`database_writer.py`)

**Purpose**: Write mapped data to database with transaction management

**Responsibilities**:
- Execute inserts in correct hierarchical order
- Use batch inserts for performance
- Manage database transactions
- Handle constraint violations
- Rollback on errors
- Track inserted record counts

**Key Methods**:
```python
class DatabaseWriter:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.counts = {
            'clients': 0,
            'programs': 0,
            'projects': 0,
            'usecases': 0,
            'user_stories': 0,
            'tasks': 0,
            'subtasks': 0
        }
    
    async def insert_entity(self, entity_type: str, data: Dict[str, Any]) -> UUID:
        """Insert single entity and return its UUID"""
    
    async def batch_insert_entities(self, entity_type: str, data_list: List[Dict[str, Any]]) -> List[UUID]:
        """Insert multiple entities efficiently"""
    
    async def commit_transaction(self):
        """Commit all changes"""
    
    async def rollback_transaction(self):
        """Rollback all changes"""
    
    def get_summary(self) -> Dict[str, int]:
        """Return count of inserted records by type"""
```

### 6. Import Orchestrator (`import_orchestrator.py`)

**Purpose**: Coordinate the entire import process

**Responsibilities**:
- Orchestrate all components in correct order
- Handle errors and collect warnings
- Manage transaction lifecycle
- Generate import summary

**Key Methods**:
```python
class ImportOrchestrator:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.parser = None
        self.mapper = DataMapper()
        self.hierarchy = HierarchyBuilder(db_session)
        self.writer = DatabaseWriter(db_session)
        self.warnings = []
        self.errors = []
    
    async def import_from_file(self, file_path: str) -> ImportResponse:
        """Execute complete import process"""
        
    async def _import_projects(self, sheet_data: List[Dict]):
        """Import projects sheet"""
    
    async def _import_usecases(self, sheet_data: List[Dict]):
        """Import usecases sheet"""
    
    async def _import_user_stories(self, sheet_data: List[Dict]):
        """Import user stories sheet"""
    
    async def _import_tasks(self, sheet_data: List[Dict]):
        """Import tasks sheet"""
    
    async def _import_subtasks(self, sheet_data: List[Dict]):
        """Import subtasks sheet"""
```

## Data Models

### Import Response Model
```python
class ImportResponse(BaseModel):
    success: bool
    message: str
    summary: Dict[str, int]  # {'projects': 5, 'tasks': 20, ...}
    warnings: List[str]
    errors: List[str]
    duration_seconds: float
```

### Entity Mapping Models
```python
class ProjectMapping(BaseModel):
    excel_id: Optional[str]
    name: str
    description: str = ""
    client_name: str
    status: str = "Planning"
    priority: str = "Medium"
    start_date: Optional[date]
    end_date: Optional[date]

class UsecaseMapping(BaseModel):
    excel_id: Optional[str]
    project_excel_id: str
    name: str
    description: str = ""
    status: str = "Draft"
    priority: str = "Medium"
    start_date: Optional[date]
    end_date: Optional[date]

class UserStoryMapping(BaseModel):
    excel_id: Optional[str]
    usecase_excel_id: str
    title: str
    description: str = ""
    acceptance_criteria: str = ""
    status: str = "Backlog"
    priority: str = "Medium"
    owner: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

class TaskMapping(BaseModel):
    excel_id: Optional[str]
    user_story_excel_id: str
    title: str
    description: str = ""
    status: str = "To Do"
    priority: str = "Medium"
    owner: Optional[str]
    start_date: Optional[date]
    due_date: Optional[date]

class SubtaskMapping(BaseModel):
    excel_id: Optional[str]
    task_excel_id: str
    title: str
    description: str = ""
    status: str = "To Do"
    assigned_to: Optional[str]
    start_date: Optional[date]
    due_date: Optional[date]
```

## Error Handling

### Error Categories

1. **File Errors**
   - File not found
   - Invalid Excel format
   - Corrupted file
   - Action: Return 400 Bad Request with error message

2. **Data Validation Errors**
   - Missing required parent references
   - Invalid foreign keys
   - Data type conversion failures
   - Action: Collect as warnings, use defaults where possible

3. **Database Errors**
   - Connection failures
   - Constraint violations
   - Transaction deadlocks
   - Action: Rollback transaction, return 500 Internal Server Error

4. **Business Logic Errors**
   - Circular dependencies
   - Duplicate records
   - Action: Log warning, skip record or use existing

### Error Response Format
```python
{
    "success": false,
    "message": "Import failed: Database connection error",
    "summary": {},
    "warnings": [],
    "errors": [
        "Failed to connect to database",
        "Transaction rolled back"
    ]
}
```

### Warning Examples
```python
warnings = [
    "Sheet 'Team Members' not found, skipping",
    "Column 'completion_percentage' in Projects sheet is unmapped, ignoring",
    "User 'John Doe' not found, task assignment set to NULL",
    "Row 15 in Tasks: Invalid date format for 'due_date', using NULL"
]
```

## Testing Strategy

### Unit Tests

1. **Data Mapper Tests** (`test_data_mapper.py`)
   - Test column mapping for each entity type
   - Test date conversion with various formats
   - Test number and percentage conversion
   - Test default value application
   - Test whitespace trimming

2. **Hierarchy Builder Tests** (`test_hierarchy_builder.py`)
   - Test client creation and lookup
   - Test program creation
   - Test user reference resolution
   - Test ID mapping storage and retrieval

3. **Database Writer Tests** (`test_database_writer.py`)
   - Test single entity insert
   - Test batch insert
   - Test transaction commit
   - Test transaction rollback
   - Test count tracking

### Integration Tests

1. **End-to-End Import Test** (`test_import_e2e.py`)
   - Create sample Excel file with all sheets
   - Execute full import
   - Verify all records in database
   - Verify parent-child relationships
   - Verify default values applied

2. **Error Handling Test** (`test_import_errors.py`)
   - Test with missing sheets
   - Test with invalid data types
   - Test with missing required fields
   - Test with invalid references
   - Verify rollback on errors

3. **Edge Cases Test** (`test_import_edge_cases.py`)
   - Test with empty sheets
   - Test with duplicate records
   - Test with circular references
   - Test with very large files

### Manual Testing

1. **Real Data Import**
   - Use actual Project Tracking Automation.xlsx file
   - Verify all data imported correctly
   - Check for warnings and errors
   - Validate data in UI

2. **Performance Testing**
   - Test with 1000+ rows
   - Measure import duration
   - Monitor memory usage

## Implementation Notes

### Technology Stack
- **FastAPI**: Web framework for REST API
- **openpyxl**: Excel file reading
- **SQLAlchemy**: Database ORM (async)
- **asyncpg**: PostgreSQL async driver
- **Pydantic**: Data validation and serialization
- **python-multipart**: File upload handling

### Configuration
- Reuse existing database configuration from `api/app/core/config.py`
- Add new environment variables:
  - `EXCEL_UPLOAD_MAX_SIZE`: Maximum file size (default: 50MB)
  - `EXCEL_IMPORT_TIMEOUT`: Import timeout in seconds (default: 300)

### Performance Considerations
- Use batch inserts for better performance (100 records per batch)
- Use async database operations
- Stream large Excel files if needed
- Add progress tracking for long imports

### Security Considerations
- Validate file type (only .xlsx allowed)
- Limit file size to prevent DoS
- Sanitize all input data
- Use parameterized queries to prevent SQL injection
- Require admin authentication for import endpoint

### Deployment
- Run as separate service on port 8001
- Can be deployed alongside main API
- Share database connection pool
- Use same logging configuration

# Design Document: QA Testing and Bug Management System

## Overview

This document outlines the technical design for implementing a comprehensive QA Testing and Bug Management system within the Worky project management platform. The system introduces a new "QA" menu group with Test Run Management, Test Case Management, and enhanced Bug Lifecycle features, following industry-standard practices for bug tracking, test execution, and quality metrics.

### Key Concepts

**Test Run Hierarchy:**
- Test Run can be attached to any hierarchy level: Project, Use Case, User Story, Task, or Subtask
- Test Run serves as a container for Test Cases
- Test Run ID is used to group related bugs
- Test Run types: "Misc" or "One-Timer"

**Test Case Structure:**
- Test Cases belong to a Test Run
- Failed Test Cases generate Bugs
- Test Cases have detailed steps, expected results, and actual results

**Bug Hierarchy:**
- Bugs can be created from failed Test Cases (linked to Test Run)
- Bugs can be created directly at any hierarchy level (Project, Use Case, User Story, Task, Subtask)
- Bugs track comprehensive lifecycle with assignments, status transitions, and audit trail

### Key Features

- **QA Menu Group**: New navigation section with Test Runs, Test Cases, and Bug Lifecycle sub-items
- **Test Run Management**: Create and manage test runs at any hierarchy level (Project → Subtask)
- **Test Case Management**: Create test cases within test runs with detailed steps and results
- **Enhanced Bug Tracking**: Industry-standard bug lifecycle with comprehensive categorization
- **Test-to-Bug Workflow**: Create bugs directly from failed test case executions
- **Hierarchical Bug Viewing**: View bugs at any hierarchy level with descendant aggregation
- **Metrics & Reporting**: Comprehensive dashboards with KPIs, trends, and analytics
- **Comments & Collaboration**: Threaded discussions on bugs and test cases with @mentions
- **Dummy Data Generation**: Realistic test data for development and testing

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Test Cases   │  │ Bug Lifecycle│  │ Bug Metrics  │     │
│  │ Page         │  │ Page         │  │ Dashboard    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Test Case    │  │ Bug Form     │  │ Comments     │     │
│  │ Execution    │  │ Component    │  │ Component    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Test Case    │  │ Bug          │  │ Test         │     │
│  │ Endpoints    │  │ Endpoints    │  │ Execution    │     │
│  │              │  │              │  │ Endpoints    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Comment      │  │ Metrics      │  │ Notification │     │
│  │ Endpoints    │  │ Endpoints    │  │ Service      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  test_cases │ test_executions │ test_case_bugs              │
│  bugs (extended) │ bug_comments │ test_case_comments        │
│  bug_attachments │ test_runs │ bug_status_history          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: React, TypeScript, TailwindCSS, React Query
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **API**: RESTful with JSON responses
- **Authentication**: JWT tokens (existing system)

## Data Models

### 1. Test Runs Table

```sql
CREATE TABLE test_runs (
    id VARCHAR(20) PRIMARY KEY,
    
    -- Hierarchy associations (nullable, only one should be set)
    project_id VARCHAR(20) REFERENCES projects(id),
    usecase_id VARCHAR(20) REFERENCES usecases(id),
    user_story_id VARCHAR(20) REFERENCES user_stories(id),
    task_id VARCHAR(20) REFERENCES tasks(id),
    subtask_id VARCHAR(20) REFERENCES subtasks(id),
    
    -- Test run details
    name VARCHAR(255) NOT NULL,
    purpose TEXT,
    short_description VARCHAR(500),
    long_description TEXT,
    component_attached_to VARCHAR(255),  -- e.g., "Login Module", "Payment Screen"
    
    -- Classification
    run_type VARCHAR(50) DEFAULT 'Misc',  -- Misc, One-Timer
    status VARCHAR(50) DEFAULT 'In Progress',  -- In Progress, Completed, Aborted
    
    -- Dates
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    
    -- Metrics (calculated)
    total_test_cases INTEGER DEFAULT 0,
    passed_test_cases INTEGER DEFAULT 0,
    failed_test_cases INTEGER DEFAULT 0,
    blocked_test_cases INTEGER DEFAULT 0,
    
    -- Audit fields
    created_by VARCHAR(20) NOT NULL,
    updated_by VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CONSTRAINT test_run_hierarchy_check CHECK (
        (project_id IS NOT NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
        (project_id IS NULL AND usecase_id IS NOT NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
        (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NOT NULL AND task_id IS NULL AND subtask_id IS NULL) OR
        (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NOT NULL AND subtask_id IS NULL) OR
        (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NOT NULL)
    )
);

CREATE INDEX idx_test_runs_project ON test_runs(project_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_usecase ON test_runs(usecase_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_user_story ON test_runs(user_story_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_task ON test_runs(task_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_subtask ON test_runs(subtask_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_status ON test_runs(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_runs_type ON test_runs(run_type) WHERE is_deleted = FALSE;
```

### 2. Test Cases Table

```sql
CREATE TABLE test_cases (
    id VARCHAR(20) PRIMARY KEY,
    
    -- Belongs to a Test Run
    test_run_id VARCHAR(20) NOT NULL REFERENCES test_runs(id),
    
    -- Test case details
    test_case_name VARCHAR(255) NOT NULL,
    test_case_description TEXT,
    test_case_steps TEXT NOT NULL,  -- JSON array of numbered steps
    expected_result TEXT NOT NULL,
    actual_result TEXT,  -- Filled during execution
    inference TEXT,  -- Conclusion/analysis after execution
    component_attached_to VARCHAR(255),  -- e.g., "Login Screen", "API Gateway"
    remarks TEXT,
    
    -- Classification
    priority VARCHAR(20),  -- P0, P1, P2, P3
    status VARCHAR(50) DEFAULT 'Not Executed',  -- Not Executed, Passed, Failed, Blocked, Skipped
    
    -- Audit fields
    created_by VARCHAR(20) NOT NULL,
    updated_by VARCHAR(20),
    executed_by VARCHAR(20),
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_test_cases_test_run ON test_cases(test_run_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_cases_status ON test_cases(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_test_cases_component ON test_cases(component_attached_to) WHERE is_deleted = FALSE;
```

### 3. Extended Bugs Table

```sql
-- Extend existing bugs table with new columns
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS test_run_id VARCHAR(20) REFERENCES test_runs(id);  -- Link to test run if bug from test case
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS test_case_id VARCHAR(20) REFERENCES test_cases(id);  -- Direct link to failed test case

-- Hierarchy associations (for bugs created directly, not from test cases)
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS project_id VARCHAR(20) REFERENCES projects(id);
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS usecase_id VARCHAR(20) REFERENCES usecases(id);
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS user_story_id VARCHAR(20) REFERENCES user_stories(id);
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS task_id VARCHAR(20) REFERENCES tasks(id);
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS subtask_id VARCHAR(20) REFERENCES subtasks(id);

-- Bug categorization (following industry standards)
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS category VARCHAR(50);  -- UI, Backend, Database, Integration, Performance, Security, Environment
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS severity VARCHAR(50);  -- Critical, High, Medium, Low (Impact on system)
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS priority VARCHAR(50);  -- P1, P2, P3, P4 (How soon it must be fixed)

-- Bug status workflow
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'New';  -- New, Open, In Progress, Fixed, In Review, Ready for QA, Verified, Closed, Reopened

-- Assignments
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reporter_id VARCHAR(20) REFERENCES users(id);  -- Who reported the bug
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS assignee_id VARCHAR(20) REFERENCES users(id);  -- Developer assigned
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS qa_owner_id VARCHAR(20) REFERENCES users(id);  -- QA owner

-- Reproduction path
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reproduction_steps TEXT;  -- Steps to reproduce
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS expected_result TEXT;  -- What should happen
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS actual_result TEXT;  -- What actually happens

-- Linked items
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_task_id VARCHAR(20);  -- Link to task/user story
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_commit VARCHAR(255);  -- Git commit hash
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_pr VARCHAR(255);  -- Pull request URL

-- Additional fields
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS component_attached_to VARCHAR(255);  -- Component/module affected
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS environment VARCHAR(255);  -- Environment where bug found
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reopen_count INTEGER DEFAULT 0;
ALTER TABLE bugs ADD COLUMN IF NOT EXISTS resolution_notes TEXT;

-- Indexes for hierarchy relationships
CREATE INDEX IF NOT EXISTS idx_bugs_test_run ON bugs(test_run_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_test_case ON bugs(test_case_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_project ON bugs(project_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_usecase ON bugs(usecase_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_user_story ON bugs(user_story_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_task ON bugs(task_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_subtask ON bugs(subtask_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_category ON bugs(category) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_severity ON bugs(severity) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_priority ON bugs(priority) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_reporter ON bugs(reporter_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_assignee ON bugs(assignee_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bugs_qa_owner ON bugs(qa_owner_id) WHERE is_deleted = FALSE;
```

### 4. Bug Comments Table

```sql
CREATE TABLE bug_comments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id),
    
    -- Comment details
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL REFERENCES users(id),
    
    -- Mentions
    mentioned_users TEXT,  -- JSON array of user IDs
    
    -- Edit tracking
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    
    -- Attachments
    attachments TEXT,  -- JSON array of file paths
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_bug_comments_bug ON bug_comments(bug_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_bug_comments_author ON bug_comments(author_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_bug_comments_created ON bug_comments(created_at);
```

### 5. Bug Attachments Table

```sql
CREATE TABLE bug_attachments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id),
    
    -- File details
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),  -- image/png, application/pdf, etc.
    file_size INTEGER,  -- in bytes
    
    -- Audit fields
    uploaded_by VARCHAR(20) NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_bug_attachments_bug ON bug_attachments(bug_id) WHERE is_deleted = FALSE;
```

### 6. Bug Status History Table

```sql
CREATE TABLE bug_status_history (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL REFERENCES bugs(id),
    
    -- Status change
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    resolution_type VARCHAR(50),
    notes TEXT,
    
    -- Audit fields
    changed_by VARCHAR(20) NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bug_status_history_bug ON bug_status_history(bug_id);
CREATE INDEX idx_bug_status_history_date ON bug_status_history(changed_at);
```

## Components and Interfaces

### Frontend Components

#### 1. QA Menu Group (Sidebar Update)

**Location**: `ui/src/components/layout/Sidebar.tsx`

**Changes**:
```typescript
const navGroups: Record<string, NavGroup> = {
  // ... existing groups ...
  qa: {
    label: 'QA',
    icon: '🧪',
    defaultOpen: true,
    items: [
      { path: '/test-cases', label: 'Test Cases', icon: '📋' },
      { path: '/bug-lifecycle', label: 'Bug Lifecycle', icon: '🐛' }
    ]
  },
  // ... rest of groups ...
}
```

#### 2. Test Cases Page

**Location**: `ui/src/pages/TestCasesPage.tsx`

**Features**:
- Hierarchical selector (Client → Task)
- Test case list with filters
- Create/Edit test case modal
- Execute test button
- Link to related bugs

**Key State**:
```typescript
interface TestCasesPageState {
  selectedHierarchy: {
    clientId?: string;
    programId?: string;
    projectId?: string;
    usecaseId?: string;
    userStoryId?: string;
    taskId?: string;
  };
  testCases: TestCase[];
  filters: {
    status?: string;
    type?: string;
    priority?: string;
  };
  selectedTestCase?: TestCase;
}
```

#### 3. Bug Lifecycle Page

**Location**: `ui/src/pages/BugLifecyclePage.tsx`

**Features**:
- Hierarchical selector (Client → Subtask)
- "View Bugs" button at each level
- Bug list with advanced filters
- Create/Edit bug modal
- Bug details panel with comments
- Metrics dashboard

**Key State**:
```typescript
interface BugLifecyclePageState {
  selectedHierarchy: {
    clientId?: string;
    programId?: string;
    projectId?: string;
    usecaseId?: string;
    userStoryId?: string;
    taskId?: string;
    subtaskId?: string;
  };
  bugs: Bug[];
  filters: {
    status?: string[];
    severity?: string[];
    priority?: string[];
    assignee?: string;
    reporter?: string;
    bugType?: string;
    dateRange?: { start: Date; end: Date };
  };
  selectedBug?: Bug;
  showMetrics: boolean;
}
```

#### 4. Test Case Form Component

**Location**: `ui/src/components/forms/TestCaseForm.tsx`

**Props**:
```typescript
interface TestCaseFormProps {
  testCase?: TestCase;  // For editing
  hierarchyLevel: {
    type: 'project' | 'usecase' | 'user_story' | 'task';
    id: string;
  };
  onSave: (testCase: TestCaseCreate) => Promise<void>;
  onCancel: () => void;
}
```

**Fields**:
- Title (required)
- Description
- Preconditions
- Test Steps (dynamic list)
- Expected Result (required)
- Test Data
- Test Type (dropdown)
- Priority (dropdown)
- Tags (multi-select)

#### 5. Bug Form Component

**Location**: `ui/src/components/forms/BugForm.tsx` (enhance existing)

**Additional Fields**:
- Hierarchy selector (Client → Subtask)
- Bug Type dropdown
- Environment details (browser, OS, device)
- Found in Version
- Assign to User dropdown
- Link to Test Case (optional)

#### 6. Test Execution Modal

**Location**: `ui/src/components/qa/TestExecutionModal.tsx`

**Features**:
- Display test case details
- Record actual results
- Select execution status
- Add execution notes
- Capture environment
- Upload screenshots/logs
- Create bug on failure

#### 7. Comments Component

**Location**: `ui/src/components/qa/CommentsSection.tsx`

**Features**:
- Display threaded comments
- Add new comment with rich text
- Edit own comments (within 15 min)
- Delete own comments
- @mention autocomplete
- File attachments
- System-generated notes

**Props**:
```typescript
interface CommentsSectionProps {
  entityType: 'bug' | 'test_case';
  entityId: string;
  currentUser: User;
}
```

#### 8. Bug Metrics Dashboard

**Location**: `ui/src/components/qa/BugMetricsDashboard.tsx`

**Metrics Displayed**:
- Total bugs, open bugs, closed bugs
- Bug resolution rate
- Average resolution time (MTTR)
- Bug distribution by severity/priority (pie charts)
- Bug trend analysis (line chart)
- Bug aging report (bar chart)
- Reopen rate
- Test execution coverage

### Backend API Endpoints

#### Test Cases Endpoints

```python
# api/app/api/v1/endpoints/test_cases.py

@router.get("/test-cases/")
async def list_test_cases(
    project_id: Optional[str] = None,
    usecase_id: Optional[str] = None,
    user_story_id: Optional[str] = None,
    task_id: Optional[str] = None,
    status: Optional[str] = None,
    test_type: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> TestCaseList

@router.get("/test-cases/{test_case_id}")
async def get_test_case(test_case_id: str) -> TestCaseResponse

@router.post("/test-cases/")
async def create_test_case(test_case: TestCaseCreate) -> TestCaseResponse

@router.put("/test-cases/{test_case_id}")
async def update_test_case(
    test_case_id: str,
    test_case: TestCaseUpdate
) -> TestCaseResponse

@router.delete("/test-cases/{test_case_id}")
async def delete_test_case(test_case_id: str) -> None

@router.get("/test-cases/{test_case_id}/executions")
async def get_test_case_executions(
    test_case_id: str
) -> List[TestExecutionResponse]
```

#### Test Executions Endpoints

```python
# api/app/api/v1/endpoints/test_executions.py

@router.post("/test-executions/")
async def create_test_execution(
    execution: TestExecutionCreate
) -> TestExecutionResponse

@router.get("/test-executions/{execution_id}")
async def get_test_execution(execution_id: str) -> TestExecutionResponse

@router.post("/test-executions/{execution_id}/create-bug")
async def create_bug_from_execution(
    execution_id: str,
    bug_data: BugCreateFromExecution
) -> BugResponse
```

#### Enhanced Bug Endpoints

```python
# api/app/api/v1/endpoints/bugs.py (enhance existing)

@router.get("/bugs/hierarchy")
async def get_bugs_by_hierarchy(
    client_id: Optional[str] = None,
    program_id: Optional[str] = None,
    project_id: Optional[str] = None,
    usecase_id: Optional[str] = None,
    user_story_id: Optional[str] = None,
    task_id: Optional[str] = None,
    subtask_id: Optional[str] = None,
    include_descendants: bool = True,
    status: Optional[List[str]] = None,
    severity: Optional[List[str]] = None,
    priority: Optional[List[str]] = None,
    skip: int = 0,
    limit: int = 50
) -> BugList

@router.post("/bugs/{bug_id}/assign")
async def assign_bug(
    bug_id: str,
    assignee_id: str,
    notify: bool = True
) -> BugResponse

@router.post("/bugs/{bug_id}/status")
async def update_bug_status(
    bug_id: str,
    status_update: BugStatusUpdate
) -> BugResponse

@router.get("/bugs/{bug_id}/history")
async def get_bug_history(bug_id: str) -> List[BugStatusHistoryResponse]
```

#### Comments Endpoints

```python
# api/app/api/v1/endpoints/comments.py

@router.get("/bugs/{bug_id}/comments")
async def get_bug_comments(bug_id: str) -> List[CommentResponse]

@router.post("/bugs/{bug_id}/comments")
async def create_bug_comment(
    bug_id: str,
    comment: CommentCreate
) -> CommentResponse

@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: str,
    comment: CommentUpdate
) -> CommentResponse

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str) -> None

@router.get("/test-cases/{test_case_id}/comments")
async def get_test_case_comments(test_case_id: str) -> List[CommentResponse]

@router.post("/test-cases/{test_case_id}/comments")
async def create_test_case_comment(
    test_case_id: str,
    comment: CommentCreate
) -> CommentResponse
```

#### Metrics Endpoints

```python
# api/app/api/v1/endpoints/qa_metrics.py

@router.get("/qa-metrics/bugs/summary")
async def get_bug_summary(
    hierarchy_filter: HierarchyFilter
) -> BugSummaryMetrics

@router.get("/qa-metrics/bugs/trends")
async def get_bug_trends(
    start_date: date,
    end_date: date,
    hierarchy_filter: HierarchyFilter
) -> BugTrendData

@router.get("/qa-metrics/bugs/aging")
async def get_bug_aging_report(
    hierarchy_filter: HierarchyFilter
) -> BugAgingReport

@router.get("/qa-metrics/test-execution/summary")
async def get_test_execution_summary(
    test_run_id: Optional[str] = None,
    hierarchy_filter: Optional[HierarchyFilter] = None
) -> TestExecutionMetrics
```

## Error Handling

### Validation Errors

- Invalid hierarchy associations
- Invalid status transitions
- Missing required fields
- Invalid enum values (severity, priority, status)

### Business Logic Errors

- Cannot assign bug to inactive user
- Cannot execute deprecated test case
- Cannot reopen bug without reason
- Cannot delete test case with active executions

### HTTP Status Codes

- `200 OK`: Successful GET/PUT requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Business logic violation
- `500 Internal Server Error`: Unexpected errors

## Testing Strategy

### Unit Tests

- Model validation tests
- CRUD operation tests
- Business logic tests (status transitions, hierarchy validation)
- Comment and attachment handling

### Integration Tests

- API endpoint tests
- Database transaction tests
- Hierarchy query tests (descendant aggregation)
- Metrics calculation tests

### End-to-End Tests

- Test case creation and execution workflow
- Bug creation from failed test
- Bug lifecycle (New → Closed)
- Comment and @mention functionality
- Hierarchical bug viewing

### Performance Tests

- Large dataset queries (1000+ bugs)
- Hierarchical aggregation performance
- Metrics calculation performance
- Comment pagination

## Security Considerations

### Authentication & Authorization

- All endpoints require authentication
- Role-based access control:
  - **Admin**: Full access to all QA features
  - **Tester/QA**: Create/edit test cases and bugs, execute tests
  - **Developer**: View bugs assigned to them, add comments
  - **Project Manager**: View all bugs and metrics
  - **Viewer**: Read-only access

### Data Validation

- Input sanitization for all text fields
- File upload validation (type, size limits)
- SQL injection prevention (parameterized queries)
- XSS prevention in comments (sanitize HTML)

### Audit Trail

- Track all bug status changes
- Track all test executions
- Track comment edits and deletions
- Track bug assignments

## Migration Strategy

### Database Migrations

1. **Migration 012**: Create test_cases table
2. **Migration 013**: Create test_executions and test_runs tables
3. **Migration 014**: Extend bugs table with new columns
4. **Migration 015**: Create test_case_bugs junction table
5. **Migration 016**: Create bug_comments and test_case_comments tables
6. **Migration 017**: Create bug_attachments and bug_status_history tables

### Data Migration

- Existing bugs: Add default hierarchy associations based on existing relationships
- Preserve all existing bug data
- Set default values for new fields

### Backward Compatibility

- Maintain existing bug API endpoints
- Add new endpoints with `/v1/` prefix
- Support both old and new bug schemas during transition period

## Deployment Plan

### Phase 1: Backend Infrastructure
- Database migrations
- API models and schemas
- CRUD endpoints for test cases
- Enhanced bug endpoints

### Phase 2: Core Features
- Test case management UI
- Bug lifecycle UI with hierarchy selector
- Comments functionality
- Test execution workflow

### Phase 3: Advanced Features
- Metrics dashboard
- Bug reports and exports
- Test runs
- Notifications

### Phase 4: Polish & Optimization
- Performance optimization
- UI/UX improvements
- Comprehensive testing
- Documentation

## Dummy Data Generation

### Script Location
`dummy_data_setup/create_qa_data.py`

### Excel Templates
- `excel_templates/test_cases.xlsx`
- `excel_templates/test_executions.xlsx`
- `excel_templates/bugs_extended.xlsx`

### Data Generation Strategy

1. **Test Cases**: 30 test cases distributed across:
   - 10 at Project level
   - 8 at Use Case level
   - 8 at User Story level
   - 4 at Task level

2. **Test Executions**: 100 executions with:
   - 60% Passed
   - 25% Failed
   - 10% Blocked
   - 5% Skipped

3. **Bugs**: 50 bugs with:
   - Various statuses (realistic distribution)
   - Different severity levels
   - Assigned to different users
   - 20% linked to test cases
   - Comments and status history

4. **Comments**: 100+ comments across bugs and test cases

### API Integration
- Use real API endpoints for data creation
- Validate all data before insertion
- Handle errors gracefully
- Log creation progress

## Next Steps

After design approval, the implementation will proceed with:
1. Database migration scripts
2. Backend API models and endpoints
3. Frontend components and pages
4. Dummy data generation scripts
5. Testing and validation
6. Documentation updates


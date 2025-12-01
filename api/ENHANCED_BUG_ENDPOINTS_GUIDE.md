# Enhanced Bug Endpoints - Quick Reference Guide

## New Endpoints Overview

This guide provides quick reference for the newly implemented enhanced bug management endpoints.

---

## 1. Hierarchical Bug List

**Endpoint**: `GET /api/v1/bugs/hierarchy`

**Purpose**: Retrieve bugs filtered by hierarchy level with optional descendant inclusion.

**Example Requests**:

```bash
# Get all bugs for a specific project (including descendants)
curl -X GET "http://localhost:8000/api/v1/bugs/hierarchy?project_id=PROJ-123&include_descendants=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get bugs for a use case (direct only, no descendants)
curl -X GET "http://localhost:8000/api/v1/bugs/hierarchy?usecase_id=UC-456&include_descendants=false" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get open critical bugs for a task
curl -X GET "http://localhost:8000/api/v1/bugs/hierarchy?task_id=TASK-789&status=Open&severity=Critical" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search bugs by text
curl -X GET "http://localhost:8000/api/v1/bugs/hierarchy?project_id=PROJ-123&search=login%20error" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get bugs assigned to a specific user
curl -X GET "http://localhost:8000/api/v1/bugs/hierarchy?project_id=PROJ-123&assignee_id=USER-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Query Parameters**:
- `client_id`, `program_id`, `project_id`, `usecase_id`, `user_story_id`, `task_id`, `subtask_id` - Hierarchy filters
- `include_descendants` (boolean, default: true) - Include bugs from child levels
- `status` (list) - Filter by status (can specify multiple)
- `severity` (list) - Filter by severity (can specify multiple)
- `priority` (list) - Filter by priority (can specify multiple)
- `bug_type` (string) - Filter by bug type
- `assignee_id` (string) - Filter by assignee
- `reporter_id` (string) - Filter by reporter
- `search` (string) - Search in title and description
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 50, max: 100) - Page size

**Response**:
```json
{
  "bugs": [
    {
      "id": "BUG-123",
      "title": "Login button not working",
      "description": "...",
      "severity": "Critical",
      "priority": "P0 (Critical)",
      "status": "Open",
      "bug_type": "Functional",
      "hierarchy_path": "Acme Corp > ERP System > User Management > Login",
      "age_days": 5,
      "assigned_to": "USER-001",
      "reported_by": "USER-002",
      "created_at": "2024-01-10T09:00:00Z",
      ...
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

---

## 2. Enhanced Bug Creation

**Endpoint**: `POST /api/v1/bugs/`

**Purpose**: Create a new bug with hierarchy selection and optional assignment.

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/v1/bugs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Payment gateway timeout",
    "description": "Payment processing times out after 30 seconds",
    "severity": "Critical",
    "priority": "P0 (Critical)",
    "project_id": "PROJ-123",
    "bug_type": "Performance",
    "browser": "Chrome 120",
    "os": "Windows 11",
    "device_type": "Desktop",
    "found_in_version": "v2.1.0",
    "assigned_to": "USER-001",
    "steps_to_reproduce": "1. Go to checkout\n2. Enter payment details\n3. Click Pay",
    "expected_behavior": "Payment should process within 5 seconds",
    "actual_behavior": "Payment times out after 30 seconds"
  }'
```

**Required Fields**:
- `title` (string, 1-255 chars)
- `description` (string)
- `severity` (enum: Blocker, Critical, Major, Minor, Trivial)
- `priority` (enum: P0 (Critical), P1 (High), P2 (Medium), P3 (Low), P4 (Trivial))
- At least one hierarchy field (client_id, program_id, project_id, etc.)

**Optional Fields**:
- `assigned_to` (string) - User ID
- `bug_type` (enum: Functional, Performance, Security, UI/UX, Data, Integration, Configuration)
- `browser`, `os`, `device_type` (strings)
- `found_in_version` (string)
- `steps_to_reproduce`, `expected_behavior`, `actual_behavior` (text)

**Response**: Returns created bug with status "New"

---

## 3. Bug Status Update

**Endpoint**: `POST /api/v1/bugs/{bug_id}/status`

**Purpose**: Update bug status with validation and history tracking.

**Example Requests**:

```bash
# Mark bug as fixed
curl -X POST "http://localhost:8000/api/v1/bugs/BUG-123/status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Fixed",
    "resolution_type": "Fixed",
    "resolution_notes": "Fixed by updating the timeout configuration"
  }'

# Reopen a bug
curl -X POST "http://localhost:8000/api/v1/bugs/BUG-123/status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Reopened",
    "resolution_notes": "Issue still occurs in production"
  }'

# Close a verified bug
curl -X POST "http://localhost:8000/api/v1/bugs/BUG-123/status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Closed"
  }'
```

**Request Body**:
- `status` (required, enum) - New status
- `resolution_type` (required when status is "Fixed", enum) - Resolution type
- `resolution_notes` (optional, string) - Notes about the change

**Valid Statuses**:
- New, Open, In Progress, Fixed, Ready for Testing, Retest, Verified, Closed, Reopened, Deferred, Rejected

**Resolution Types** (required for "Fixed" status):
- Fixed, Duplicate, Cannot Reproduce, Won't Fix, By Design, Deferred

**Status Transition Rules**:
- The endpoint validates transitions according to the bug lifecycle workflow
- Invalid transitions return a 400 error with allowed transitions

**Response**: Returns updated bug

---

## 4. Bug Assignment

**Endpoint**: `POST /api/v1/bugs/{bug_id}/assign`

**Purpose**: Assign a bug to a user with validation.

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/v1/bugs/BUG-123/assign?assignee_id=USER-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Query Parameters**:
- `assignee_id` (required) - User ID to assign the bug to

**Authorization**: Requires Admin, Tester, or Project Manager role

**Validation**:
- Verifies bug exists and is not deleted
- Verifies assignee exists and is active
- Sends notification to assignee (logged)

**Response**: Returns updated bug

---

## 5. Bug History

**Endpoint**: `GET /api/v1/bugs/{bug_id}/history`

**Purpose**: Retrieve complete history of bug changes.

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/bugs/BUG-123/history" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "bug_id": "BUG-123",
  "history": [
    {
      "id": "HIST-001",
      "type": "status_change",
      "timestamp": "2024-01-15T14:30:00Z",
      "changed_by": "USER-001",
      "changed_by_name": "John Doe",
      "from_status": "In Progress",
      "to_status": "Fixed",
      "resolution_type": "Fixed",
      "notes": "Fixed the timeout issue",
      "description": "Status changed from 'In Progress' to 'Fixed' (Resolution: Fixed)"
    },
    {
      "id": "HIST-002",
      "type": "status_change",
      "timestamp": "2024-01-12T10:00:00Z",
      "changed_by": "USER-001",
      "changed_by_name": "John Doe",
      "from_status": "Open",
      "to_status": "In Progress",
      "description": "Status changed from 'Open' to 'In Progress'"
    },
    {
      "id": "BUG-123_created",
      "type": "created",
      "timestamp": "2024-01-10T09:00:00Z",
      "changed_by": "USER-002",
      "changed_by_name": "Jane Smith",
      "description": "Bug created by Jane Smith",
      "severity": "Critical",
      "priority": "P0 (Critical)"
    }
  ],
  "total_changes": 3
}
```

**History Item Types**:
- `status_change` - Status transition
- `created` - Bug creation event

**Ordering**: Most recent changes first (descending timestamp)

---

## Common Use Cases

### 1. View All Bugs for a Project and Its Children

```bash
GET /api/v1/bugs/hierarchy?project_id=PROJ-123&include_descendants=true
```

### 2. Find All Open Critical Bugs Assigned to Me

```bash
GET /api/v1/bugs/hierarchy?assignee_id=MY-USER-ID&status=Open&severity=Critical
```

### 3. Create and Assign a Bug in One Step

```bash
POST /api/v1/bugs/
{
  "title": "Bug title",
  "description": "Bug description",
  "severity": "Major",
  "priority": "P1 (High)",
  "project_id": "PROJ-123",
  "assigned_to": "USER-001"
}
```

### 4. Complete Bug Workflow

```bash
# 1. Create bug (status: New)
POST /api/v1/bugs/

# 2. Assign to developer
POST /api/v1/bugs/BUG-123/assign?assignee_id=DEV-001

# 3. Developer starts work
POST /api/v1/bugs/BUG-123/status
{"status": "In Progress"}

# 4. Developer fixes bug
POST /api/v1/bugs/BUG-123/status
{"status": "Fixed", "resolution_type": "Fixed"}

# 5. QA verifies fix
POST /api/v1/bugs/BUG-123/status
{"status": "Verified"}

# 6. Close bug
POST /api/v1/bugs/BUG-123/status
{"status": "Closed"}

# 7. View complete history
GET /api/v1/bugs/BUG-123/history
```

### 5. Search for Bugs by Keyword

```bash
GET /api/v1/bugs/hierarchy?project_id=PROJ-123&search=timeout
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid status transition from 'New' to 'Closed'. Allowed transitions: Open, Deferred, Rejected"
}
```

### 404 Not Found
```json
{
  "detail": "Bug with id BUG-123 not found"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to perform this action"
}
```

---

## Notes

- All endpoints require authentication (Bearer token)
- Timestamps are in UTC ISO 8601 format
- IDs are strings (not UUIDs)
- Pagination defaults: skip=0, limit=50, max=100
- All endpoints log activities for audit purposes
- Notification service is currently a placeholder (logs only)

---

## Testing with Postman

Import the API at `http://localhost:8000/docs` to get the OpenAPI specification, which can be imported into Postman for easy testing.

---

## Related Endpoints

- `GET /api/v1/bugs/` - Legacy bug list endpoint (still supported)
- `GET /api/v1/bugs/{bug_id}` - Get single bug details
- `PUT /api/v1/bugs/{bug_id}` - Update bug fields
- `DELETE /api/v1/bugs/{bug_id}` - Soft delete bug
- `POST /api/v1/bugs/{bug_id}/resolve` - Legacy resolve endpoint (deprecated)

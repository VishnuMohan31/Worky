# Design Document

## Overview

The TODO feature is a personal work organization system that provides users with a time-bound view of their work items. The design emphasizes a modern, vibrant UI with smooth interactions, while maintaining strict read-only access to the main project hierarchy. The system consists of three main components: the UI layer (React/TypeScript), the API layer (FastAPI/Python), and the database layer (PostgreSQL).

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ TODO         │  │ Time Panes   │  │ ADHOC        │      │
│  │ Dashboard    │  │ Component    │  │ Notes        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ TODO         │  │ ADHOC        │  │ Task Link    │      │
│  │ Endpoints    │  │ Endpoints    │  │ Service      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer (PostgreSQL)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ todo_items   │  │ adhoc_notes  │  │ tasks/       │      │
│  │              │  │              │  │ subtasks     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Navigation**: User clicks TODO in left navigation → UI loads TODO Dashboard
2. **Data Fetch**: Dashboard requests TODO items for date range → API queries database → Returns TODO items with linked task info
3. **Drag & Drop**: User drags TODO item to different pane → UI updates optimistically → API updates target_date → Database persists change
4. **Task Linking**: User links TODO to task → API validates task exists → Creates link record → Fetches task high-level info
5. **ADHOC Notes**: User creates sticky note → API creates adhoc_note record → UI displays in ADHOC pane

## Components and Interfaces

### UI Components

#### 1. TODO Dashboard Page (`TodoPage.tsx`)

**Purpose**: Main container for the TODO feature

**Props**: None (uses auth context for user)

**State**:
- `todoItems: TodoItem[]` - All TODO items for the user
- `adhocNotes: AdhocNote[]` - All ADHOC notes for the user
- `selectedDate: Date` - Current date for calculating panes
- `isLoading: boolean` - Loading state
- `error: string | null` - Error state

**Key Methods**:
- `fetchTodoItems()` - Loads TODO items from API
- `fetchAdhocNotes()` - Loads ADHOC notes from API
- `handleDateChange(date: Date)` - Updates selected date and recalculates panes

#### 2. Time Panes Component (`TimePanes.tsx`)

**Purpose**: Displays four date-based columns for TODO items

**Props**:
- `todoItems: TodoItem[]` - TODO items to display
- `onItemMove: (itemId: string, newDate: Date) => void` - Callback for drag & drop
- `onItemUpdate: (item: TodoItem) => void` - Callback for item updates
- `onItemDelete: (itemId: string) => void` - Callback for item deletion

**State**:
- `panes: Pane[]` - Array of four panes with dates and items
- `draggedItem: TodoItem | null` - Currently dragged item

**Pane Structure**:
```typescript
interface Pane {
  label: 'Yesterday' | 'Today' | 'Tomorrow' | 'Day After Tomorrow';
  date: Date;
  items: TodoItem[];
}
```

**Key Methods**:
- `calculatePanes()` - Computes dates for each pane
- `handleDragStart(item: TodoItem)` - Initiates drag operation
- `handleDrop(pane: Pane)` - Handles drop and updates item date
- `filterItemsByDate(date: Date)` - Filters items for specific pane

#### 3. TODO Item Card (`TodoItemCard.tsx`)

**Purpose**: Displays individual TODO item with all details

**Props**:
- `item: TodoItem` - The TODO item to display
- `onUpdate: (item: TodoItem) => void` - Update callback
- `onDelete: (itemId: string) => void` - Delete callback
- `draggable: boolean` - Whether item can be dragged

**Visual Elements**:
- Title and description
- Visibility badge (Public/Private)
- Link indicator (if linked to task/subtask)
- Linked task info panel (expandable)
- Action buttons (edit, delete, toggle visibility)

**Styling**:
- Card with subtle shadow and border
- Hover state with elevated shadow
- Drag cursor when draggable
- Color-coded border for visibility (green=public, blue=private)

#### 4. ADHOC Notes Pane (`AdhocNotesPane.tsx`)

**Purpose**: Displays sticky notes for quick capture

**Props**:
- `notes: AdhocNote[]` - ADHOC notes to display
- `onNoteCreate: (note: Partial<AdhocNote>) => void` - Create callback
- `onNoteUpdate: (note: AdhocNote) => void` - Update callback
- `onNoteDelete: (noteId: string) => void` - Delete callback
- `onNoteReorder: (noteId: string, newPosition: number) => void` - Reorder callback

**Visual Style**:
- Sticky note appearance (yellow background, slight rotation)
- Masonry layout for notes
- Add button at top
- Drag handles for reordering

#### 5. TODO Item Form Modal (`TodoItemFormModal.tsx`)

**Purpose**: Create/edit TODO items

**Props**:
- `item?: TodoItem` - Existing item for edit mode
- `isOpen: boolean` - Modal visibility
- `onClose: () => void` - Close callback
- `onSave: (item: Partial<TodoItem>) => void` - Save callback

**Form Fields**:
- Title (required, max 255 chars)
- Description (optional, textarea)
- Target Date (date picker, defaults to today)
- Visibility (radio: Public/Private)
- Link to Task/Subtask (optional, searchable dropdown)

#### 6. Task Link Info Panel (`TaskLinkInfoPanel.tsx`)

**Purpose**: Displays read-only task/subtask information

**Props**:
- `linkedEntity: LinkedTaskInfo` - Task or subtask info
- `entityType: 'task' | 'subtask'` - Type of linked entity

**Displayed Information**:
- Entity ID and title
- Status badge
- Due date (if available)
- Assigned user (if available)
- Link to view full task in hierarchy

**Styling**:
- Compact panel with light background
- Read-only indicator (lock icon)
- Status color-coding

### API Endpoints

#### TODO Items Endpoints

**1. GET /api/v1/todos**

Fetch TODO items for the authenticated user

Query Parameters:
- `start_date` (optional): ISO date string for range start
- `end_date` (optional): ISO date string for range end
- `include_public` (optional): boolean, include public items from other users

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "USR-001",
      "title": "Review PR #123",
      "description": "Check code quality and tests",
      "target_date": "2025-11-28",
      "visibility": "private",
      "linked_entity_type": "task",
      "linked_entity_id": "TSK-001",
      "linked_entity_info": {
        "title": "Implement authentication",
        "status": "In Progress",
        "due_date": "2025-11-30",
        "assigned_to": "John Doe"
      },
      "is_deleted": false,
      "created_at": "2025-11-27T10:00:00Z",
      "updated_at": "2025-11-27T10:00:00Z"
    }
  ],
  "total": 15
}
```

**2. POST /api/v1/todos**

Create a new TODO item

Request Body:
```json
{
  "title": "Review PR #123",
  "description": "Check code quality and tests",
  "target_date": "2025-11-28",
  "visibility": "private",
  "linked_entity_type": "task",
  "linked_entity_id": "TSK-001"
}
```

Response: Created TODO item (201)

**3. PUT /api/v1/todos/{todo_id}**

Update an existing TODO item

Request Body: Same as POST (all fields optional)

Response: Updated TODO item (200)

**4. DELETE /api/v1/todos/{todo_id}**

Soft delete a TODO item

Response: 204 No Content

**5. PATCH /api/v1/todos/{todo_id}/move**

Move TODO item to different date

Request Body:
```json
{
  "target_date": "2025-11-29"
}
```

Response: Updated TODO item (200)

**6. POST /api/v1/todos/{todo_id}/link**

Link TODO item to task or subtask

Request Body:
```json
{
  "entity_type": "task",
  "entity_id": "TSK-001"
}
```

Response: Updated TODO item with linked info (200)

**7. DELETE /api/v1/todos/{todo_id}/link**

Unlink TODO item from task/subtask

Response: Updated TODO item (200)

#### ADHOC Notes Endpoints

**1. GET /api/v1/adhoc-notes**

Fetch ADHOC notes for the authenticated user

Response:
```json
{
  "notes": [
    {
      "id": "uuid",
      "user_id": "USR-001",
      "title": "Remember to...",
      "content": "Call client about requirements",
      "position": 1,
      "color": "#FFEB3B",
      "is_deleted": false,
      "created_at": "2025-11-27T10:00:00Z",
      "updated_at": "2025-11-27T10:00:00Z"
    }
  ],
  "total": 5
}
```

**2. POST /api/v1/adhoc-notes**

Create a new ADHOC note

Request Body:
```json
{
  "title": "Remember to...",
  "content": "Call client about requirements",
  "color": "#FFEB3B"
}
```

Response: Created note (201)

**3. PUT /api/v1/adhoc-notes/{note_id}**

Update an ADHOC note

Request Body: Same as POST (all fields optional)

Response: Updated note (200)

**4. DELETE /api/v1/adhoc-notes/{note_id}**

Soft delete an ADHOC note

Response: 204 No Content

**5. PATCH /api/v1/adhoc-notes/{note_id}/reorder**

Update note position

Request Body:
```json
{
  "position": 3
}
```

Response: Updated note (200)

#### Task Link Service Endpoints

**1. GET /api/v1/tasks/{task_id}/summary**

Get high-level task information (read-only)

Response:
```json
{
  "id": "TSK-001",
  "title": "Implement authentication",
  "status": "In Progress",
  "due_date": "2025-11-30",
  "assigned_to": "John Doe",
  "user_story_id": "UST-001"
}
```

**2. GET /api/v1/subtasks/{subtask_id}/summary**

Get high-level subtask information (read-only)

Response:
```json
{
  "id": "SUB-001",
  "title": "Write unit tests",
  "status": "To Do",
  "assigned_to": "Jane Smith",
  "task_id": "TSK-001"
}
```

### API Business Rules

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own TODO items and ADHOC notes (except public TODO items)
3. **Validation**:
   - Title: required, 1-255 characters
   - Description: optional, max 2000 characters
   - Target date: must be valid date
   - Visibility: must be 'public' or 'private'
   - Linked entity: must exist in database if provided
4. **Rate Limiting**: 100 requests per minute per user
5. **Soft Delete**: Deleted items are marked is_deleted=true, not physically removed
6. **Read-Only Task Access**: Task/subtask endpoints only allow GET operations from TODO context

## Data Models

### Database Schema

#### Table: `todo_items`

Stores user TODO items with optional links to tasks/subtasks

```sql
CREATE TABLE todo_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    visibility VARCHAR(10) NOT NULL CHECK (visibility IN ('public', 'private')),
    linked_entity_type VARCHAR(20) CHECK (linked_entity_type IN ('task', 'subtask')),
    linked_entity_id VARCHAR(20),
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_todo_items_user_id ON todo_items(user_id);
CREATE INDEX idx_todo_items_target_date ON todo_items(target_date);
CREATE INDEX idx_todo_items_visibility ON todo_items(visibility);
CREATE INDEX idx_todo_items_user_date ON todo_items(user_id, target_date) WHERE is_deleted = false;
CREATE INDEX idx_todo_items_linked_entity ON todo_items(linked_entity_type, linked_entity_id) WHERE linked_entity_id IS NOT NULL;

-- Trigger for updated_at
CREATE TRIGGER update_todo_items_updated_at BEFORE UPDATE ON todo_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Field Descriptions**:
- `id`: Unique identifier for the TODO item
- `user_id`: Owner of the TODO item (foreign key to users table)
- `title`: Short title of the TODO item (required)
- `description`: Detailed description (optional)
- `target_date`: The date this TODO item is planned for
- `visibility`: Controls who can see this item ('public' or 'private')
- `linked_entity_type`: Type of linked entity ('task' or 'subtask'), null if standalone
- `linked_entity_id`: ID of the linked task or subtask, null if standalone
- `is_deleted`: Soft delete flag
- `created_at`: Timestamp when item was created
- `updated_at`: Timestamp when item was last modified

**Constraints**:
- If `linked_entity_type` is set, `linked_entity_id` must also be set
- `target_date` cannot be null
- `visibility` must be either 'public' or 'private'

#### Table: `adhoc_notes`

Stores standalone sticky notes for users

```sql
CREATE TABLE adhoc_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    color VARCHAR(7) DEFAULT '#FFEB3B',
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_adhoc_notes_user_id ON adhoc_notes(user_id);
CREATE INDEX idx_adhoc_notes_position ON adhoc_notes(user_id, position) WHERE is_deleted = false;

-- Trigger for updated_at
CREATE TRIGGER update_adhoc_notes_updated_at BEFORE UPDATE ON adhoc_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Field Descriptions**:
- `id`: Unique identifier for the ADHOC note
- `user_id`: Owner of the note (foreign key to users table)
- `title`: Short title of the note (required)
- `content`: Full content of the note (optional)
- `position`: Display order within user's ADHOC pane (for reordering)
- `color`: Hex color code for sticky note appearance
- `is_deleted`: Soft delete flag
- `created_at`: Timestamp when note was created
- `updated_at`: Timestamp when note was last modified

**Constraints**:
- `position` must be >= 0
- `color` must be valid hex color format (#RRGGBB)

### TypeScript Interfaces

```typescript
// TODO Item
interface TodoItem {
  id: string;
  userId: string;
  title: string;
  description?: string;
  targetDate: string; // ISO date string
  visibility: 'public' | 'private';
  linkedEntityType?: 'task' | 'subtask';
  linkedEntityId?: string;
  linkedEntityInfo?: LinkedTaskInfo;
  isDeleted: boolean;
  createdAt: string;
  updatedAt: string;
}

// Linked Task/Subtask Info
interface LinkedTaskInfo {
  id: string;
  title: string;
  status: string;
  dueDate?: string;
  assignedTo?: string;
  parentId?: string; // user_story_id for tasks, task_id for subtasks
}

// ADHOC Note
interface AdhocNote {
  id: string;
  userId: string;
  title: string;
  content?: string;
  position: number;
  color: string;
  isDeleted: boolean;
  createdAt: string;
  updatedAt: string;
}

// API Request/Response Types
interface CreateTodoItemRequest {
  title: string;
  description?: string;
  targetDate: string;
  visibility: 'public' | 'private';
  linkedEntityType?: 'task' | 'subtask';
  linkedEntityId?: string;
}

interface UpdateTodoItemRequest {
  title?: string;
  description?: string;
  targetDate?: string;
  visibility?: 'public' | 'private';
}

interface MoveTodoItemRequest {
  targetDate: string;
}

interface LinkTodoItemRequest {
  entityType: 'task' | 'subtask';
  entityId: string;
}

interface CreateAdhocNoteRequest {
  title: string;
  content?: string;
  color?: string;
}

interface ReorderAdhocNoteRequest {
  position: number;
}
```

### Python Models (SQLAlchemy)

```python
# api/app/models/todo.py

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Date, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_date = Column(Date, nullable=False)
    visibility = Column(String(10), nullable=False)
    linked_entity_type = Column(String(20))
    linked_entity_id = Column(String(20))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="todo_items")

    # Constraints
    __table_args__ = (
        CheckConstraint("visibility IN ('public', 'private')", name="check_visibility"),
        CheckConstraint("linked_entity_type IN ('task', 'subtask') OR linked_entity_type IS NULL", name="check_entity_type"),
    )


class AdhocNote(Base):
    __tablename__ = "adhoc_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    position = Column(Integer, nullable=False, default=0)
    color = Column(String(7), default="#FFEB3B")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="adhoc_notes")

    # Constraints
    __table_args__ = (
        CheckConstraint("position >= 0", name="check_position_positive"),
    )
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "field_errors": {
    "field_name": ["Error message 1", "Error message 2"]
  }
}
```

### Error Codes

- `TODO_NOT_FOUND`: TODO item not found
- `TODO_UNAUTHORIZED`: User not authorized to access TODO item
- `TODO_INVALID_DATE`: Invalid target date provided
- `TODO_INVALID_VISIBILITY`: Invalid visibility value
- `TODO_LINK_NOT_FOUND`: Linked task/subtask not found
- `TODO_LINK_INVALID`: Invalid entity type or ID
- `ADHOC_NOTE_NOT_FOUND`: ADHOC note not found
- `ADHOC_NOTE_UNAUTHORIZED`: User not authorized to access note
- `VALIDATION_ERROR`: Input validation failed

### Error Handling Strategy

1. **Client-Side Validation**: Validate input before API calls (title length, date format, etc.)
2. **API Validation**: Use Pydantic schemas for request validation
3. **Database Constraints**: Enforce data integrity at database level
4. **User-Friendly Messages**: Display clear, actionable error messages in UI
5. **Logging**: Log all errors with context for debugging
6. **Retry Logic**: Implement retry for transient network errors
7. **Fallback UI**: Show graceful degradation when data fails to load

## Testing Strategy

### Unit Tests

**Backend (Python)**:
- Test CRUD operations for TodoItem model
- Test CRUD operations for AdhocNote model
- Test visibility filtering logic
- Test date range filtering
- Test task/subtask linking validation
- Test soft delete functionality

**Frontend (TypeScript/React)**:
- Test TodoItemCard rendering
- Test drag and drop logic
- Test date calculations for panes
- Test visibility toggle
- Test form validation
- Test ADHOC note reordering

### Integration Tests

- Test complete TODO item lifecycle (create → update → move → delete)
- Test linking TODO to task and fetching task info
- Test public TODO visibility across users
- Test ADHOC note CRUD operations
- Test authentication and authorization
- Test concurrent updates to same TODO item

### E2E Tests

- Test user navigates to TODO section
- Test user creates TODO item and links to task
- Test user drags TODO item between panes
- Test user creates and reorders ADHOC notes
- Test user toggles TODO visibility
- Test public TODO items visible to team members

### Performance Tests

- Test loading 100+ TODO items
- Test drag and drop responsiveness
- Test API response times under load
- Test database query performance with indexes

## UI/UX Design Guidelines

### Color Palette

- **Primary**: #6366F1 (Indigo) - Main actions, links
- **Secondary**: #8B5CF6 (Purple) - Secondary actions
- **Success**: #10B981 (Green) - Public visibility, completed items
- **Info**: #3B82F6 (Blue) - Private visibility, informational
- **Warning**: #F59E0B (Amber) - Warnings, overdue items
- **Danger**: #EF4444 (Red) - Delete actions, errors
- **Background**: #F9FAFB (Light gray) - Page background
- **Card**: #FFFFFF (White) - Card backgrounds
- **Sticky Note**: #FFEB3B (Yellow) - ADHOC notes default

### Typography

- **Headings**: Inter, 600 weight
- **Body**: Inter, 400 weight
- **Monospace**: Fira Code (for IDs, dates)

### Spacing

- **Base unit**: 4px
- **Card padding**: 16px
- **Section gap**: 24px
- **Pane gap**: 16px

### Animations

- **Drag start**: Scale 1.05, shadow elevation
- **Drop**: Smooth transition to new position (300ms ease-out)
- **Card hover**: Shadow elevation (200ms ease)
- **Modal open**: Fade in + scale (250ms ease-out)
- **Delete**: Fade out + slide left (300ms ease-in)

### Accessibility

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Readers**: ARIA labels on all interactive elements
- **Focus Indicators**: Clear focus rings on all focusable elements
- **Color Contrast**: WCAG AA compliance (4.5:1 for text)
- **Alt Text**: Descriptive alt text for icons and images

### Responsive Design

- **Desktop (>1024px)**: Four panes side-by-side + ADHOC pane on right
- **Tablet (768-1024px)**: Two panes per row + ADHOC pane below
- **Mobile (<768px)**: Single pane view with tabs + ADHOC as separate tab

## Security Considerations

1. **Authentication**: JWT tokens required for all API calls
2. **Authorization**: Users can only access their own TODO items (except public ones)
3. **Input Sanitization**: Sanitize all user input to prevent XSS
4. **SQL Injection Prevention**: Use parameterized queries (SQLAlchemy ORM)
5. **Rate Limiting**: Prevent abuse with rate limits
6. **CORS**: Configure appropriate CORS policies
7. **Data Privacy**: Private TODO items never exposed to other users
8. **Audit Trail**: Log all TODO operations for audit purposes

## Performance Optimization

1. **Database Indexing**: Indexes on user_id, target_date, visibility
2. **Query Optimization**: Fetch only required fields, use joins efficiently
3. **Caching**: Cache task/subtask summary info (5-minute TTL)
4. **Pagination**: Paginate TODO items if count exceeds 100
5. **Lazy Loading**: Load ADHOC notes separately from TODO items
6. **Optimistic Updates**: Update UI immediately, sync with server in background
7. **Debouncing**: Debounce search and filter operations
8. **Code Splitting**: Lazy load TODO feature components

## Migration Strategy

Since this is a new feature with new tables, the migration is straightforward:

1. Create database migration file for `todo_items` and `adhoc_notes` tables
2. Run migration on development environment
3. Test all CRUD operations
4. Run migration on staging environment
5. Perform integration testing
6. Run migration on production during maintenance window
7. Monitor for any issues

No data migration required as these are new tables with no existing data.

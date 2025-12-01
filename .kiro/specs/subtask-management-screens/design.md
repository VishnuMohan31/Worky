# Design Document

## Overview

This design document outlines the implementation of subtask management screens for the Worky project management platform. The solution follows the established patterns from the existing task management implementation, ensuring consistency in user experience and code architecture. The subtask management feature will provide a complete CRUD interface for managing the lowest level of work items in the hierarchy.

## Architecture

### Component Structure

The subtask management feature follows a three-tier architecture:

1. **Page Layer** (`SubtasksPage.tsx`): Main container component managing state, data fetching, and orchestration
2. **Modal Layer** (`SubtaskModal.tsx`): Dialog component for create/edit operations
3. **Form Layer** (`SubtaskForm.tsx`): Reusable form component with validation logic

### Data Flow

```
SubtasksPage
  ├─> API Service (fetch hierarchy data)
  ├─> API Service (fetch subtasks)
  ├─> SubtaskModal
  │     └─> SubtaskForm
  │           └─> API Service (create/update subtask)
  └─> HierarchyNavigator (detail view navigation)
```

### State Management

The page will manage the following state:
- Hierarchy selections (client, program, project, usecase, userstory, task)
- Loaded data for each hierarchy level
- Subtasks list
- Loading states for each data fetch operation
- Modal open/close state
- Current editing subtask (for edit mode)
- Search and filter values

## Components and Interfaces

### 1. SubtasksPage Component

**Location:** `ui/src/pages/SubtasksPage.tsx`

**Purpose:** Main page component that displays the subtask list with hierarchy filtering

**Props:** None (uses URL search params)

**State:**
```typescript
interface SubtasksPageState {
  // Hierarchy selections
  selectedClientId: string
  selectedProgramId: string
  selectedProjectId: string
  selectedUseCaseId: string
  selectedUserStoryId: string
  selectedTaskId: string
  
  // Data arrays
  clients: Client[]
  programs: Program[]
  projects: Project[]
  usecases: UseCase[]
  userstories: UserStory[]
  tasks: Task[]
  subtasks: Subtask[]
  users: User[]
  phases: Phase[]
  
  // Loading states
  loadingClients: boolean
  loadingPrograms: boolean
  loadingProjects: boolean
  loadingUseCases: boolean
  loadingUserStories: boolean
  loadingTasks: boolean
  loadingSubtasks: boolean
  
  // UI state
  searchQuery: string
  filterStatus: string
  isModalOpen: boolean
  editingSubtask: Subtask | null
}
```

**Key Features:**
- Cascading hierarchy dropdowns with loading states
- Breadcrumb navigation with clickable links
- Search and status filter
- Subtask table with sortable columns
- "New Subtask" button (admin only, task must be selected)
- Row click navigation to detail view

**API Calls:**
- `api.getClients()` - Load all clients
- `api.getEntityList('program')` - Load programs filtered by client
- `api.getProjects()` - Load projects filtered by program
- `api.getEntityList('usecase')` - Load use cases filtered by project
- `api.getEntityList('userstory')` - Load user stories filtered by use case
- `api.getTasks()` - Load tasks filtered by user story
- `api.getSubtasks()` - Load subtasks filtered by task
- `api.getUsers()` - Load users for assignment
- `api.getPhases()` - Load phases for filtering

### 2. SubtaskModal Component

**Location:** `ui/src/components/subtasks/SubtaskModal.tsx`

**Purpose:** Modal dialog for creating and editing subtasks

**Props:**
```typescript
interface SubtaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  subtask?: Subtask | null
  selectedClientId?: string
  selectedProgramId?: string
  selectedProjectId?: string
  selectedUseCaseId?: string
  selectedUserStoryId?: string
  selectedTaskId?: string
  clients: Client[]
  programs: Program[]
  projects: Project[]
  usecases: UseCase[]
  userstories: UserStory[]
  tasks: Task[]
  users: User[]
  phases: Phase[]
  isAdmin: boolean
}
```

**Features:**
- Display hierarchy context (breadcrumb-style info box)
- Form fields for all subtask properties
- Validation error display
- Loading state during save
- Cancel and Save buttons

**Validation Rules:**
- Title: Required, non-empty string
- Task ID: Required, must be selected
- Estimated Hours: Required, must be positive number
- Duration Days: Required, must be positive integer
- Scrum Points: Optional, must be non-negative integer if provided
- Status: Required, must be one of predefined values
- Phase: Optional
- Assigned To: Optional

### 3. SubtaskForm Component

**Location:** `ui/src/components/forms/SubtaskForm.tsx`

**Purpose:** Reusable form component with validation logic

**Props:**
```typescript
interface SubtaskFormProps {
  initialData?: Partial<SubtaskFormData>
  onSubmit: (data: SubtaskFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  taskId?: string
  tasks?: Task[]
  users?: User[]
  phases?: Phase[]
}
```

**Form Fields:**
1. **Title** (text input, required)
2. **Task** (dropdown, required, pre-selected if taskId provided)
3. **Description** (textarea, optional)
4. **Status** (dropdown, required, default: "To Do")
   - Options: "To Do", "In Progress", "Done", "Blocked"
5. **Phase** (dropdown, optional)
6. **Assigned To** (dropdown, optional, shows "Unassigned" option)
7. **Estimated Hours** (number input, required, min: 0, step: 0.5)
8. **Duration Days** (number input, required, min: 1, step: 1)
9. **Scrum Points** (number input, optional, min: 0, step: 0.5)

**Layout:**
- Two-column grid for Status/Phase
- Two-column grid for Estimated Hours/Duration Days
- Full-width fields for Title, Task, Description, Assigned To, Scrum Points

## Data Models

### Subtask Interface (Frontend)

```typescript
interface Subtask extends BaseEntity {
  task_id: string
  phase_id?: string
  title: string
  short_description?: string
  long_description?: string
  status: string
  assigned_to?: string
  estimated_hours?: number
  actual_hours?: number
  duration_days?: number
  scrum_points?: number
  completed_at?: string
}
```

### SubtaskFormData Interface

```typescript
interface SubtaskFormData {
  title: string
  task_id: string
  short_description?: string
  long_description?: string
  status: string
  phase_id?: string
  assigned_to?: string
  estimated_hours: number
  duration_days: number
  scrum_points?: number
}
```

### API Endpoints

The implementation will use the existing hierarchy API pattern:

**Get Subtasks:**
```
GET /api/v1/hierarchy/subtask
Response: Subtask[]
```

**Get Subtask by ID:**
```
GET /api/v1/hierarchy/subtask/{id}
Response: Subtask
```

**Create Subtask:**
```
POST /api/v1/hierarchy/subtask
Body: SubtaskFormData
Response: Subtask
```

**Update Subtask:**
```
PUT /api/v1/hierarchy/subtask/{id}
Body: Partial<SubtaskFormData>
Response: Subtask
```

**Delete Subtask:**
```
DELETE /api/v1/hierarchy/subtask/{id}
Response: { success: boolean }
```

### Database Schema Updates

The subtasks table needs to be extended with new fields:

```sql
ALTER TABLE subtasks
ADD COLUMN duration_days INTEGER,
ADD COLUMN scrum_points NUMERIC(5, 2),
ADD COLUMN estimated_hours NUMERIC(10, 2);
```

**Note:** The `estimated_hours` field may already exist in the schema. Verify before adding.

## Error Handling

### Client-Side Validation

1. **Required Field Validation:**
   - Display error message below field: "This field is required"
   - Prevent form submission until resolved

2. **Numeric Validation:**
   - Estimated Hours: Must be >= 0, display "Must be a positive number"
   - Duration Days: Must be >= 1, display "Must be at least 1 day"
   - Scrum Points: Must be >= 0 if provided, display "Must be a non-negative number"

3. **Form-Level Validation:**
   - Check all required fields before submission
   - Display summary error at top of form if multiple errors exist

### API Error Handling

1. **Network Errors:**
   - Display toast notification: "Network error. Please check your connection."
   - Keep modal open with form data preserved

2. **Validation Errors (400):**
   - Parse error response and display field-specific errors
   - Example: `{ "detail": { "title": "Title is required" } }`

3. **Authorization Errors (403):**
   - Display toast: "You don't have permission to perform this action"
   - Close modal

4. **Not Found Errors (404):**
   - Display toast: "Subtask not found"
   - Refresh subtask list

5. **Server Errors (500):**
   - Display toast: "Server error. Please try again later."
   - Keep modal open with form data preserved

### Loading States

1. **Initial Page Load:**
   - Show centered spinner while loading clients
   - Disable all controls

2. **Hierarchy Dropdown Loading:**
   - Disable dropdown with gray background
   - Show loading text in dropdown

3. **Subtask List Loading:**
   - Show skeleton loader or spinner in table area

4. **Form Submission:**
   - Disable all form fields
   - Show "Saving..." text on submit button
   - Disable cancel button

## Testing Strategy

### Unit Tests

1. **SubtaskForm Component:**
   - Test required field validation
   - Test numeric field validation (estimated hours, duration days, scrum points)
   - Test form submission with valid data
   - Test form submission with invalid data
   - Test cancel button behavior
   - Test initial data population in edit mode

2. **SubtaskModal Component:**
   - Test modal open/close behavior
   - Test hierarchy context display
   - Test success callback invocation
   - Test error display

3. **SubtasksPage Component:**
   - Test hierarchy filter cascading
   - Test search functionality
   - Test status filter
   - Test URL parameter parsing
   - Test breadcrumb navigation
   - Test admin-only button visibility

### Integration Tests

1. **Create Subtask Flow:**
   - Navigate to subtasks page
   - Select full hierarchy (client → task)
   - Click "New Subtask" button
   - Fill form with valid data
   - Submit and verify subtask appears in list

2. **Edit Subtask Flow:**
   - Navigate to subtask detail page
   - Click edit button
   - Modify fields
   - Submit and verify changes

3. **Filter and Search:**
   - Load subtasks page with data
   - Apply search filter
   - Verify filtered results
   - Apply status filter
   - Verify combined filters work

4. **Hierarchy Navigation:**
   - Select hierarchy levels
   - Verify cascading loads
   - Click breadcrumb items
   - Verify navigation to correct pages

### Manual Testing Checklist

- [ ] Create subtask with all required fields
- [ ] Create subtask with optional fields
- [ ] Attempt to create subtask without required fields (should show errors)
- [ ] Edit existing subtask
- [ ] Search subtasks by title
- [ ] Filter subtasks by status
- [ ] Navigate via breadcrumbs
- [ ] Test as non-admin user (button should be disabled)
- [ ] Test with URL parameters
- [ ] Test responsive layout on mobile
- [ ] Test with empty subtask list
- [ ] Test with no task selected
- [ ] Verify estimated hours accepts decimals
- [ ] Verify duration days only accepts integers
- [ ] Verify scrum points is optional

## UI/UX Considerations

### Responsive Design

- **Desktop (>1024px):** Full table layout with all columns visible
- **Tablet (768px-1024px):** Horizontal scroll for table, stacked hierarchy filters
- **Mobile (<768px):** Card-based layout instead of table, vertical hierarchy filters

### Accessibility

- All form fields have associated labels
- Error messages are announced to screen readers
- Keyboard navigation support (Tab, Enter, Escape)
- Focus management in modal (trap focus, return focus on close)
- ARIA labels for icon buttons
- Color contrast meets WCAG AA standards

### Visual Design

**Color Scheme:**
- Primary action: Blue (#3B82F6)
- Success/Done: Green (#10B981)
- In Progress: Blue (#3B82F6)
- Blocked: Red (#EF4444)
- Default/To Do: Gray (#6B7280)

**Typography:**
- Page title: 3xl, bold
- Section headers: lg, medium
- Body text: sm, regular
- Labels: sm, medium

**Spacing:**
- Page padding: 6 (24px)
- Section gaps: 6 (24px)
- Form field gaps: 4 (16px)
- Button padding: 4 (16px) horizontal, 2 (8px) vertical

### User Feedback

1. **Success Messages:**
   - Toast notification: "Subtask created successfully"
   - Toast notification: "Subtask updated successfully"
   - Auto-dismiss after 3 seconds

2. **Loading Indicators:**
   - Spinner for initial load
   - Disabled state for dropdowns during load
   - "Saving..." text on submit button

3. **Empty States:**
   - Informative message when no subtasks exist
   - Instruction to select hierarchy when incomplete
   - Helpful text for disabled buttons (tooltips)

## Performance Considerations

### Data Fetching Optimization

1. **Lazy Loading:**
   - Only load hierarchy levels when parent is selected
   - Don't fetch subtasks until task is selected

2. **Caching:**
   - Cache hierarchy data in component state
   - Avoid refetching when navigating back

3. **Debouncing:**
   - Debounce search input (300ms delay)
   - Prevent excessive filtering operations

### Rendering Optimization

1. **Memoization:**
   - Use `useMemo` for filtered subtask list
   - Use `useMemo` for derived data (status options)

2. **Virtual Scrolling:**
   - Consider implementing if subtask lists exceed 100 items
   - Use library like `react-virtual` or `react-window`

3. **Code Splitting:**
   - Lazy load SubtaskModal component
   - Lazy load SubtaskForm component

## Security Considerations

### Authorization

1. **Admin-Only Actions:**
   - Create subtask: Admin only
   - Edit subtask: Admin only
   - Delete subtask: Admin only

2. **Frontend Enforcement:**
   - Hide/disable buttons for non-admin users
   - Show tooltip explaining permission requirement

3. **Backend Enforcement:**
   - API endpoints must verify user role
   - Return 403 Forbidden for unauthorized requests

### Data Validation

1. **Input Sanitization:**
   - Sanitize text inputs to prevent XSS
   - Validate numeric inputs on both client and server

2. **SQL Injection Prevention:**
   - Use parameterized queries (already handled by SQLAlchemy)
   - Never concatenate user input into SQL

3. **CSRF Protection:**
   - Use CSRF tokens for state-changing operations
   - Verify tokens on backend

## Migration Strategy

### Phase 1: Backend Implementation
1. Add database migration for new fields (duration_days, scrum_points, estimated_hours)
2. Update Subtask model in SQLAlchemy
3. Create/update API endpoints for subtask CRUD operations
4. Add validation logic in schemas
5. Test API endpoints with Postman/curl

### Phase 2: Frontend Implementation
1. Create SubtaskForm component
2. Create SubtaskModal component
3. Create SubtasksPage component
4. Add routing for /subtasks page
5. Update navigation menu to include Subtasks link

### Phase 3: Integration
1. Connect frontend to backend APIs
2. Test full create/edit/delete flows
3. Verify hierarchy filtering works correctly
4. Test error handling and edge cases

### Phase 4: Polish
1. Add loading states and animations
2. Implement responsive design
3. Add accessibility features
4. Perform cross-browser testing
5. Gather user feedback and iterate

## Dependencies

### New Dependencies
None required - all necessary libraries are already in the project.

### Existing Dependencies
- React 18+
- React Router v6
- TypeScript
- Tailwind CSS
- API service layer (existing)

## Future Enhancements

1. **Bulk Operations:**
   - Select multiple subtasks
   - Bulk status update
   - Bulk assignment

2. **Drag and Drop:**
   - Reorder subtasks within a task
   - Drag subtasks between tasks

3. **Advanced Filtering:**
   - Filter by assignee
   - Filter by phase
   - Filter by date range
   - Save filter presets

4. **Export Functionality:**
   - Export subtasks to CSV
   - Export to Excel
   - Print view

5. **Time Tracking:**
   - Log actual hours worked
   - Compare estimated vs actual
   - Time tracking reports

6. **Comments and Attachments:**
   - Add comments to subtasks
   - Attach files to subtasks
   - Activity history

7. **Notifications:**
   - Email notifications for assignments
   - Due date reminders
   - Status change notifications

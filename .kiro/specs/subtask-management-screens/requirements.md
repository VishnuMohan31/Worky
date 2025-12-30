# Requirements Document

## Introduction

This feature adds comprehensive subtask management screens to the Worky project management platform, mirroring the functionality of the existing task management system. Subtasks are the lowest level in the work breakdown hierarchy (Client → Program → Project → Use Case → User Story → Task → Subtask) and enable granular tracking of work items within tasks.

## Glossary

- **Worky System**: The project management platform that manages hierarchical work breakdown structures
- **Subtask**: A work item that belongs to a parent Task, representing the smallest unit of trackable work
- **Task**: A work item that belongs to a User Story and can contain multiple Subtasks
- **User Story**: A work item that belongs to a Use Case and can contain multiple Tasks
- **Hierarchy Filter**: A cascading selection interface that allows users to navigate through Client → Program → Project → Use Case → User Story → Task levels
- **Admin User**: A user with role "Admin" who has permissions to create, edit, and delete entities
- **Phase**: A workflow stage (e.g., Design, Development, Testing) that can be assigned to tasks and subtasks
- **Assignee**: A user who is responsible for completing a subtask
- **Estimated Hours**: The number of hours expected to complete a subtask (required field)
- **Duration Days**: The number of calendar days expected to complete a subtask (required field)
- **Scrum Points**: Story points assigned to a subtask for agile estimation

## Requirements

### Requirement 1: Subtask List Page

**User Story:** As a project team member, I want to view all subtasks under a selected task, so that I can track granular work items and their status.

#### Acceptance Criteria

1. WHEN THE Worky System displays the subtasks page, THE Worky System SHALL render a page title "Subtasks" with a descriptive subtitle
2. WHEN THE Worky System displays the subtasks page, THE Worky System SHALL display a hierarchical filter bar with cascading dropdowns for Client, Program, Project, Use Case, User Story, and Task selection
3. WHEN a user selects a Client in the hierarchy filter, THE Worky System SHALL load and display all Programs associated with that Client
4. WHEN a user selects a Program in the hierarchy filter, THE Worky System SHALL load and display all Projects associated with that Program
5. WHEN a user selects a Project in the hierarchy filter, THE Worky System SHALL load and display all Use Cases associated with that Project
6. WHEN a user selects a Use Case in the hierarchy filter, THE Worky System SHALL load and display all User Stories associated with that Use Case
7. WHEN a user selects a User Story in the hierarchy filter, THE Worky System SHALL load and display all Tasks associated with that User Story
8. WHEN a user selects a Task in the hierarchy filter, THE Worky System SHALL load and display all Subtasks associated with that Task
9. WHEN all hierarchy selections are not complete, THE Worky System SHALL display a message instructing users to complete all selections
10. WHEN all hierarchy selections are complete, THE Worky System SHALL display a table of subtasks with columns for Title, Status, Assigned To, Phase, Estimated Hours, Duration Days, and Scrum Points

### Requirement 2: Subtask Filtering and Search

**User Story:** As a project team member, I want to filter and search subtasks, so that I can quickly find specific work items.

#### Acceptance Criteria

1. WHEN THE Worky System displays the subtasks list, THE Worky System SHALL provide a search input field that filters subtasks by title
2. WHEN a user types in the search field, THE Worky System SHALL filter the subtask list in real-time to show only matching subtasks
3. WHEN THE Worky System displays the subtasks list, THE Worky System SHALL provide a status filter dropdown showing all unique status values from the current subtask list
4. WHEN a user selects a status filter, THE Worky System SHALL display only subtasks matching that status
5. WHEN a user selects "All Status" in the filter, THE Worky System SHALL display all subtasks regardless of status

### Requirement 3: Breadcrumb Navigation

**User Story:** As a project team member, I want to see breadcrumb navigation showing my current location in the hierarchy, so that I can understand context and navigate back to parent levels.

#### Acceptance Criteria

1. WHEN a user has selected a Client, THE Worky System SHALL display a clickable breadcrumb showing the Client name
2. WHEN a user has selected a Program, THE Worky System SHALL display a clickable breadcrumb showing Client → Program
3. WHEN a user has selected a Project, THE Worky System SHALL display a clickable breadcrumb showing Client → Program → Project
4. WHEN a user has selected a Use Case, THE Worky System SHALL display a clickable breadcrumb showing Client → Program → Project → Use Case
5. WHEN a user has selected a User Story, THE Worky System SHALL display a clickable breadcrumb showing Client → Program → Project → Use Case → User Story
6. WHEN a user has selected a Task, THE Worky System SHALL display a clickable breadcrumb showing Client → Program → Project → Use Case → User Story → Task
7. WHEN a user clicks a breadcrumb item, THE Worky System SHALL navigate to the appropriate page for that entity

### Requirement 4: Subtask Creation

**User Story:** As an Admin user, I want to create new subtasks under a selected task, so that I can break down work into manageable pieces.

#### Acceptance Criteria

1. WHEN THE Worky System displays the subtasks page, THE Worky System SHALL display a "New Subtask" button
2. WHEN a user is not an Admin, THE Worky System SHALL disable the "New Subtask" button and display a tooltip explaining admin-only access
3. WHEN a Task is not selected, THE Worky System SHALL disable the "New Subtask" button and display a tooltip instructing to select a task first
4. WHEN an Admin user clicks the "New Subtask" button, THE Worky System SHALL open a modal dialog with a form for creating a subtask
5. WHEN THE Worky System displays the subtask creation form, THE Worky System SHALL display the selected hierarchy path (Client → Program → Project → Use Case → User Story → Task)
6. WHEN THE Worky System displays the subtask creation form, THE Worky System SHALL require a Title field
7. WHEN THE Worky System displays the subtask creation form, THE Worky System SHALL require an Estimated Hours field with numeric validation
8. WHEN THE Worky System displays the subtask creation form, THE Worky System SHALL require a Duration Days field with numeric validation
9. WHEN THE Worky System displays the subtask creation form, THE Worky System SHALL provide optional fields for Description, Status, Phase, Assigned To, and Scrum Points
10. WHEN a user submits the creation form without Title, Estimated Hours, or Duration Days, THE Worky System SHALL display validation error messages indicating required fields
11. WHEN a user submits the creation form with valid data, THE Worky System SHALL create the subtask and refresh the subtask list
12. WHEN a user submits the creation form with invalid data, THE Worky System SHALL display validation error messages

### Requirement 5: Subtask Details Navigation

**User Story:** As a project team member, I want to click on a subtask row to view its full details, so that I can see comprehensive information about the work item.

#### Acceptance Criteria

1. WHEN THE Worky System displays a subtask in the list, THE Worky System SHALL make the entire row clickable
2. WHEN a user clicks a subtask row, THE Worky System SHALL navigate to the hierarchy detail page for that subtask
3. WHEN a user hovers over a subtask row, THE Worky System SHALL highlight the row to indicate it is clickable

### Requirement 6: Subtask Status Display

**User Story:** As a project team member, I want to see visual indicators for subtask status, so that I can quickly understand the state of work items.

#### Acceptance Criteria

1. WHEN THE Worky System displays a subtask with status "Done", THE Worky System SHALL display a green badge
2. WHEN THE Worky System displays a subtask with status "In Progress", THE Worky System SHALL display a blue badge
3. WHEN THE Worky System displays a subtask with any other status, THE Worky System SHALL display a gray badge
4. WHEN THE Worky System displays a status badge, THE Worky System SHALL show the status text within the badge

### Requirement 7: URL Parameter Support

**User Story:** As a project team member, I want to navigate to the subtasks page with pre-selected hierarchy levels via URL parameters, so that I can share direct links to specific contexts.

#### Acceptance Criteria

1. WHEN THE Worky System loads the subtasks page with a "client" URL parameter, THE Worky System SHALL pre-select that Client in the hierarchy filter
2. WHEN THE Worky System loads the subtasks page with a "program" URL parameter, THE Worky System SHALL pre-select that Program in the hierarchy filter
3. WHEN THE Worky System loads the subtasks page with a "project" URL parameter, THE Worky System SHALL pre-select that Project in the hierarchy filter
4. WHEN THE Worky System loads the subtasks page with a "usecase" URL parameter, THE Worky System SHALL pre-select that Use Case in the hierarchy filter
5. WHEN THE Worky System loads the subtasks page with a "userstory" URL parameter, THE Worky System SHALL pre-select that User Story in the hierarchy filter
6. WHEN THE Worky System loads the subtasks page with a "task" URL parameter, THE Worky System SHALL pre-select that Task in the hierarchy filter

### Requirement 8: Loading States

**User Story:** As a project team member, I want to see loading indicators when data is being fetched, so that I understand the system is working.

#### Acceptance Criteria

1. WHEN THE Worky System is loading initial client data, THE Worky System SHALL display a centered spinner animation
2. WHEN THE Worky System is loading hierarchy level data (programs, projects, etc.), THE Worky System SHALL disable the corresponding dropdown
3. WHEN THE Worky System is loading subtasks, THE Worky System SHALL display a loading indicator in the subtask list area

### Requirement 9: Empty State Handling

**User Story:** As a project team member, I want to see helpful messages when no subtasks exist, so that I understand the current state.

#### Acceptance Criteria

1. WHEN THE Worky System displays a subtask list with zero subtasks after filtering, THE Worky System SHALL display a centered message "No subtasks found for this task"
2. WHEN THE Worky System displays the subtasks page without complete hierarchy selection, THE Worky System SHALL display a blue informational box with instructions to complete all selections

### Requirement 10: Subtask Modal Form

**User Story:** As an Admin user, I want to use a modal form to create and edit subtasks, so that I can manage subtask details without leaving the list page.

#### Acceptance Criteria

1. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL show a title "Create New Subtask" for new subtasks or "Edit Subtask" for existing subtasks
2. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL display the parent task context in an informational box
3. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Title input field marked as required
4. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Task dropdown pre-populated with tasks from the selected user story
5. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Description textarea field
6. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Status dropdown with options: "To Do", "In Progress", "Done", "Blocked"
7. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Phase dropdown populated with active phases
8. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide an Assigned To dropdown with active users
9. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide an Estimated Hours numeric input field marked as required
10. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Duration Days numeric input field marked as required
11. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL provide a Scrum Points numeric input field as optional
12. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL validate that Estimated Hours is a positive number
13. WHEN THE Worky System displays the subtask modal, THE Worky System SHALL validate that Duration Days is a positive integer
14. WHEN a user clicks Cancel in the modal, THE Worky System SHALL close the modal without saving changes
15. WHEN a user clicks Save in the modal with valid data, THE Worky System SHALL save the subtask and close the modal
16. WHEN a user clicks Save in the modal with invalid data, THE Worky System SHALL display validation errors and keep the modal open
17. WHEN a user clicks Save in the modal without required fields (Title, Estimated Hours, Duration Days), THE Worky System SHALL display error messages for each missing required field

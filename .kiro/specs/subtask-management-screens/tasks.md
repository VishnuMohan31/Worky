# Implementation Plan

- [ ] 1. Database and Backend Setup
  - Add database migration to extend subtasks table with duration_days, scrum_points, and estimated_hours columns
  - Update SQLAlchemy Subtask model to include new fields
  - Verify subtask API endpoints exist and support CRUD operations
  - _Requirements: 4.7, 4.8, 4.9, 10.9, 10.10, 10.11_

- [x] 2. Create SubtaskForm Component
  - [x] 2.1 Create base SubtaskForm component structure with TypeScript interfaces
    - Define SubtaskFormProps interface with all required props
    - Define SubtaskFormData interface matching the data model
    - Set up component state for form data and validation errors
    - _Requirements: 4.6, 4.7, 4.8, 4.9, 10.3, 10.4, 10.9, 10.10, 10.11_
  
  - [x] 2.2 Implement form fields with proper validation
    - Add Title input field (required)
    - Add Task dropdown (required, pre-populated)
    - Add Description textarea (optional)
    - Add Status dropdown with options: "To Do", "In Progress", "Done", "Blocked"
    - Add Phase dropdown populated with active phases
    - Add Assigned To dropdown with active users
    - Add Estimated Hours numeric input (required, min: 0, step: 0.5)
    - Add Duration Days numeric input (required, min: 1, step: 1)
    - Add Scrum Points numeric input (optional, min: 0, step: 0.5)
    - _Requirements: 4.6, 4.7, 4.8, 4.9, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11_
  
  - [x] 2.3 Implement client-side validation logic
    - Validate required fields (Title, Estimated Hours, Duration Days)
    - Validate Estimated Hours is positive number
    - Validate Duration Days is positive integer
    - Validate Scrum Points is non-negative if provided
    - Display field-specific error messages
    - _Requirements: 4.10, 4.11, 10.12, 10.13, 10.16, 10.17_
  
  - [x] 2.4 Implement form submission and cancel handlers
    - Handle form submit with validation
    - Call onSubmit callback with form data
    - Handle cancel button click
    - Reset form on successful submission
    - _Requirements: 4.11, 10.14, 10.15_

- [x] 3. Create SubtaskModal Component
  - [x] 3.1 Create modal component structure
    - Set up Modal wrapper with open/close functionality
    - Define SubtaskModalProps interface
    - Implement modal title logic (Create vs Edit)
    - _Requirements: 4.4, 10.1_
  
  - [x] 3.2 Implement hierarchy context display
    - Display selected hierarchy path in informational box
    - Show Client → Program → Project → Use Case → User Story → Task breadcrumb
    - Style with blue background for visibility
    - _Requirements: 4.5, 10.2_
  
  - [x] 3.3 Integrate SubtaskForm component
    - Embed SubtaskForm within modal
    - Pass through all required props
    - Handle form submission success
    - Handle form cancellation
    - _Requirements: 4.4, 4.11_
  
  - [x] 3.4 Implement API integration and error handling
    - Call create API endpoint for new subtasks
    - Call update API endpoint for existing subtasks
    - Display loading state during API calls
    - Handle API errors with user-friendly messages
    - Call onSuccess callback after successful save
    - _Requirements: 4.11, 4.12_

- [x] 4. Create SubtasksPage Component
  - [x] 4.1 Set up page structure and state management
    - Create SubtasksPage component with TypeScript
    - Define state for hierarchy selections (client, program, project, usecase, userstory, task)
    - Define state for data arrays (clients, programs, projects, usecases, userstories, tasks, subtasks, users, phases)
    - Define state for loading flags for each hierarchy level
    - Define state for UI (searchQuery, filterStatus, isModalOpen, editingSubtask)
    - _Requirements: 1.1, 1.2_
  
  - [x] 4.2 Implement hierarchy filter bar with cascading dropdowns
    - Create Client dropdown that loads on mount
    - Create Program dropdown that loads when client is selected
    - Create Project dropdown that loads when program is selected
    - Create Use Case dropdown that loads when project is selected
    - Create User Story dropdown that loads when use case is selected
    - Create Task dropdown that loads when user story is selected
    - Implement cascading logic to clear child selections when parent changes
    - Show loading states for each dropdown
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 8.2_
  
  - [x] 4.3 Implement URL parameter support
    - Parse URL search params on component mount
    - Pre-select hierarchy levels based on URL params (client, program, project, usecase, userstory, task)
    - Trigger cascading loads for pre-selected values
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [x] 4.4 Implement breadcrumb navigation
    - Display breadcrumb showing selected hierarchy path
    - Make each breadcrumb item clickable
    - Navigate to appropriate page when breadcrumb is clicked
    - Show arrow separators between items
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 4.5 Implement search and filter functionality
    - Add search input field that filters subtasks by title
    - Implement real-time filtering as user types
    - Add status filter dropdown with unique status values
    - Implement combined search and status filtering
    - Use useMemo for filtered subtask list
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 4.6 Implement subtask table display
    - Create table with columns: Title, Status, Assigned To, Phase, Estimated Hours, Duration Days, Scrum Points
    - Display subtasks in table rows
    - Make rows clickable to navigate to detail view
    - Add hover effect on rows
    - Display status badges with appropriate colors (green for Done, blue for In Progress, gray for others)
    - Format numeric values appropriately
    - _Requirements: 1.10, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4_
  
  - [x] 4.7 Implement "New Subtask" button with permissions
    - Add "New Subtask" button in filter bar
    - Disable button if user is not Admin
    - Disable button if task is not selected
    - Show tooltip explaining why button is disabled
    - Open SubtaskModal when button is clicked
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 4.8 Implement empty states and loading indicators
    - Show centered spinner during initial client load
    - Display message when no task is selected
    - Display message when no subtasks exist for selected task
    - Show loading indicator while fetching subtasks
    - _Requirements: 1.9, 8.1, 8.3, 9.1, 9.2_
  
  - [x] 4.9 Integrate SubtaskModal and handle CRUD operations
    - Pass all required props to SubtaskModal
    - Handle modal open/close state
    - Refresh subtask list after successful create/update
    - Handle edit mode by passing selected subtask to modal
    - _Requirements: 4.4, 4.11_

- [x] 5. Add Routing and Navigation
  - Add route for /subtasks page in App.tsx
  - Add "Subtasks" link to navigation menu
  - Ensure route is protected (requires authentication)
  - _Requirements: 1.1_

- [x] 6. API Service Integration
  - Verify api.getSubtasks() method exists or create it
  - Verify api.createEntity('subtask', data) works
  - Verify api.updateEntity('subtask', id, data) works
  - Test API error handling and response parsing
  - _Requirements: 4.11, 4.12_

- [x] 7. Styling and Responsive Design
  - Apply Tailwind CSS classes for consistent styling
  - Ensure responsive layout for mobile, tablet, and desktop
  - Test table horizontal scroll on smaller screens
  - Verify modal is responsive and accessible
  - _Requirements: 1.1, 1.2, 1.10_

- [ ] 8. Testing and Quality Assurance
  - [ ]* 8.1 Write unit tests for SubtaskForm validation logic
    - Test required field validation
    - Test numeric field validation
    - Test form submission with valid/invalid data
    - _Requirements: 4.10, 4.11, 4.12_
  
  - [ ]* 8.2 Write unit tests for SubtasksPage filtering
    - Test search functionality
    - Test status filter
    - Test combined filters
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 8.3 Perform manual testing of complete user flows
    - Test create subtask flow
    - Test edit subtask flow
    - Test hierarchy navigation
    - Test URL parameters
    - Test as admin and non-admin users
    - Test empty states
    - Test error scenarios
    - _Requirements: All_

- [ ] 9. Documentation and Cleanup
  - [ ]* 9.1 Add JSDoc comments to components
    - Document component purpose and props
    - Document complex functions
    - _Requirements: All_
  
  - [ ]* 9.2 Update README or developer documentation
    - Document new subtask management feature
    - Add screenshots if applicable
    - Document any new API endpoints
    - _Requirements: All_

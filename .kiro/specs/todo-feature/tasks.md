# Implementation Plan

- [x] 1. Create database schema and migration
  - Create migration file for `todo_items` and `adhoc_notes` tables with all fields, constraints, indexes, and triggers as specified in the design
  - Test migration on development database
  - Verify all indexes are created correctly
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 2. Implement backend data models
  - [x] 2.1 Create TodoItem SQLAlchemy model
    - Write TodoItem model class in `api/app/models/todo.py` with all fields and relationships
    - Add check constraints for visibility and linked_entity_type
    - Add relationship to User model
    - _Requirements: 1.1, 2.1, 3.2, 4.3, 9.1_

  - [x] 2.2 Create AdhocNote SQLAlchemy model
    - Write AdhocNote model class in `api/app/models/todo.py` with all fields and relationships
    - Add check constraint for position
    - Add relationship to User model
    - _Requirements: 5.1, 5.3, 9.2_

  - [x] 2.3 Update User model with TODO relationships
    - Add `todo_items` and `adhoc_notes` relationships to User model
    - _Requirements: 1.1, 5.1_

- [x] 3. Implement Pydantic schemas for request/response validation
  - [x] 3.1 Create TODO item schemas
    - Write schemas in `api/app/schemas/todo.py`: TodoItemBase, TodoItemCreate, TodoItemUpdate, TodoItemResponse, TodoItemList
    - Add LinkedTaskInfo schema for task/subtask summary data
    - Add MoveTodoItemRequest and LinkTodoItemRequest schemas
    - Include field validators for title length, date format, visibility values
    - _Requirements: 8.7, 3.3, 4.5_

  - [x] 3.2 Create ADHOC note schemas
    - Write schemas in `api/app/schemas/todo.py`: AdhocNoteBase, AdhocNoteCreate, AdhocNoteUpdate, AdhocNoteResponse, AdhocNoteList
    - Add ReorderAdhocNoteRequest schema
    - Include field validators for title length, color format, position
    - _Requirements: 8.7, 5.3, 5.4_

- [x] 4. Implement CRUD operations layer
  - [x] 4.1 Create TodoItem CRUD operations
    - Write CRUD class in `api/app/crud/crud_todo.py` with methods: get, get_multi, get_by_user, get_by_date_range, create, update, delete (soft), move, link_entity, unlink_entity
    - Implement visibility filtering logic (private vs public)
    - Implement date range filtering
    - _Requirements: 1.2, 1.4, 2.2, 2.3, 3.2, 3.5, 4.4, 4.5, 8.1, 8.3, 8.4_

  - [x] 4.2 Create AdhocNote CRUD operations
    - Write CRUD class in `api/app/crud/crud_todo.py` with methods: get, get_multi, get_by_user, create, update, delete (soft), reorder
    - Implement position management for reordering
    - _Requirements: 5.3, 5.4, 5.5, 8.2_

  - [x] 4.3 Create task/subtask summary service
    - Write service in `api/app/services/todo_service.py` with methods: get_task_summary, get_subtask_summary
    - Fetch read-only high-level info (title, status, due_date, assigned_to)
    - Validate that linked entities exist before creating links
    - _Requirements: 3.3, 3.6, 8.5_

- [x] 5. Implement API endpoints for TODO items
  - [x] 5.1 Create TODO items router
    - Create router file `api/app/api/v1/endpoints/todos.py`
    - Implement GET /api/v1/todos endpoint with date range and public filtering
    - Implement POST /api/v1/todos endpoint for creating TODO items
    - Implement PUT /api/v1/todos/{todo_id} endpoint for updating TODO items
    - Implement DELETE /api/v1/todos/{todo_id} endpoint for soft deleting TODO items
    - Add authentication dependency to all endpoints
    - Add authorization checks (user can only access own items)
    - _Requirements: 8.1, 8.6, 1.5, 2.2, 2.3_

  - [x] 5.2 Create TODO item action endpoints
    - Implement PATCH /api/v1/todos/{todo_id}/move endpoint for moving items between panes
    - Implement POST /api/v1/todos/{todo_id}/link endpoint for linking to task/subtask
    - Implement DELETE /api/v1/todos/{todo_id}/link endpoint for unlinking
    - Add validation for linked entity existence
    - _Requirements: 4.4, 4.5, 3.2, 3.5, 8.4_

  - [x] 5.3 Create task summary endpoints
    - Implement GET /api/v1/tasks/{task_id}/summary endpoint for read-only task info
    - Implement GET /api/v1/subtasks/{subtask_id}/summary endpoint for read-only subtask info
    - Ensure endpoints only return summary data, no modification allowed
    - _Requirements: 3.3, 3.6, 8.5_

- [x] 6. Implement API endpoints for ADHOC notes
  - Create router file `api/app/api/v1/endpoints/adhoc_notes.py`
  - Implement GET /api/v1/adhoc-notes endpoint
  - Implement POST /api/v1/adhoc-notes endpoint for creating notes
  - Implement PUT /api/v1/adhoc-notes/{note_id} endpoint for updating notes
  - Implement DELETE /api/v1/adhoc-notes/{note_id} endpoint for soft deleting notes
  - Implement PATCH /api/v1/adhoc-notes/{note_id}/reorder endpoint for reordering
  - Add authentication and authorization checks
  - _Requirements: 8.2, 5.3, 5.4, 5.5, 8.6_

- [x] 7. Register TODO routes in main API router
  - Import TODO and ADHOC notes routers in `api/app/api/v1/router.py`
  - Register routers with appropriate prefixes and tags
  - _Requirements: 8.1, 8.2_

- [x] 8. Implement frontend TypeScript types and interfaces
  - Create types file `ui/src/types/todo.ts`
  - Define TodoItem, AdhocNote, LinkedTaskInfo interfaces
  - Define request/response types for API calls
  - Define Pane interface for time-based panes
  - _Requirements: 4.1, 5.1_

- [x] 9. Implement frontend API service layer
  - [x] 9.1 Create TODO items API service
    - Create service file `ui/src/services/todoApi.ts`
    - Implement functions: fetchTodoItems, createTodoItem, updateTodoItem, deleteTodoItem, moveTodoItem, linkTodoItem, unlinkTodoItem
    - Implement functions: fetchTaskSummary, fetchSubtaskSummary
    - Use axios with authentication headers
    - Handle error responses and return typed data
    - _Requirements: 8.1, 8.3, 8.4, 8.5_

  - [x] 9.2 Create ADHOC notes API service
    - Add functions to `ui/src/services/todoApi.ts`: fetchAdhocNotes, createAdhocNote, updateAdhocNote, deleteAdhocNote, reorderAdhocNote
    - Use axios with authentication headers
    - Handle error responses and return typed data
    - _Requirements: 8.2_

- [x] 10. Implement TODO Dashboard page component
  - Create page component `ui/src/pages/TodoPage.tsx`
  - Implement state management for TODO items and ADHOC notes
  - Implement data fetching on component mount using React Query
  - Implement date selection state for calculating panes
  - Implement loading and error states
  - Create page layout with Time Panes and ADHOC pane
  - _Requirements: 1.5, 7.2, 7.5_

- [x] 11. Implement Time Panes component
  - [x] 11.1 Create Time Panes container component
    - Create component `ui/src/components/todo/TimePanes.tsx`
    - Calculate four panes (Yesterday, Today, Tomorrow, Day After Tomorrow) based on current date
    - Filter TODO items by target_date for each pane
    - Render four pane columns with labels and dates
    - _Requirements: 4.1, 4.2_

  - [x] 11.2 Implement drag and drop functionality
    - Add react-dnd or native HTML5 drag and drop
    - Implement drag start, drag over, and drop handlers
    - Update TODO item target_date when dropped in new pane
    - Call API to persist the move
    - Implement optimistic UI updates
    - _Requirements: 4.4, 4.5, 6.2_

  - [x] 11.3 Create individual pane component
    - Create component `ui/src/components/todo/TimePane.tsx`
    - Display pane label and date
    - Render list of TODO items for that pane
    - Handle drop events for the pane
    - Style with modern card layout
    - _Requirements: 4.1, 4.2, 6.1_

- [x] 12. Implement TODO Item Card component
  - Create component `ui/src/components/todo/TodoItemCard.tsx`
  - Display title, description, visibility badge
  - Display link indicator if linked to task/subtask
  - Implement expandable panel for linked task info
  - Add action buttons: edit, delete, toggle visibility
  - Implement drag handle for drag and drop
  - Style with card design, hover effects, and color-coded borders
  - _Requirements: 2.1, 2.2, 3.3, 6.1, 6.3, 6.4_

- [x] 13. Implement Task Link Info Panel component
  - Create component `ui/src/components/todo/TaskLinkInfoPanel.tsx`
  - Display read-only task/subtask information (title, status, due date, assigned user)
  - Display entity ID and type
  - Add link to view full task in hierarchy view
  - Show read-only indicator (lock icon)
  - Style with compact panel and status color-coding
  - _Requirements: 3.3, 3.6_

- [x] 14. Implement TODO Item Form Modal component
  - Create component `ui/src/components/todo/TodoItemFormModal.tsx`
  - Implement form with fields: title, description, target_date, visibility, linked entity
  - Add task/subtask search dropdown for linking
  - Implement form validation (title required, max lengths)
  - Handle create and edit modes
  - Call API on form submit
  - Display validation errors
  - _Requirements: 2.1, 2.5, 3.2, 4.3, 8.7_

- [x] 15. Implement ADHOC Notes Pane component
  - [x] 15.1 Create ADHOC Notes container component
    - Create component `ui/src/components/todo/AdhocNotesPane.tsx`
    - Fetch and display ADHOC notes
    - Implement add note button
    - Render notes in masonry or grid layout
    - _Requirements: 5.1, 5.3_

  - [x] 15.2 Implement ADHOC note card component
    - Create component `ui/src/components/todo/AdhocNoteCard.tsx`
    - Display title and content
    - Style as sticky note (yellow background, slight rotation)
    - Add edit and delete buttons
    - Implement drag handle for reordering
    - _Requirements: 5.2, 5.3, 5.5_

  - [x] 15.3 Implement ADHOC note reordering
    - Add drag and drop for reordering notes
    - Update position values when notes are reordered
    - Call API to persist new positions
    - Implement optimistic UI updates
    - _Requirements: 5.4_

- [x] 16. Implement ADHOC Note Form Modal component
  - Create component `ui/src/components/todo/AdhocNoteFormModal.tsx`
  - Implement form with fields: title, content, color
  - Add color picker for note color
  - Implement form validation
  - Handle create and edit modes
  - Call API on form submit
  - _Requirements: 5.3_

- [x] 17. Add TODO navigation item to left sidebar
  - Update navigation component `ui/src/components/layout/Sidebar.tsx`
  - Add TODO menu item with icon
  - Add badge showing count of today's TODO items
  - Link to TODO page route
  - _Requirements: 7.1, 7.3, 7.4_

- [x] 18. Implement routing for TODO page
  - Add TODO route to `ui/src/App.tsx`
  - Configure route path as `/todos`
  - Add protected route wrapper for authentication
  - _Requirements: 7.2_

- [x] 19. Implement error handling and user feedback
  - Add error boundary for TODO feature
  - Implement toast notifications for success/error messages
  - Display user-friendly error messages for API failures
  - Implement retry logic for failed API calls
  - Add loading skeletons for better UX
  - _Requirements: 8.8_

- [x] 20. Implement responsive design and accessibility
  - Add responsive breakpoints for desktop, tablet, mobile
  - Implement mobile-friendly layout (tabs for panes)
  - Add keyboard navigation support
  - Add ARIA labels to all interactive elements
  - Ensure focus indicators are visible
  - Test color contrast for WCAG AA compliance
  - _Requirements: 6.5, 6.6_

- [x] 21. Apply styling and animations
  - Implement color palette from design guidelines
  - Add hover effects and transitions
  - Implement drag animations (scale, shadow)
  - Add modal open/close animations
  - Style cards with shadows and borders
  - Ensure consistent spacing throughout
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ]* 22. Write backend unit tests
  - Write tests for TodoItem CRUD operations
  - Write tests for AdhocNote CRUD operations
  - Write tests for visibility filtering logic
  - Write tests for date range filtering
  - Write tests for task/subtask linking validation
  - Write tests for soft delete functionality
  - _Requirements: 1.1, 2.2, 3.2, 4.4, 5.3, 9.5_

- [ ]* 23. Write frontend unit tests
  - Write tests for TodoItemCard component rendering
  - Write tests for drag and drop logic
  - Write tests for date calculations in TimePanes
  - Write tests for visibility toggle
  - Write tests for form validation
  - Write tests for ADHOC note reordering
  - _Requirements: 2.5, 4.4, 5.4, 6.2_

- [ ]* 24. Write integration tests
  - Write test for complete TODO item lifecycle
  - Write test for linking TODO to task and fetching task info
  - Write test for public TODO visibility across users
  - Write test for ADHOC note CRUD operations
  - Write test for authentication and authorization
  - _Requirements: 1.1, 2.2, 3.2, 8.6_

- [x] 25. Final integration and testing
  - Test complete user flow from navigation to TODO operations
  - Verify drag and drop works smoothly across all panes
  - Verify public/private visibility works correctly
  - Verify task linking displays correct read-only info
  - Verify ADHOC notes can be created, reordered, and deleted
  - Test on different browsers and screen sizes
  - Verify no modifications to main project hierarchy are possible
  - _Requirements: 1.3, 3.6, 4.6, 5.6, 6.2, 7.2_

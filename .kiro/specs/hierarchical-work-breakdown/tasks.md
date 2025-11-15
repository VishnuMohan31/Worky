# Implementation Plan

## Overview
This implementation plan breaks down the hierarchical work breakdown structure feature into discrete, manageable coding tasks. Each task builds incrementally on previous work, ensuring no orphaned code. Tasks are organized by layer (Database, API, UI) and include references to specific requirements.

## Task List

- [ ] 1. Database Schema and Models Setup
- [x] 1.1 Create database migration for core entity tables
  - Create migration file for clients, programs, projects, usecases, user_stories tables
  - Add all required columns (id, name, description, status, dates, foreign keys)
  - Add indexes on foreign keys and frequently queried columns
  - Add soft delete (is_deleted) columns
  - _Requirements: 1.1, 9.1, 9.2_

- [x] 1.2 Create database migration for tasks, subtasks, and phases tables
  - Create tasks table with phase_id foreign key
  - Create subtasks table with constraint preventing subtasks under subtasks
  - Create phases table with default phases (Development, Analysis, Design, Testing)
  - Add indexes on all foreign keys and status columns
  - _Requirements: 10.1, 10.2, 11.1, 11.2_

- [x] 1.3 Create database migration for bugs and audit tables
  - Create bugs table with polymorphic entity_type and entity_id columns
  - Create audit_logs table with JSONB changes column
  - Create entity_history table for field-level tracking
  - Add indexes for efficient querying
  - _Requirements: 2.1, 2.2, 17.1, 17.2_

- [x] 1.4 Implement SQLAlchemy models for all entities
  - Create BaseModel with common fields (id, created_at, updated_at, is_deleted)
  - Implement Client, Program, Project, UseCase, UserStory models with relationships
  - Implement Task, Subtask models with phase relationship
  - Implement Phase and Bug models
  - _Requirements: 1.1, 9.1, 10.1, 11.1_

- [ ]* 1.5 Create database seed data for development
  - Create seed script with sample clients, programs, projects
  - Add sample use cases, user stories, tasks, and subtasks
  - Add sample bugs at various hierarchy levels
  - _Requirements: N/A (Development support)_

- [-] 2. Core API Services and Business Logic
- [x] 2.1 Implement HierarchyService with basic CRUD operations
  - Create HierarchyService class with database session injection
  - Implement get_entity_with_context method for retrieving entity with parent and children
  - Implement get_parent_entity and get_child_entities methods
  - Implement get_breadcrumb method for hierarchy trail
  - Add client-level data isolation checks
  - _Requirements: 1.1, 3.1, 5.1, 5.2, 6.1_

- [x] 2.2 Implement entity creation methods in HierarchyService
  - Implement create_client, create_program, create_project methods
  - Implement create_usecase, create_user_story methods
  - Implement create_task with phase validation
  - Implement create_subtask with parent task validation
  - Add role-based permission checks
  - _Requirements: 1.1, 3.1, 7.1, 10.1, 10.2_

- [x] 2.3 Implement entity update and delete methods in HierarchyService
  - Implement update methods for all entity types
  - Implement soft delete methods with cascade checks
  - Add validation to prevent deletion of entities with active children
  - Implement cache invalidation on updates and deletes
  - _Requirements: 4.1, 9.2, 10.2, 26.4_

- [x] 2.4 Implement statistics and rollup calculations in HierarchyService
  - Implement get_entity_statistics method with status counts
  - Implement phase distribution calculation for tasks/subtasks
  - Implement rollup counts for all descendant entities
  - Calculate completion percentages
  - _Requirements: 8.1, 8.2, 13.1, 13.2, 25.1, 25.2_

- [x] 2.5 Implement global search functionality in HierarchyService
  - Implement search_entities method with full-text search
  - Add support for filtering by entity types
  - Implement pagination for search results
  - Generate hierarchy paths for search results
  - Apply client-level filtering for non-Admin users
  - _Requirements: 2.1, 2.2, 2.3, 6.1, 6.2_

- [x] 3. Phase Management Service
- [x] 3.1 Implement PhaseService with CRUD operations
  - Create PhaseService class
  - Implement list_phases method with active/inactive filter
  - Implement create_phase method (Admin only)
  - Implement update_phase method (Admin only)
  - Implement deactivate_phase with usage count validation
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 24.1, 24.2_

- [x] 3.2 Implement phase usage tracking and statistics
  - Implement get_phase_usage_count method
  - Implement get_phase_usage method with breakdown by entity
  - Add phase distribution calculations
  - _Requirements: 13.1, 13.2, 13.3, 24.3_

- [ ] 4. Bug Management Service
- [ ] 4.1 Implement BugService with CRUD operations
  - Create BugService class
  - Implement list_bugs with filtering by entity, severity, status, assignee
  - Implement create_bug with entity association
  - Implement update_bug method
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4.2 Implement bug assignment and resolution workflows
  - Implement assign_bug method
  - Implement resolve_bug method with resolution notes
  - Add status transition validation
  - Send notifications on bug assignment and resolution
  - _Requirements: 2.5, 3.1_



- [ ] 5. Caching Layer Implementation
- [ ] 5.1 Implement Redis cache service
  - Create CacheService class with Redis connection
  - Implement get, set, delete, and delete_pattern methods
  - Implement invalidate_entity method for cache invalidation
  - Add TTL support (default 5 minutes)
  - _Requirements: 26.1, 26.2, 26.3, 26.4_

- [ ] 5.2 Integrate caching into HierarchyService
  - Add cache checks in get_entity_with_context method
  - Implement cache invalidation on entity create, update, delete
  - Add cache metrics tracking (hits/misses)
  - _Requirements: 26.1, 26.2, 26.4_

- [ ] 6. Authentication and Authorization Middleware
- [ ] 6.1 Implement JWT authentication middleware
  - Create AuthMiddleware to extract and verify JWT tokens
  - Attach user info (user_id, role, client_id) to request state
  - Handle token expiration and invalid tokens
  - _Requirements: 3.1, 3.2, 13.1, 13.2, 20.1, 20.2_

- [ ] 6.2 Implement role-based access control decorators
  - Create require_role decorator for endpoint protection
  - Implement permission checks for each entity type and operation
  - Add client-level data isolation enforcement
  - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 19.1_

- [ ] 7. Audit Logging Middleware
- [ ] 7.1 Implement audit logging middleware
  - Create AuditMiddleware to capture all state-changing operations
  - Log user_id, entity_type, entity_id, action, changes, request_id
  - Store audit logs in immutable audit_logs table
  - _Requirements: 15.1, 15.2, 17.1, 17.2, 17.3_

- [ ] 7.2 Implement structured logging for activity and system events
  - Create StructuredLogger class with JSON formatting
  - Implement log_activity method for user actions
  - Implement log_system method for system events
  - Add request_id and user_id context variables
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 16.1, 16.2_

- [x] 8. API Endpoints - Hierarchy Management
- [x] 8.1 Implement generic entity retrieval endpoint
  - Create GET /api/v1/hierarchy/{entity_type}/{entity_id} endpoint
  - Return entity with parent, children, and breadcrumb
  - Apply client-level access control
  - Add response caching headers
  - _Requirements: 5.1, 5.2, 11.1, 11.2_

- [x] 8.2 Implement Client endpoints
  - Create GET /api/v1/hierarchy/clients (list with pagination)
  - Create POST /api/v1/hierarchy/clients (Admin only)
  - Create PUT /api/v1/hierarchy/clients/{id} (Admin only)
  - Add request validation using Pydantic schemas
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1_

- [x] 8.3 Implement Program endpoints
  - Create GET /api/v1/hierarchy/clients/{client_id}/programs
  - Create POST /api/v1/hierarchy/programs (Admin, Architect)
  - Create PUT /api/v1/hierarchy/programs/{id}
  - Create DELETE /api/v1/hierarchy/programs/{id} (soft delete)
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1_

- [x] 8.4 Implement Project endpoints
  - Create GET /api/v1/hierarchy/programs/{program_id}/projects
  - Create POST /api/v1/hierarchy/projects (Admin, Architect)
  - Create PUT /api/v1/hierarchy/projects/{id}
  - Create DELETE /api/v1/hierarchy/projects/{id} (soft delete)
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1_

- [x] 8.5 Implement Use Case endpoints
  - Create GET /api/v1/hierarchy/projects/{project_id}/usecases
  - Create POST /api/v1/hierarchy/usecases (Admin, Architect, Designer)
  - Create PUT /api/v1/hierarchy/usecases/{id}
  - Create DELETE /api/v1/hierarchy/usecases/{id} (soft delete)
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1_

- [x] 8.6 Implement User Story endpoints
  - Create GET /api/v1/hierarchy/usecases/{usecase_id}/userstories
  - Create POST /api/v1/hierarchy/userstories (Admin, Architect, Designer)
  - Create PUT /api/v1/hierarchy/userstories/{id}
  - Create DELETE /api/v1/hierarchy/userstories/{id} (soft delete)
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1_

- [x] 8.7 Implement Task endpoints
  - Create GET /api/v1/hierarchy/userstories/{story_id}/tasks with phase and status filters
  - Create POST /api/v1/hierarchy/tasks with phase_id validation
  - Create PUT /api/v1/hierarchy/tasks/{id}
  - Create DELETE /api/v1/hierarchy/tasks/{id} (soft delete)
  - _Requirements: 4.1, 4.2, 11.1, 11.3, 12.1, 23.1_

- [x] 8.8 Implement Subtask endpoints
  - Create GET /api/v1/hierarchy/tasks/{task_id}/subtasks
  - Create POST /api/v1/hierarchy/subtasks with parent task validation
  - Create PUT /api/v1/hierarchy/subtasks/{id}
  - Create DELETE /api/v1/hierarchy/subtasks/{id} (soft delete)
  - Validate that parent is a Task, not another Subtask
  - _Requirements: 4.1, 4.2, 10.1, 10.2, 11.1, 11.3_

- [x] 8.9 Implement statistics endpoint
  - Create GET /api/v1/hierarchy/{entity_type}/{entity_id}/statistics
  - Return status counts, phase distribution, rollup counts, completion percentage
  - Apply client-level access control
  - _Requirements: 8.1, 8.2, 8.3, 25.1, 25.2, 25.3, 25.4_

- [x] 8.10 Implement global search endpoint
  - Create GET /api/v1/hierarchy/search with query parameter
  - Support filtering by entity_types
  - Implement pagination
  - Return results with hierarchy paths
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 6.1, 6.2, 6.3_

- [x] 9. API Endpoints - Phase Management
- [x] 9.1 Implement Phase CRUD endpoints
  - Create GET /api/v1/phases (list with active/inactive filter)
  - Create POST /api/v1/phases (Admin only)
  - Create PUT /api/v1/phases/{id} (Admin only)
  - Create POST /api/v1/phases/{id}/deactivate (Admin only with usage validation)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 24.1, 24.2_

- [x] 9.2 Implement Phase usage endpoint
  - Create GET /api/v1/phases/{id}/usage
  - Return usage count and breakdown by entity
  - _Requirements: 13.1, 24.3_

- [ ] 10. API Endpoints - Bug Management
- [ ] 10.1 Implement Bug CRUD endpoints
  - Create GET /api/v1/bugs with filters (entity, severity, status, assignee)
  - Create POST /api/v1/bugs with entity association
  - Create PUT /api/v1/bugs/{id}
  - Implement pagination
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 11.1_

- [ ] 10.2 Implement Bug workflow endpoints
  - Create POST /api/v1/bugs/{id}/assign
  - Create POST /api/v1/bugs/{id}/resolve with resolution notes
  - Add status transition validation
  - _Requirements: 2.5_

- [ ] 11. Monitoring and Metrics
- [ ] 11.1 Implement Prometheus metrics collection
  - Create metrics for entity operations (counter, histogram)
  - Create metrics for hierarchy navigation
  - Create metrics for search operations
  - Create metrics for cache hits/misses
  - Create gauges for active entities and phase distribution
  - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_

- [ ] 11.2 Implement metrics middleware
  - Create MetricsMiddleware to track request duration and counts
  - Parse entity type and operation from request path
  - Record metrics for all entity operations
  - _Requirements: 21.1, 22.1_

- [ ] 11.3 Create Grafana dashboard configuration
  - Create dashboard JSON for hierarchy management metrics
  - Add panels for operation rates, duration, cache hit rate
  - Add panels for active entities and phase distribution
  - _Requirements: 22.1, 22.2_



- [x] 12. UI Components - Core Hierarchy Navigation
- [x] 12.1 Create Zustand store for hierarchy navigation state
  - Create useHierarchyStore with currentEntity, parentEntity, childEntities state
  - Implement navigateToEntity action to load entity and update all panes
  - Implement setCurrentEntity, setParentEntity, setChildEntities actions
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 12.2 Implement HierarchyNavigator component with three-pane layout
  - Create main pane for current entity details
  - Create resizable top context pane for parent entity
  - Create resizable bottom context pane for child entities
  - Persist pane sizes to localStorage
  - Implement click handlers for parent and child navigation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 9.1, 9.2, 9.3, 9.4_

- [x] 12.3 Implement Breadcrumb navigation component
  - Display full hierarchy path from Client to current entity
  - Make each breadcrumb item clickable for navigation
  - Truncate long names with ellipsis and show full text on hover
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 12.4 Implement EntityDetails component
  - Display entity name, description, status, dates
  - Show assigned users for tasks/subtasks
  - Display phase badge for tasks/subtasks
  - Show entity-specific fields based on type
  - _Requirements: 4.1, 5.1, 23.3_

- [x] 12.5 Implement EntityList component for context panes
  - Display list of entities with name, status, and summary info
  - Implement click handler for drill-down navigation
  - Show empty state when no children exist
  - Add "Add Child" button in header
  - _Requirements: 5.2, 5.3, 5.5, 7.1, 7.2_

- [x] 12.6 Implement EntityCard component for list items
  - Display entity name, status badge, and key metrics
  - Show phase badge for tasks/subtasks
  - Add hover effects and click handling
  - _Requirements: 4.1, 23.3_

- [-] 13. UI Components - Entity Forms
- [x] 13.1 Create generic EntityForm component
  - Implement form with name, description, status fields
  - Add date pickers for start_date and end_date
  - Implement form validation
  - Handle create and update modes
  - _Requirements: 4.1, 4.2, 4.3, 7.1, 7.2_

- [x] 13.2 Create TaskForm component with phase selection
  - Extend EntityForm with phase dropdown
  - Add assignee selection
  - Add estimated_hours and due_date fields
  - Validate phase_id is required
  - _Requirements: 7.1, 11.1, 23.1, 23.2_

- [x] 13.3 Create SubtaskForm component
  - Extend EntityForm with phase dropdown
  - Add assignee selection
  - Validate parent is a Task (not Subtask)
  - _Requirements: 7.1, 10.1, 10.2, 11.1_

- [ ] 13.4 Create BugForm component
  - Add entity type and entity ID selection
  - Add severity and priority dropdowns
  - Add description textarea
  - Add assignee selection
  - _Requirements: 2.1, 2.2, 7.1_

- [ ] 13.5 Implement form modals for entity creation
  - Create modal wrapper component
  - Integrate with EntityForm, TaskForm, SubtaskForm, BugForm
  - Handle form submission and error display
  - Close modal on successful creation
  - _Requirements: 4.5, 7.1, 7.2, 7.3_

- [-] 14. UI Components - Search and Filtering
- [x] 14.1 Implement GlobalSearch component
  - Create search input with debounced query
  - Display search results with entity type, name, and hierarchy path
  - Implement click handler to navigate to entity
  - Show loading state during search
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 6.1, 6.2_

- [ ] 14.2 Implement filter controls for entity lists
  - Add status filter dropdown
  - Add phase filter dropdown (for tasks/subtasks)
  - Add assignee filter dropdown
  - Add date range filter
  - _Requirements: 4.3, 6.4, 23.4_

- [x] 15. UI Components - Statistics and Reporting
- [x] 15.1 Implement EntityStatistics component
  - Display status distribution with counts
  - Show completion progress bar
  - Display phase distribution pie chart (for User Stories and above)
  - Show rollup counts table
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 25.1, 25.2, 25.3, 25.4, 25.5_

- [x] 15.2 Implement phase distribution chart
  - Use Recharts PieChart for phase visualization
  - Color code by phase (Development, Analysis, Design, Testing)
  - Add click handler to filter by phase
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 16. UI Components - Phase Management (Admin)
- [x] 16.1 Implement PhaseManager component
  - Display table of all phases with name, description, color, status
  - Add "Create Phase" button (Admin only)
  - Show usage count for each phase
  - Add Edit and Deactivate buttons
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 24.1, 24.2_

- [x] 16.2 Implement PhaseForm component
  - Add name and description inputs
  - Add color picker for phase color
  - Add active/inactive toggle
  - Validate unique phase name
  - _Requirements: 12.3, 12.4, 24.2_

- [x] 17. UI Components - Bug Tracking
- [x] 17.1 Implement BugList component
  - Display bugs with title, severity, priority, status
  - Add filters for severity, status, assignee
  - Show associated entity information
  - Add "Create Bug" button
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 17.2 Implement BugDetails component
  - Display bug title, description, severity, priority, status
  - Show reporter and assignee information
  - Display associated entity with link
  - Show resolution notes if resolved
  - Add Assign and Resolve buttons
  - _Requirements: 2.1, 2.2, 2.5_

- [x] 18. UI Components - Audit History
- [x] 18.1 Implement AuditHistory component
  - Display audit log entries in reverse chronological order
  - Show timestamp, user, action, and changed fields
  - Add filters for date range and action type
  - Implement pagination (100 entries per page)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 19. UI Integration and Routing
- [x] 19.1 Set up React Router routes for hierarchy navigation
  - Add route /hierarchy/:type/:id for HierarchyNavigator
  - Add route /admin/phases for PhaseManager
  - Add route /bugs for BugList
  - Add route /bugs/:id for BugDetails
  - _Requirements: 5.1, 5.4_

- [x] 19.2 Integrate React Query for server state management
  - Set up QueryClient with cache configuration
  - Create useEntity hook for entity fetching
  - Create useCreateEntity, useUpdateEntity, useDeleteEntity hooks
  - Implement cache invalidation on mutations
  - _Requirements: 26.1, 26.2, 26.3, 26.4_

- [x] 19.3 Implement API service methods
  - Add getEntity, createEntity, updateEntity, deleteEntity methods
  - Add getEntityStatistics method
  - Add searchEntities method
  - Add phase and bug management methods
  - Handle authentication token in request headers
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 19.4 Integrate with existing Worky theme system
  - Apply theme CSS variables to new components
  - Ensure compatibility with all 6 themes
  - Test dark mode compatibility
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 19.5 Integrate with existing i18n system
  - Add translation keys for all new UI text
  - Support English and Telugu languages
  - Test language switching
  - _Requirements: 7.1, 7.2_

- [ ] 20. Performance Optimization
- [ ] 20.1 Implement virtual scrolling for large entity lists
  - Use @tanstack/react-virtual for entity lists
  - Set appropriate item size and overscan
  - Test with 1000+ entities
  - _Requirements: 26.5_

- [ ] 20.2 Implement code splitting for lazy loading
  - Lazy load HierarchyNavigator component
  - Lazy load PhaseManager component
  - Lazy load BugTracker component
  - Add loading fallback components
  - _Requirements: N/A (Performance optimization)_

- [ ] 20.3 Optimize database queries with eager loading
  - Add selectinload for relationships in queries
  - Implement cursor-based pagination for large datasets
  - Create materialized views for statistics
  - _Requirements: 26.1, 26.5_

- [ ] 21. Security Hardening
- [ ] 21.1 Implement input sanitization
  - Sanitize all user inputs to prevent XSS
  - Validate all inputs against expected formats
  - Implement SQL injection protection
  - _Requirements: 12.2, 19.4_

- [ ] 21.2 Implement rate limiting
  - Add rate limiting middleware (100 requests/minute per user)
  - Return 429 status code when limit exceeded
  - _Requirements: 19.2_

- [ ] 21.3 Implement CSRF protection
  - Add CSRF token generation and validation
  - Include CSRF token in all state-changing requests
  - _Requirements: 19.3_



- [x] 22. Entity Notes/Comments Feature
- [x] 22.1 Create API endpoints for entity notes
  - Create GET /api/v1/hierarchy/{entity_type}/{entity_id}/notes endpoint
  - Create POST /api/v1/hierarchy/{entity_type}/{entity_id}/notes endpoint
  - Return notes with creator name and timestamp
  - Implement pagination (default 100 notes)
  - Apply access control (users assigned to project or entity can view/add notes)
  - _Requirements: Comments on any hierarchy element_

- [x] 22.2 Implement EntityNotes UI component
  - Display notes in reverse chronological order (time series)
  - Show creator name, timestamp, and note text
  - Add "Add Note" form with textarea
  - Implement auto-refresh or real-time updates
  - Show loading and empty states
  - _Requirements: Display comments with user names in time series_

- [x] 22.3 Integrate notes into EntityDetails component
  - Replace placeholder "Add Note" button with functional component
  - Display notes section below entity details
  - Add collapsible section for notes
  - Show note count badge
  - _Requirements: Comments visible on entity UI_

- [ ] 23. Documentation and Configuration
- [ ] 23.1 Update API documentation
  - Document all new endpoints in OpenAPI/Swagger
  - Add request/response examples
  - Document authentication requirements
  - Document error responses
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 23.2 Update database documentation
  - Document all new tables and columns
  - Document foreign key relationships
  - Document indexes and constraints
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 23.3 Create deployment configuration
  - Update docker-compose.yml with Redis service
  - Update environment variables for new features
  - Update Ansible inventory with new configuration
  - _Requirements: N/A (Deployment)_

- [ ] 23.4 Update README with new features
  - Document hierarchy navigation feature
  - Document phase management
  - Document bug tracking
  - Add screenshots of new UI
  - _Requirements: N/A (Documentation)_

## Notes

- All tasks marked with * are optional and focus on testing or development support
- Tasks should be executed in order as they build on each other
- Each task includes specific requirement references for traceability
- Cache invalidation should be implemented alongside entity mutations
- All API endpoints must enforce role-based access control
- All database operations must respect soft delete (is_deleted) flag
- All UI components must support both English and Telugu languages
- All UI components must be compatible with all 6 Worky themes

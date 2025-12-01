# Implementation Plan: QA Testing and Bug Management System

## Overview

This implementation plan breaks down the QA Testing and Bug Management feature into discrete, actionable tasks following the Test Run-centric hierarchy: Test Runs → Test Cases → Bugs. Each task builds incrementally on previous work, ensuring a systematic approach to implementation.

## Task List

- [x] 1. Database Schema and Migrations
- [x] 1.1 Create test_runs table migration
  - Write Alembic migration script for test_runs table with hierarchy associations
  - Add fields: name, purpose, short_description, long_description, component_attached_to, run_type, status
  - Add constraint to ensure only one hierarchy level is set (project_id through subtask_id)
  - Add indexes for hierarchy relationships and status
  - Test migration up and down
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.10, 9.1, 9.4_

- [x] 1.2 Create test_cases table migration
  - Write Alembic migration script for test_cases table linked to test_runs
  - Add fields: test_case_name, test_case_description, test_case_steps, expected_result, actual_result, inference, component_attached_to, remarks
  - Add test_run_id foreign key to test_runs table
  - Add priority and status fields
  - Add execution tracking fields: executed_by, executed_at
  - Add indexes for test_run_id and status
  - Test migration up and down
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 9.2, 9.3_

- [x] 1.3 Extend bugs table with new columns migration
  - Add test_run_id and test_case_id foreign keys for bugs from test failures
  - Add hierarchy relationship columns (project_id through subtask_id) for direct bugs
  - Add category, severity, priority, status fields
  - Add assignment fields: reporter_id, assignee_id, qa_owner_id
  - Add reproduction path fields: reproduction_steps, expected_result, actual_result
  - Add linked items fields: linked_task_id, linked_commit, linked_pr
  - Add component_attached_to, environment, reopen_count, resolution_notes
  - Create indexes for all new columns
  - Test migration with existing bug data
  - _Requirements: 4.1-4.10, 5.1-5.11, 8.1-8.13, 9.5-9.18_

- [x] 1.4 Create bug_comments table migration
  - Write migration for bug_comments table
  - Add fields for comment_text, author_id, mentioned_users, attachments
  - Add edit tracking: is_edited, edited_at
  - Add indexes for bug_id and author_id
  - _Requirements: 6.1-6.13_

- [x] 1.5 Create bug_attachments table migration
  - Write migration for bug_attachments table
  - Add fields: file_name, file_path, file_type, file_size
  - Add uploaded_by and uploaded_at fields
  - Add indexes for bug_id
  - _Requirements: 9.14_

- [x] 1.6 Create bug_status_history table migration
  - Write migration for bug_status_history table for audit trail
  - Add fields: from_status, to_status, resolution_notes
  - Add changed_by and changed_at fields
  - Add indexes for bug_id and changed_at
  - Test all migrations together
  - _Requirements: 8.9, 8.13, 8.15_

- [x] 2. Backend API Models and Schemas
- [x] 2.1 Create TestRun SQLAlchemy model
  - Define TestRun model with all fields from design
  - Add relationships to hierarchy entities (Project, UseCase, UserStory, Task, Subtask)
  - Add validation for hierarchy constraint (only one can be set)
  - Add relationship to test_cases
  - Add soft delete support
  - _Requirements: 2.1-2.10_

- [x] 2.2 Create TestCase SQLAlchemy model
  - Define TestCase model with all fields from design
  - Add relationship to TestRun (many-to-one)
  - Add relationship to User for executed_by
  - Add soft delete support
  - _Requirements: 3.1-3.10_

- [x] 2.3 Extend Bug SQLAlchemy model
  - Add test_run_id and test_case_id relationships
  - Add hierarchy relationship fields
  - Add category, severity, priority, status fields
  - Add assignment relationships: reporter, assignee, qa_owner
  - Add reproduction path fields
  - Add linked items fields
  - Update existing relationships
  - _Requirements: 4.1-4.10, 5.1-5.11, 8.1-8.13_

- [x] 2.4 Create BugComment and BugAttachment models
  - Define BugComment model with relationships
  - Define BugAttachment model
  - Define BugStatusHistory model
  - Add relationships to Bug and User
  - _Requirements: 6.1-6.13, 9.14, 8.15_

- [x] 2.5 Create Pydantic schemas for test runs
  - Create TestRunBase, TestRunCreate, TestRunUpdate schemas
  - Create TestRunResponse schema with relationships
  - Add validation for run_type, status enums
  - Add validation for hierarchy constraint
  - Create TestRunList schema for pagination
  - _Requirements: 2.1-2.10_

- [x] 2.6 Create Pydantic schemas for test cases
  - Create TestCaseBase, TestCaseCreate, TestCaseUpdate schemas
  - Create TestCaseResponse schema with relationships
  - Add validation for priority, status enums
  - Create TestCaseList schema for pagination
  - _Requirements: 3.1-3.10_

- [x] 2.7 Extend Bug Pydantic schemas
  - Update BugCreate schema with test_run_id, test_case_id, hierarchy fields
  - Add category, severity, priority, status fields
  - Add assignment fields: reporter_id, assignee_id, qa_owner_id
  - Add reproduction path fields
  - Add linked items fields
  - Update BugResponse schema to include all new fields
  - Add BugStatusUpdate schema for status transitions
  - _Requirements: 4.1-4.10, 5.1-5.11, 8.1-8.13_

- [x] 2.8 Create Comment and Attachment Pydantic schemas
  - Create CommentCreate, CommentUpdate, CommentResponse schemas
  - Create AttachmentCreate, AttachmentResponse schemas
  - Add validation for mentions format
  - _Requirements: 6.1-6.13_

- [x] 3. Backend CRUD Operations
- [x] 3.1 Implement TestRun CRUD operations
  - Create CRUDTestRun class extending CRUDBase
  - Implement get_by_hierarchy method for filtering by hierarchy level
  - Implement get_with_descendants method for hierarchical queries
  - Add validation for hierarchy constraint
  - Add method to calculate test run metrics (passed, failed, blocked counts)
  - _Requirements: 2.1-2.10, 11.7_

- [x] 3.2 Implement TestCase CRUD operations
  - Create CRUDTestCase class extending CRUDBase
  - Implement get_by_test_run method
  - Implement update_execution method to record execution results
  - Add method to update test run metrics when test case status changes
  - _Requirements: 3.1-3.10, 11.1-11.10_

- [x] 3.3 Extend Bug CRUD operations
  - Update CRUDBug with hierarchy filtering methods
  - Implement get_by_hierarchy_with_descendants method
  - Implement get_by_test_run method
  - Add status transition validation
  - Add assignment tracking
  - Add method to create bug from test case with pre-population
  - _Requirements: 4.1-4.10, 5.1-5.11, 7.1-7.7, 8.1-8.13_

- [x] 3.4 Implement Comment and Attachment CRUD operations
  - Create CRUDComment class for bug comments
  - Implement get_by_bug method
  - Add edit time window validation (15 minutes)
  - Add mention extraction logic
  - Create CRUDAttachment class for bug attachments
  - _Requirements: 6.1-6.13_

- [x] 4. Backend API Endpoints - Test Runs
- [x] 4.1 Create test runs list endpoint
  - Implement GET /api/v1/test-runs/ with hierarchy filters
  - Add support for status, run_type filters
  - Implement pagination
  - Return test run list with metrics
  - _Requirements: 2.1, 2.5, 2.6, 2.7_

- [x] 4.2 Create test run CRUD endpoints
  - Implement GET /api/v1/test-runs/{id}
  - Implement POST /api/v1/test-runs/
  - Implement PUT /api/v1/test-runs/{id}
  - Implement DELETE /api/v1/test-runs/{id} (soft delete)
  - Add authorization checks
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 4.3 Create test run metrics endpoint
  - Implement GET /api/v1/test-runs/{id}/metrics
  - Return test case counts (total, passed, failed, blocked)
  - Calculate pass rate and completion percentage
  - _Requirements: 2.8, 11.6, 11.7, 13.10_

- [x] 5. Backend API Endpoints - Test Cases
- [x] 5.1 Create test cases list endpoint
  - Implement GET /api/v1/test-cases/ with test_run_id filter
  - Add support for status, priority filters
  - Implement pagination
  - Return test case list with execution info
  - _Requirements: 3.1, 3.10_

- [x] 5.2 Create test case CRUD endpoints
  - Implement GET /api/v1/test-cases/{id}
  - Implement POST /api/v1/test-cases/
  - Implement PUT /api/v1/test-cases/{id}
  - Implement DELETE /api/v1/test-cases/{id} (soft delete)
  - Add authorization checks
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 5.3 Create test case execution endpoint
  - Implement POST /api/v1/test-cases/{id}/execute
  - Update actual_result, inference, status
  - Record executed_by and executed_at
  - Update test run metrics
  - Return updated test case
  - _Requirements: 11.1, 11.2, 11.3, 11.5, 11.6, 11.9_

- [x] 5.4 Create bug from failed test case endpoint
  - Implement POST /api/v1/test-cases/{id}/create-bug
  - Pre-populate bug with test case details
  - Link bug to test case and test run
  - Copy test steps to reproduction steps
  - Copy expected/actual results
  - Return created bug
  - _Requirements: 4.1-4.10, 11.4_

- [-] 6. Backend API Endpoints - Enhanced Bugs
- [x] 6.1 Create hierarchical bug list endpoint
  - Implement GET /api/v1/bugs/hierarchy with hierarchy filters
  - Support include_descendants parameter
  - Add filters for status, category, severity, priority, assignee, reporter, qa_owner
  - Implement advanced search by title/reproduction steps
  - Return bugs with hierarchy path and test run/test case info
  - _Requirements: 7.1-7.7, 10.1-10.11_

- [x] 6.2 Enhance bug create endpoint
  - Update POST /api/v1/bugs/ to support hierarchy selection
  - Add category, severity, priority fields
  - Support assignment during creation (reporter, assignee, qa_owner)
  - Add reproduction path fields
  - Send notification to assignee and qa_owner
  - _Requirements: 5.1-5.11_

- [x] 6.3 Create bug status update endpoint
  - Implement POST /api/v1/bugs/{id}/status
  - Validate status transitions
  - Allow resolution_notes when status changes
  - Record status change in bug_status_history
  - Update closed_at timestamp for Verified/Closed
  - _Requirements: 8.1-8.4, 8.9_

- [x] 6.4 Create bug assignment endpoints
  - Implement POST /api/v1/bugs/{id}/assign
  - Support assigning reporter, assignee, qa_owner
  - Validate assignee exists and is active
  - Track assignment history
  - Send notification to new assignee/qa_owner
  - _Requirements: 5.6-5.11, 8.5_

- [x] 6.5 Create bug history endpoint
  - Implement GET /api/v1/bugs/{id}/history
  - Return status changes, assignments, field updates
  - Include system-generated notes
  - Order by timestamp descending
  - _Requirements: 8.9, 8.13, 6.13_

- [-] 7. Backend API Endpoints - Comments and Attachments
- [x] 7.1 Create comment endpoints for bugs
  - Implement GET /api/v1/bugs/{id}/comments
  - Implement POST /api/v1/bugs/{id}/comments
  - Implement PUT /api/v1/comments/{id}
  - Implement DELETE /api/v1/comments/{id}
  - Validate edit time window (15 minutes)
  - _Requirements: 6.1-6.7_

- [x] 7.2 Implement mention notification logic
  - Extract @mentions from comment text
  - Send notifications to mentioned users
  - Store mentioned_users in database
  - Notify assignee, reporter, qa_owner on new comment
  - _Requirements: 6.7, 6.8, 6.10_

- [x] 7.3 Create attachment endpoints
  - Implement POST /api/v1/bugs/{id}/attachments for file upload
  - Implement GET /api/v1/bugs/{id}/attachments
  - Implement DELETE /api/v1/attachments/{id}
  - Support screenshots, logs, videos
  - _Requirements: 6.12_

- [x] 8. Backend API Endpoints - Metrics
- [x] 8.1 Create bug summary metrics endpoint
  - Implement GET /api/v1/qa-metrics/bugs/summary
  - Calculate total, open, closed bugs
  - Calculate resolution rate and average resolution time
  - Return bug distribution by category/severity/priority
  - Support hierarchy filtering
  - _Requirements: 10.7, 13.1, 13.4, 13.5_

- [x] 8.2 Create bug trend analysis endpoint
  - Implement GET /api/v1/qa-metrics/bugs/trends
  - Calculate bug creation and resolution rates over time
  - Support date range filtering
  - Return data for line charts
  - _Requirements: 13.2, 13.9_

- [x] 8.3 Create bug aging report endpoint
  - Implement GET /api/v1/qa-metrics/bugs/aging
  - Group bugs by age ranges (0-7, 8-30, 31-90, 90+ days)
  - Calculate average age by severity
  - _Requirements: 13.3, 8.11_

- [x] 8.4 Create test run metrics endpoint
  - Implement GET /api/v1/qa-metrics/test-runs/summary
  - Calculate test run completion metrics
  - Return pass/fail trends over time
  - Support filtering by hierarchy
  - _Requirements: 13.9, 13.10, 13.11_

- [-] 9. Frontend - Navigation and Routing
- [x] 9.1 Add QA menu group to Sidebar
  - Update Sidebar.tsx to add QA group
  - Add "Test Runs", "Test Cases", and "Bug Lifecycle" menu items
  - Use appropriate icons (🧪 for QA, 🏃 for Test Runs, 📋 for Test Cases, 🐛 for Bug Lifecycle)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 9.2 Add routes for QA pages
  - Add /test-runs route in App.tsx
  - Add /test-cases route in App.tsx
  - Add /bug-lifecycle route in App.tsx
  - Ensure routes are protected (require authentication)
  - _Requirements: 1.1, 1.4_

- [-] 10. Frontend - Test Runs Page
- [x] 10.1 Create TestRunsPage component
  - Create basic page structure with header
  - Add hierarchical selector component (Project → Subtask)
  - Add "Create Test Run" button
  - Add test run list table with metrics
  - Add filters for status, run_type
  - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

- [x] 10.2 Create TestRunForm component
  - Create modal form for creating/editing test runs
  - Add fields: name, purpose, short_description, long_description
  - Add component_attached_to field
  - Add run_type dropdown (Misc, One-Timer)
  - Add hierarchy selector
  - _Requirements: 2.3, 2.4, 2.5_

- [x] 10.3 Implement test run list with API integration
  - Fetch test runs from API based on hierarchy selection
  - Display test runs in table with metrics
  - Show test case counts (total, passed, failed, blocked)
  - Add click handler to view test run details
  - _Requirements: 2.6, 2.8_

- [x] 10.4 Create TestRunDetails component
  - Display full test run information
  - Show test case list within the test run
  - Display test run progress (pass rate, completion %)
  - Add "Add Test Case" button
  - Show visual indicators (progress bars, pie charts)
  - _Requirements: 2.8, 11.7, 11.8_

- [x] 11. Frontend - Test Cases Page
- [x] 11.1 Create TestCasesPage component
  - Create page structure with test run selector
  - Display test cases for selected test run
  - Add "Create Test Case" button
  - Add filters for status, priority
  - _Requirements: 3.1, 3.10_

- [x] 11.2 Create TestCaseForm component
  - Create modal form for creating/editing test cases
  - Add fields: test_case_name, test_case_description
  - Add dynamic test_case_steps list (numbered)
  - Add expected_result field
  - Add component_attached_to field
  - Add priority dropdown (P0-P3)
  - Add remarks field
  - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 11.3 Implement test case list with API integration
  - Fetch test cases from API for selected test run
  - Display test cases in table with status
  - Show last execution info (executor, date)
  - Add click handler to view test case details
  - _Requirements: 3.1, 3.10_

- [x] 11.4 Create TestCaseDetails component
  - Display full test case information
  - Show test steps, expected result
  - Add "Execute Test" button
  - Show actual result and inference fields
  - Display execution history
  - _Requirements: 3.6, 3.9, 11.1, 11.10_

- [x] 12. Frontend - Test Execution
- [x] 12.1 Create TestExecutionModal component
  - Display test case details (steps, expected results)
  - Add actual_result text area
  - Add inference text area
  - Add status dropdown (Passed, Failed, Blocked, Skipped)
  - _Requirements: 11.1, 11.2, 11.3, 11.9_

- [x] 12.2 Implement test execution submission
  - Submit execution to API
  - Update test case status
  - Record executor and timestamp
  - Update test run metrics
  - Show success message
  - _Requirements: 11.2, 11.3, 11.5, 11.6_

- [x] 12.3 Implement create bug from failed test case
  - Show "Create Bug" option if test case marked as Failed
  - Pre-populate bug form with test case details
  - Link bug to test case and test run
  - Submit bug creation to API
  - Show success message with bug link
  - _Requirements: 4.1-4.10, 11.4_

- [x] 13. Frontend - Bug Lifecycle Page
- [x] 13.1 Create BugLifecyclePage component
  - Create page structure with hierarchical selector (Project → Subtask)
  - Add "View Bugs" button at each hierarchy level
  - Add "Create Bug" button
  - Add bug list table
  - Add advanced filters panel
  - _Requirements: 5.1, 7.1-7.7, 10.1-10.11_

- [x] 13.2 Implement hierarchical bug filtering
  - Fetch bugs based on selected hierarchy level
  - Support include_descendants option
  - Update bug list when hierarchy selection changes
  - Display hierarchy path for each bug
  - Show test run/test case info for bugs from test failures
  - _Requirements: 7.1-7.7, 10.4, 10.11_

- [x] 13.3 Create BugForm component (enhance existing)
  - Add hierarchy selector to bug form
  - Add category dropdown (UI, Backend, Database, etc.)
  - Add severity dropdown (Critical, High, Medium, Low)
  - Add priority dropdown (P1, P2, P3, P4)
  - Add reproduction_steps text area
  - Add expected_result and actual_result fields
  - Add assignee, qa_owner dropdowns
  - Add component_attached_to field
  - Add linked items fields (task, commit, PR)
  - _Requirements: 5.1-5.11_

- [x] 13.4 Create BugDetails component
  - Display full bug information with all fields
  - Show hierarchy path
  - Show test run and test case links if applicable
  - Add status update dropdown with validation
  - Add reassign buttons for assignee and qa_owner
  - Display reproduction path section
  - Display linked items section
  - Show comments section
  - Show attachments section
  - Show status history timeline
  - _Requirements: 8.1-8.13, 10.5, 10.11_

- [x] 13.5 Implement bug filters and search
  - Add filter controls for status, category, severity, priority
  - Add assignee, reporter, qa_owner filters
  - Add date range picker
  - Implement search by title/reproduction steps/ID
  - Add saved filters functionality
  - _Requirements: 8.10, 10.1-10.3, 10.6, 10.9_

- [x] 14. Frontend - Comments and Attachments
- [x] 14.1 Create CommentsSection component
  - Display comments in chronological order
  - Show comment author, timestamp, text
  - Show "edited" indicator for edited comments
  - Add "Add Comment" form
  - Support rich text formatting
  - _Requirements: 6.1-6.4, 6.6, 6.9_

- [x] 14.2 Implement comment actions
  - Add edit button for own comments (within 15 min)
  - Add delete button for own comments
  - Implement @mention autocomplete
  - Add file attachment upload
  - _Requirements: 6.5, 6.6, 6.7, 6.12_

- [x] 14.3 Display system-generated notes
  - Show status changes in timeline
  - Show assignment changes
  - Show field updates
  - Differentiate from user comments
  - _Requirements: 6.13_

- [x] 14.4 Create AttachmentsSection component
  - Display list of attachments (screenshots, logs, videos)
  - Add upload button
  - Show file name, type, size, uploader
  - Add download and delete actions
  - _Requirements: 6.12_

- [x] 15. Frontend - Bug Metrics Dashboard
- [x] 15.1 Create BugMetricsDashboard component
  - Create dashboard layout with metric cards
  - Add summary cards (total bugs, open, closed, resolution rate)
  - Add bug distribution pie charts (category, severity, priority)
  - Add bug trend line chart
  - Add bug aging bar chart
  - _Requirements: 10.7, 13.1-13.6_

- [x] 15.2 Implement metrics API integration
  - Fetch bug summary metrics from API
  - Fetch bug trends data
  - Fetch bug aging report
  - Update charts with real data
  - Add loading states
  - _Requirements: 13.1-13.6_

- [x] 15.3 Add test run metrics
  - Add test run completion metrics card
  - Add pass/fail rate pie chart
  - Add test run progress indicators
  - Add bugs grouped by test run view
  - _Requirements: 13.9, 13.10, 13.11_

- [x] 16. Dummy Data Generation
- [x] 16.1 Create Excel templates for QA data
  - Create test_runs.xlsx template with all fields
  - Create test_cases.xlsx template
  - Create bugs_extended.xlsx template with new fields
  - Add sample data rows with instructions
  - _Requirements: 14.10_

- [x] 16.2 Create QA dummy data generation script
  - Create create_qa_data.py in dummy_data_setup
  - Generate 20 test runs across hierarchy levels
  - Generate 50 test cases within test runs
  - Generate 60 bugs (40 from test cases, 20 direct)
  - Link bugs to test runs and test cases appropriately
  - _Requirements: 14.1-14.14_

- [x] 16.3 Generate realistic bug data
  - Generate bugs with various categories, severities, priorities
  - Assign reporters, assignees, qa_owners
  - Generate reproduction paths
  - Create bugs with varied ages (old and recent)
  - Set realistic test case statuses (Passed, Failed, Blocked)
  - _Requirements: 14.4, 14.5, 14.12, 14.13, 14.14_

- [x] 16.4 Generate comments and history data
  - Generate bug comments with @mentions
  - Generate bug status history for realistic lifecycle
  - Generate attachments for some bugs
  - Log creation progress and summary
  - _Requirements: 14.8, 14.9_

- [x] 16.5 Integrate with real API endpoints
  - Use API endpoints for all data creation
  - Handle authentication for API calls
  - Validate responses and handle errors
  - _Requirements: 14.9_

- [ ] 17. Integration and Testing
- [ ]* 17.1 Test test run and test case workflow
  - Create test run via UI
  - Add test cases to test run
  - Execute test cases and record results
  - Verify test run metrics update correctly

- [ ]* 17.2 Test bug creation from test case
  - Mark test case as Failed
  - Create bug from failed test case
  - Verify bug is linked to test case and test run
  - Verify pre-populated fields are correct

- [ ]* 17.3 Test direct bug creation
  - Create bug via UI with hierarchy selection
  - Assign reporter, assignee, qa_owner
  - Add reproduction path
  - Verify bug is created correctly

- [ ]* 17.4 Test bug lifecycle workflow
  - Update bug status through workflow
  - Add comments with @mentions
  - Upload attachments
  - Verify status history is recorded

- [ ]* 17.5 Test hierarchical bug viewing
  - Select different hierarchy levels
  - Verify "View Bugs" shows correct bugs
  - Test include_descendants functionality
  - Verify hierarchy path display

- [ ]* 17.6 Test metrics and reporting
  - Verify bug summary metrics are accurate
  - Test bug trend charts with date ranges
  - Verify aging report calculations
  - Test test run metrics

- [ ] 18. Documentation and Deployment
- [ ]* 18.1 Update API documentation
  - Document all new endpoints
  - Add request/response examples
  - Document enum values and validation rules
  - Update Postman collection

- [ ]* 18.2 Create user guide
  - Document test run management workflow
  - Document test case creation and execution
  - Document bug lifecycle workflow
  - Document metrics dashboard usage
  - Add screenshots and examples

- [ ] 18.3 Deploy to development environment
  - Run database migrations
  - Deploy backend API changes
  - Deploy frontend changes
  - Run dummy data generation script
  - Verify all features work end-to-end

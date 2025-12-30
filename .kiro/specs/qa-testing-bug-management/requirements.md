# Requirements Document

## Introduction

This document specifies the requirements for a comprehensive QA Testing and Bug Management system within the Worky project management platform. The system introduces a new "QA" menu group with a Test Run-centric approach. Test Runs can be attached to any hierarchy level (Project, Use Case, User Story, Task, or Subtask) and contain Test Cases. Bugs can be created from failed Test Cases or directly at any hierarchy level. The system provides hierarchical bug viewing and comprehensive bug lifecycle management following industry standards.

## Glossary

- **QA System**: The Quality Assurance module within Worky that manages test runs, test cases, and bug lifecycle
- **Test Run**: A container for test cases that can be attached to any hierarchy level; used to group related testing activities and bugs
- **Test Case**: A specific test within a Test Run containing steps, expected results, and actual results
- **Bug**: A defect or error in the system that causes it to produce incorrect or unexpected results
- **Hierarchy Level**: A level in the project structure (Project → Use Case → User Story → Task → Subtask)
- **Bug Lifecycle**: The complete workflow of a bug from creation through resolution and closure
- **Test Run Type**: Classification of test run as "Misc" (miscellaneous) or "One-Timer" (single execution)
- **Bug Category**: Classification of bug type (UI, Backend, Database, Integration, Performance, Security, Environment)
- **Bug Severity**: Impact level of the bug (Critical, High, Medium, Low)
- **Bug Priority**: Urgency of fixing the bug (P1, P2, P3, P4)
- **Hierarchical Bug View**: The ability to view all bugs associated with a selected hierarchy level and all its descendants

## Requirements

### Requirement 1: QA Menu Group

**User Story:** As a project manager, I want a dedicated QA section in the navigation menu, so that I can easily access quality assurance and testing features.

#### Acceptance Criteria

1. WHEN THE User views the navigation sidebar, THE QA System SHALL display a "QA" menu group with an appropriate icon
2. THE QA System SHALL position the QA menu group between the "Tracking" and "Administration" groups
3. WHEN THE User clicks on the QA menu group header, THE QA System SHALL expand or collapse the group to show or hide its sub-items
4. THE QA System SHALL include "Test Runs", "Test Cases", and "Bug Lifecycle" as sub-items within the QA menu group
5. THE QA System SHALL maintain the expanded/collapsed state of the QA menu group during the user session

### Requirement 2: Test Run Management

**User Story:** As a QA engineer, I want to create and manage test runs at different hierarchy levels, so that I can organize testing activities according to project structure and group related test cases.

#### Acceptance Criteria

1. WHEN THE User navigates to the Test Runs page, THE QA System SHALL display a hierarchical selector showing Project through Subtask levels
2. THE QA System SHALL allow test run creation at Project, Use Case, User Story, Task, and Subtask hierarchy levels
3. WHEN THE User creates a test run, THE QA System SHALL require name, purpose, short description, and component attached to
4. THE QA System SHALL support test run types "Misc" and "One-Timer"
5. THE QA System SHALL associate each test run with exactly one hierarchy entity (Project, Use Case, User Story, Task, or Subtask)
6. WHEN THE User views test runs, THE QA System SHALL display all test runs associated with the selected hierarchy level and its descendants
7. THE QA System SHALL support test run statuses "In Progress", "Completed", and "Aborted"
8. THE QA System SHALL display test run metrics including total test cases, passed, failed, and blocked counts
9. THE QA System SHALL allow users to add a long description to provide detailed context for the test run
10. THE QA System SHALL track start date and end date for each test run

### Requirement 3: Test Case Management

**User Story:** As a QA engineer, I want to create and manage test cases within test runs, so that I can document specific test scenarios with detailed steps and expected results.

#### Acceptance Criteria

1. WHEN THE User views a test run, THE QA System SHALL display all test cases belonging to that test run
2. THE QA System SHALL allow test case creation only within an existing test run
3. WHEN THE User creates a test case, THE QA System SHALL require test case name, description, test steps, and expected result
4. THE QA System SHALL support numbered test steps stored as a structured list
5. THE QA System SHALL allow users to specify component attached to for each test case (e.g., "Login Screen", "Payment API")
6. THE QA System SHALL provide fields for actual result and inference to be filled during test execution
7. THE QA System SHALL allow users to add remarks for additional notes or observations
8. THE QA System SHALL support test case priority levels "P0", "P1", "P2", and "P3"
9. THE QA System SHALL support test case statuses "Not Executed", "Passed", "Failed", "Blocked", and "Skipped"
10. THE QA System SHALL track who executed the test case and when it was executed

### Requirement 4: Bug Creation from Test Cases

**User Story:** As a QA engineer, I want to create bugs directly from failed test cases, so that I can quickly report issues discovered during testing with full context.

#### Acceptance Criteria

1. WHEN THE User marks a test case as "Failed", THE QA System SHALL display a "Create Bug" button
2. WHEN THE User clicks "Create Bug" from a failed test case, THE QA System SHALL pre-populate the bug form with test case details
3. THE QA System SHALL automatically link the created bug to both the test case and the test run
4. THE QA System SHALL copy the test case name to the bug title
5. THE QA System SHALL copy the test steps to the bug reproduction steps
6. THE QA System SHALL copy the expected result and actual result to the bug's corresponding fields
7. THE QA System SHALL inherit the component attached to from the test case
8. THE QA System SHALL set the bug reporter to the current user
9. THE QA System SHALL allow the user to modify all pre-populated fields before creating the bug
10. THE QA System SHALL group bugs by test run ID for tracking purposes

### Requirement 5: Direct Bug Creation and Assignment

**User Story:** As a team member, I want to create bugs directly without a test case and assign them to users, so that I can report issues discovered outside of formal testing and ensure accountability.

#### Acceptance Criteria

1. WHEN THE User navigates to the Bug Lifecycle page, THE QA System SHALL display a "Create Bug" button
2. THE QA System SHALL allow bug creation without requiring an associated test case or test run
3. WHEN THE User creates a bug directly, THE QA System SHALL require selection of a hierarchy level (Project through Subtask)
4. THE QA System SHALL require title, category, severity, priority, and reproduction steps for direct bug creation
5. THE QA System SHALL associate the bug with the selected hierarchy entity
6. THE QA System SHALL allow the user to assign the bug to a developer (assignee) during creation
7. THE QA System SHALL allow the user to assign a QA owner during creation
8. THE QA System SHALL automatically set the reporter to the current user
9. WHEN THE User assigns a bug, THE QA System SHALL send a notification to the assignee and QA owner
10. THE QA System SHALL allow reassignment of bugs to different users at any time
11. THE QA System SHALL track assignment history showing who assigned the bug to whom and when

### Requirement 6: Notes and Comments on Bugs

**User Story:** As a team member, I want to add notes and comments on bugs, so that I can track the history of what happened and collaborate with the team.

#### Acceptance Criteria

1. THE QA System SHALL allow users to add comments to any bug at any time
2. WHEN THE User adds a comment, THE QA System SHALL record the comment text, author, and timestamp
3. THE QA System SHALL display comments in chronological order (oldest to newest or newest to oldest based on user preference)
4. THE QA System SHALL allow users to edit their own comments within 15 minutes of posting
5. THE QA System SHALL allow users to delete their own comments
6. THE QA System SHALL mark edited comments with an "edited" indicator and timestamp
7. THE QA System SHALL support @mentions in comments to notify specific users
8. THE QA System SHALL support rich text formatting in comments (bold, italic, code blocks, links)
9. THE QA System SHALL display a comment count badge on bugs
10. WHEN THE User adds a comment to a bug, THE QA System SHALL notify the bug assignee, reporter, and QA owner
11. THE QA System SHALL allow filtering the activity history to show only comments or only status changes
12. THE QA System SHALL support attaching files or images to comments
13. THE QA System SHALL display system-generated notes for automated actions (status changes, assignments, field updates)

### Requirement 7: Hierarchical Bug Viewing

**User Story:** As a project manager, I want to view bugs at any hierarchy level, so that I can see all bugs affecting a specific part of the project.

#### Acceptance Criteria

1. WHEN THE User navigates to the Bug Lifecycle page, THE QA System SHALL display a hierarchical selector from Client to Subtask
2. THE QA System SHALL allow the user to select any hierarchy level without requiring selection of all parent levels
3. WHEN THE User selects a hierarchy level and clicks "View Bugs", THE QA System SHALL display all bugs associated with that level and all descendant levels
4. IF THE User selects a Project, THEN THE QA System SHALL display bugs associated with the Project, all its Use Cases, User Stories, Tasks, and Subtasks
5. IF THE User selects a Use Case, THEN THE QA System SHALL display bugs associated with the Use Case, all its User Stories, Tasks, and Subtasks
6. THE QA System SHALL display the "View Bugs" button at every hierarchy selection level
7. THE QA System SHALL update the bug list immediately when the user changes the hierarchy selection

### Requirement 8: Bug Lifecycle Management

**User Story:** As a development team member, I want to track bugs through their complete lifecycle following industry standards, so that I can manage bug resolution effectively.

#### Acceptance Criteria

1. THE QA System SHALL support bug statuses following standard workflow: "New", "Open", "In Progress", "Fixed", "In Review", "Ready for QA", "Verified", "Closed", and "Reopened"
2. THE QA System SHALL enforce valid status transitions (e.g., "New" → "Open" → "In Progress" → "Fixed" → "In Review" → "Ready for QA" → "Verified" → "Closed")
3. WHEN THE User updates a bug status to "Fixed", THE QA System SHALL allow adding resolution notes
4. WHEN THE User updates a bug status to "Verified" or "Closed", THE QA System SHALL record the closure timestamp
5. THE QA System SHALL allow assignment of bugs to team members with role validation
6. THE QA System SHALL track bug category as "UI", "Backend", "Database", "Integration", "Performance", "Security", or "Environment"
7. THE QA System SHALL track bug severity levels as "Critical", "High", "Medium", or "Low"
8. THE QA System SHALL track bug priority levels as "P1", "P2", "P3", or "P4"
9. THE QA System SHALL maintain audit history for all bug status changes, assignments, and field updates
10. THE QA System SHALL support filtering bugs by status, category, severity, priority, assignee, reporter, and date ranges
11. THE QA System SHALL track bug age (days since creation) and resolution time
12. WHEN THE User reopens a closed bug, THE QA System SHALL increment a reopen counter and log the reason
13. THE QA System SHALL support bug comments/notes with timestamps and user attribution

### Requirement 9: Bug Data Model

**User Story:** As a system administrator, I want bugs to follow industry-standard data models with proper hierarchy linkage, so that bug tracking integrates seamlessly with project structure.

#### Acceptance Criteria

1. THE QA System SHALL create a test_runs table with fields: name, purpose, short_description, long_description, component_attached_to, run_type, status, start_date, end_date
2. THE QA System SHALL create a test_cases table with fields: test_case_name, test_case_description, test_case_steps, expected_result, actual_result, inference, component_attached_to, remarks, priority, status
3. THE QA System SHALL link test_cases to test_runs via test_run_id foreign key
4. THE QA System SHALL link test_runs to hierarchy entities (project_id, usecase_id, user_story_id, task_id, subtask_id) with constraint ensuring only one is set
5. THE QA System SHALL extend the bugs table with test_run_id and test_case_id foreign keys for bugs created from test cases
6. THE QA System SHALL extend the bugs table with hierarchy foreign keys (project_id, usecase_id, user_story_id, task_id, subtask_id) for bugs created directly
7. THE QA System SHALL store bug category ("UI", "Backend", "Database", "Integration", "Performance", "Security", "Environment")
8. THE QA System SHALL store bug severity ("Critical", "High", "Medium", "Low") and priority ("P1", "P2", "P3", "P4")
9. THE QA System SHALL store bug status ("New", "Open", "In Progress", "Fixed", "In Review", "Ready for QA", "Verified", "Closed", "Reopened")
10. THE QA System SHALL store bug assignments (reporter_id, assignee_id, qa_owner_id) as foreign keys to users table
11. THE QA System SHALL store reproduction path fields (reproduction_steps, expected_result, actual_result)
12. THE QA System SHALL store linked items (linked_task_id, linked_commit, linked_pr)
13. THE QA System SHALL create a bug_comments table for threaded discussions on bugs
14. THE QA System SHALL create a bug_attachments table for screenshots, logs, and videos
15. THE QA System SHALL create a bug_status_history table for audit trail
16. THE QA System SHALL enforce referential integrity between all entities
17. THE QA System SHALL support soft deletion using an is_deleted flag
18. THE QA System SHALL track created_by, updated_by, created_at, and updated_at timestamps for all records

### Requirement 10: Bug Display and Filtering

**User Story:** As a QA engineer, I want to view and filter bugs effectively with industry-standard metrics, so that I can focus on relevant issues and track team performance.

#### Acceptance Criteria

1. WHEN THE User views the bug list, THE QA System SHALL display bug ID, title, status, category, severity, priority, assignee, reporter, QA owner, age (days), and creation date
2. THE QA System SHALL provide filter controls for status, category, severity, priority, assignee, reporter, QA owner, and date ranges
3. THE QA System SHALL provide advanced search functionality to find bugs by title, reproduction steps, or bug ID
4. THE QA System SHALL display the hierarchy path for each bug (e.g., "Project > Use Case > User Story")
5. WHEN THE User clicks on a bug, THE QA System SHALL display full bug details including all fields, reproduction path, linked items, comments, attachments, and audit history
6. THE QA System SHALL support sorting bugs by creation date, priority, severity, status, and age
7. THE QA System SHALL display bug metrics dashboard showing: total bugs, open bugs, closed bugs, bug resolution rate, average resolution time, and bugs by category/severity/priority distribution
8. THE QA System SHALL display a count of bugs by status for the selected hierarchy level with visual indicators (charts/graphs)
9. THE QA System SHALL support saved filters and custom views for frequently used bug queries
10. THE QA System SHALL provide bulk operations for updating multiple bugs (assign, change status, change priority)
11. THE QA System SHALL display linked test run and test case information for bugs created from test failures

### Requirement 11: Test Case Execution

**User Story:** As a QA engineer, I want to execute test cases and record results, so that I can track testing progress and identify failures that need bug reports.

#### Acceptance Criteria

1. WHEN THE User views a test case, THE QA System SHALL display an "Execute Test" button
2. WHEN THE User executes a test case, THE QA System SHALL allow recording of actual result and inference
3. THE QA System SHALL allow the user to mark the test case status as "Passed", "Failed", "Blocked", or "Skipped"
4. WHEN THE User marks a test case as "Failed", THE QA System SHALL prompt to create a bug with pre-populated test case details
5. THE QA System SHALL record the executor (executed_by) and execution timestamp (executed_at) for each test case
6. THE QA System SHALL update the test run metrics (passed, failed, blocked counts) when test case status changes
7. THE QA System SHALL calculate and display test run progress: pass rate, fail rate, and completion percentage
8. THE QA System SHALL display test execution progress for test runs with visual indicators (progress bars, pie charts)
9. THE QA System SHALL allow users to update actual result and inference fields during or after execution
10. THE QA System SHALL display the last execution date and executor for each test case

### Requirement 12: Integration with Existing Bug System

**User Story:** As a system administrator, I want the new QA system to integrate with existing bug data, so that we maintain continuity with current bug tracking.

#### Acceptance Criteria

1. THE QA System SHALL extend the existing bugs table with new hierarchy relationship columns
2. THE QA System SHALL migrate existing bug data to the new schema without data loss
3. THE QA System SHALL maintain backward compatibility with existing bug API endpoints
4. THE QA System SHALL preserve existing bug relationships with users (assignee, reporter)
5. THE QA System SHALL retain all existing bug fields (title, description, severity, priority, status, etc.)

### Requirement 13: Bug Reporting and Metrics

**User Story:** As a QA manager, I want comprehensive bug reports and metrics following industry standards, so that I can track quality trends and make data-driven decisions.

#### Acceptance Criteria

1. THE QA System SHALL provide a Bug Metrics Dashboard displaying key performance indicators (KPIs)
2. THE QA System SHALL display bug trend analysis showing bug creation and resolution rates over time
3. THE QA System SHALL provide bug aging reports showing bugs grouped by age ranges (0-7 days, 8-30 days, 31-90 days, 90+ days)
4. THE QA System SHALL display bug distribution by category, severity, priority, status, and assignee
5. THE QA System SHALL calculate mean time to resolution (MTTR) for bugs by severity level
6. THE QA System SHALL display bug reopen rate and identify frequently reopened bugs
7. THE QA System SHALL support exporting bug reports to PDF, Excel, and CSV formats
8. THE QA System SHALL provide customizable bug reports with date range filters and grouping options
9. THE QA System SHALL display test run completion metrics and pass/fail trends over time
10. THE QA System SHALL provide test run summary showing total test cases, passed, failed, and blocked counts
11. THE QA System SHALL display bugs grouped by test run for test run-based analysis

### Requirement 14: Dummy Data Generation for Development

**User Story:** As a developer, I want realistic test data for test runs, test cases, and bugs following industry patterns, so that I can develop and test the QA features effectively.

#### Acceptance Criteria

1. THE QA System SHALL provide a dummy data generation script in the dummy_data_setup directory
2. THE QA System SHALL generate test runs associated with Projects, Use Cases, User Stories, Tasks, and Subtasks with realistic types (Misc, One-Timer)
3. THE QA System SHALL generate test cases within test runs with realistic test steps, expected results, and priorities
4. THE QA System SHALL generate bugs with various statuses, categories, severities, and priorities following realistic distribution patterns
5. THE QA System SHALL associate generated bugs with different hierarchy levels (Project through Subtask)
6. THE QA System SHALL link some bugs to test runs and test cases to demonstrate the test-to-bug workflow
7. THE QA System SHALL generate bugs created directly (not from test cases) at various hierarchy levels
8. THE QA System SHALL generate bug comments and status change history to simulate realistic bug lifecycle
9. THE QA System SHALL use the real API endpoints for data creation to ensure API compatibility
10. THE QA System SHALL generate Excel templates for test runs, test cases, and bugs in the excel_templates directory
11. WHEN THE Developer runs the dummy data script, THE QA System SHALL create at least 20 test runs, 50 test cases, and 60 bugs across different hierarchy levels
12. THE QA System SHALL assign bugs to reporters, assignees, and QA owners from existing users with realistic workload distribution
13. THE QA System SHALL generate bugs with realistic age distribution (some old, some recent) to test aging and metrics features
14. THE QA System SHALL set realistic test case statuses (Passed, Failed, Blocked, Not Executed) to demonstrate test run progress

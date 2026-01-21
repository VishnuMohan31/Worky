# QA Testing Guide - Worky Application

**Version:** 1.0  
**Date:** January 2026  
**Purpose:** Production Readiness Testing

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Hierarchy Section Testing](#hierarchy-section-testing)
3. [Administration Section Testing](#administration-section-testing)
4. [Management Section Testing](#management-section-testing)
5. [Sprint Functionality Testing](#sprint-functionality-testing)

---

## Test Environment Setup

### Prerequisites
- Docker Desktop installed and running
- Node.js and npm installed
- Access to test credentials

### Starting the Application

**Step 1: Start Database and API (Docker)**
```bash
docker-compose up -d
```

**Step 2: Start UI Server**
```bash
cd ui
npm run dev
```

**Step 3: Access Application**
- Open browser: http://localhost:3007/
- Login with test credentials

### Test User Roles
- **Admin**: Full access to all features
- **Product Owner**: Project and sprint management
- **Developer**: Task execution and updates
- **QA Tester**: Testing and bug reporting

---

## Hierarchy Section Testing

### Overview
The Hierarchy section manages the complete project structure from Clients down to Subtasks.

**Hierarchy Levels:**
```
Client → Program → Project → Use Case → User Story → Task → Subtask
```

---

### Test Case 1: Client Management

#### TC-H-001: Create New Client (Admin Only)
**Prerequisites:** Login as Admin user

**Steps:**
1. Navigate to "Clients" page from sidebar
2. Click "Add Client" button (top-right)
3. Fill in the form:
   - Name: "Test Client ABC"
   - Short Description: "Test client for QA"
   - Long Description: "Detailed description for testing"
   - Email: "testclient@example.com"
   - Phone: "+1234567890"
   - Status: Active (checked)
4. Click "Create Client"

**Expected Results:**
- ✅ Success message appears
- ✅ New client appears in the list
- ✅ Client statistics update correctly
- ✅ Client ID is auto-generated (CLI-XXX format)

**Negative Test:**
- Try creating client as non-admin user → Should show "Admin access required" message

---

#### TC-H-002: View Client Details
**Steps:**
1. From Clients page, click on any client card
2. Review the detail view panel

**Expected Results:**
- ✅ Client information displayed correctly
- ✅ Project statistics shown (total, ongoing, completed)
- ✅ Latest project information visible
- ✅ Contact information displayed
- ✅ Created/Updated dates shown in DD/MM/YYYY format

---

#### TC-H-003: Edit Client
**Steps:**
1. Click on a client to open details
2. Click "Edit" button
3. Modify any field (e.g., change description)
4. Click "Save Changes"

**Expected Results:**
- ✅ Changes saved successfully
- ✅ Updated information reflected immediately
- ✅ Updated date changes to current date

---

#### TC-H-004: Delete Client
**Steps:**
1. Click on a client to open details
2. Click "Delete" button
3. Confirm deletion in popup

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Client removed from list after confirmation
- ✅ Cannot delete client with active projects (should show error)

---

### Test Case 2: Program Management

#### TC-H-005: Create Program
**Prerequisites:** At least one client exists

**Steps:**
1. Navigate to "Programs" page
2. Click "Add Program" button
3. Fill in the form:
   - Client: Select from dropdown
   - Name: "Test Program 2026"
   - Description: "QA Testing Program"
   - Start Date: 01/01/2026 (DD/MM/YYYY)
   - End Date: 31/12/2026 (DD/MM/YYYY)
   - Status: "Active"
4. Click "Create"

**Expected Results:**
- ✅ Program created successfully
- ✅ Program ID auto-generated (PRG-XXX format)
- ✅ Dates displayed in DD/MM/YYYY format
- ✅ Program appears in the list

**Date Validation Test:**
- Try setting End Date before Start Date → Should show error "End date must be after start date"

---

#### TC-H-006: View Program Details
**Steps:**
1. Click on any program card
2. Review program detail page

**Expected Results:**
- ✅ Program information displayed
- ✅ Associated projects listed
- ✅ Team members shown
- ✅ Progress statistics visible
- ✅ All dates in DD/MM/YYYY format

---

### Test Case 3: Project Management

#### TC-H-007: Create Project
**Prerequisites:** At least one program exists

**Steps:**
1. Navigate to "Projects" page
2. Click "Add Project" button
3. Fill in the form:
   - Program: Select from dropdown
   - Name: "Test Project Alpha"
   - Description: "QA Testing Project"
   - Start Date: 15/01/2026
   - End Date: 15/06/2026
   - Status: "Planning"
4. Click "Create"

**Expected Results:**
- ✅ Project created successfully
- ✅ Project ID auto-generated (PRJ-XXX format)
- ✅ Dates in DD/MM/YYYY format
- ✅ Project appears in list

**Date Validation:**
- End date before start date → Error message
- Invalid date format → Auto-corrects or shows error

---

#### TC-H-008: Assign Team to Project
**Steps:**
1. Open project details
2. Scroll to "Team Assignment" section
3. Click "Assign Team" button
4. Select team from dropdown
5. Click "Assign"

**Expected Results:**
- ✅ Team assigned successfully
- ✅ Team members displayed in project
- ✅ Cannot remove individual members (only change team)

---

### Test Case 4: Use Case Management

#### TC-H-009: Create Use Case
**Prerequisites:** At least one project exists

**Steps:**
1. Navigate to "Use Cases" page
2. Click "Add Use Case" button
3. Fill in the form:
   - Project: Select from dropdown
   - Name: "User Login Use Case"
   - Description: "Test user authentication flow"
   - Priority: "High"
4. Click "Create"

**Expected Results:**
- ✅ Use case created successfully
- ✅ Use case ID auto-generated (UC-XXX format)
- ✅ Use case appears in list

---

### Test Case 5: User Story Management

#### TC-H-010: Create User Story
**Prerequisites:** At least one use case exists

**Steps:**
1. Navigate to "User Stories" page
2. Click "Add User Story" button
3. Fill in the form:
   - Use Case: Select from dropdown
   - Title: "As a user, I want to login"
   - Description: "User authentication story"
   - Story Points: 5
   - Priority: "High"
   - Phase: Select from dropdown
4. Click "Create"

**Expected Results:**
- ✅ User story created successfully
- ✅ Story ID auto-generated (US-XXX format)
- ✅ Story appears in list

---

### Test Case 6: Task Management

#### TC-H-011: Create Task
**Prerequisites:** At least one user story exists

**Steps:**
1. Navigate to "Tasks" page
2. Click "Add Task" button
3. Fill in the form:
   - User Story: Select from dropdown
   - Title: "Implement login API"
   - Description: "Create authentication endpoint"
   - Assigned To: Select user
   - Due Date: 30/01/2026
   - Status: "To Do"
   - Priority: "High"
4. Click "Create"

**Expected Results:**
- ✅ Task created successfully
- ✅ Task ID auto-generated (TSK-XXX format)
- ✅ Due date in DD/MM/YYYY format
- ✅ Task appears in list

---

### Test Case 7: Subtask Management

#### TC-H-012: Create Subtask
**Prerequisites:** At least one task exists

**Steps:**
1. Navigate to "Subtasks" page
2. Select hierarchy: Client → Program → Project → Use Case → User Story → Task
3. Click "Add Subtask" button
4. Fill in the form:
   - Title: "Write unit tests"
   - Description: "Create test cases for login API"
   - Assigned To: Select user
   - Due Date: 28/01/2026
   - Status: "To Do"
   - Duration (Days): 2
   - Scrum Points: 3
5. Click "Create"

**Expected Results:**
- ✅ Subtask created successfully
- ✅ Subtask ID auto-generated (SUB-XXX format)
- ✅ Subtask appears in the list
- ✅ Due date in DD/MM/YYYY format

---

#### TC-H-013: View Complete Hierarchy
**Steps:**
1. Navigate to "Subtasks" page
2. Use hierarchy dropdowns to navigate:
   - Select Client
   - Select Program (filtered by client)
   - Select Project (filtered by program)
   - Select Use Case (filtered by project)
   - Select User Story (filtered by use case)
   - Select Task (filtered by user story)
3. View subtasks for selected task

**Expected Results:**
- ✅ Each dropdown filters correctly based on parent selection
- ✅ Only relevant items shown in each dropdown
- ✅ Subtasks displayed for selected task
- ✅ No authentication errors
- ✅ All data loads correctly

---

### Test Case 8: Hierarchy Navigation

#### TC-H-014: Navigate Through Hierarchy
**Steps:**
1. Start from Clients page
2. Click on a client → Opens client details
3. Click on a program → Opens program details
4. Click on a project → Opens project details
5. Navigate back using breadcrumbs or back button

**Expected Results:**
- ✅ Each level opens correctly
- ✅ Data displayed accurately
- ✅ Navigation is smooth
- ✅ Breadcrumbs work correctly

---

## Administration Section Testing

### Overview
Administration section is accessible only to Admin users and includes system-wide settings.

---

### Test Case 9: Phase Management

#### TC-A-001: View Phases
**Prerequisites:** Login as Admin

**Steps:**
1. Navigate to "Admin" → "Phases" from sidebar
2. Review the phases list

**Expected Results:**
- ✅ All phases displayed
- ✅ Phase order shown correctly
- ✅ Default phases visible (Planning, Development, Testing, etc.)

---

#### TC-A-002: Create New Phase
**Steps:**
1. On Phases page, click "Add Phase" button
2. Fill in the form:
   - Name: "Code Review"
   - Description: "Code review and quality check phase"
   - Order: 5
   - Color: Select a color
3. Click "Create"

**Expected Results:**
- ✅ Phase created successfully
- ✅ Phase appears in list at correct order position
- ✅ Color displayed correctly

---

#### TC-A-003: Edit Phase
**Steps:**
1. Click "Edit" on any phase
2. Modify name or description
3. Click "Save"

**Expected Results:**
- ✅ Changes saved successfully
- ✅ Updated information displayed

---

#### TC-A-004: Delete Phase
**Steps:**
1. Click "Delete" on a phase
2. Confirm deletion

**Expected Results:**
- ✅ Phase deleted if not in use
- ✅ Error message if phase is assigned to tasks/subtasks
- ✅ Cannot delete default system phases

---

### Test Case 10: User Management

#### TC-A-005: View Users
**Prerequisites:** Login as Admin

**Steps:**
1. Navigate to "Users" page
2. Review users list

**Expected Results:**
- ✅ All users displayed
- ✅ User roles shown correctly
- ✅ Active/Inactive status visible
- ✅ Email addresses displayed

---

#### TC-A-006: Create New User
**Steps:**
1. Click "Add User" button
2. Fill in the form:
   - Full Name: "Test User QA"
   - Email: "testuser@example.com"
   - Role: Select from dropdown (Admin/Product Owner/Developer/QA Tester)
   - Status: Active
3. Click "Create"

**Expected Results:**
- ✅ User created successfully
- ✅ Default password assigned (password123)
- ✅ User appears in list
- ✅ User ID auto-generated

---

#### TC-A-007: Edit User
**Steps:**
1. Click "Edit" on any user
2. Modify role or status
3. Click "Save"

**Expected Results:**
- ✅ Changes saved successfully
- ✅ User information updated

---

#### TC-A-008: Deactivate User
**Steps:**
1. Edit a user
2. Uncheck "Active" status
3. Save changes

**Expected Results:**
- ✅ User marked as inactive
- ✅ User cannot login
- ✅ User still visible in system for historical data

---

### Test Case 11: Organization Management

#### TC-A-009: View Organizations
**Prerequisites:** Login as Admin

**Steps:**
1. Navigate to "Organizations" page
2. Review organizations list

**Expected Results:**
- ✅ All organizations displayed
- ✅ Organization logos shown
- ✅ Active/Inactive status visible

---

#### TC-A-010: Create Organization
**Steps:**
1. Click "Add Organization" button
2. Fill in the form:
   - Name: "Test Organization"
   - Description: "QA Testing Org"
   - Website: "https://testorg.com"
   - Email: "contact@testorg.com"
   - Phone: "+1234567890"
   - Address: "123 Test Street"
   - Upload Logo (optional)
3. Click "Create"

**Expected Results:**
- ✅ Organization created successfully
- ✅ Logo uploaded and displayed (if provided)
- ✅ Organization appears in list

---

#### TC-A-011: Edit Organization
**Steps:**
1. Click "Edit" on an organization
2. Modify any field
3. Upload new logo (optional)
4. Click "Save"

**Expected Results:**
- ✅ Changes saved successfully
- ✅ New logo displayed if uploaded
- ✅ Information updated

---

#### TC-A-012: Access Control Test
**Prerequisites:** Login as non-admin user (Developer/QA Tester)

**Steps:**
1. Try to access "Phases" page
2. Try to access "Organizations" page
3. Try to create a user

**Expected Results:**
- ✅ Access denied message shown
- ✅ "Admin access required" notification
- ✅ User redirected or blocked from admin functions

---

## Management Section Testing

### Overview
Management section includes team management, assignments, and operational features.

---

### Test Case 12: Team Management

#### TC-M-001: View Teams
**Steps:**
1. Navigate to "Teams" page
2. Review teams list

**Expected Results:**
- ✅ All teams displayed
- ✅ Team member count shown
- ✅ Associated project visible
- ✅ Active/Inactive status shown

---

#### TC-M-002: Create Team
**Steps:**
1. Click "Create Team" button
2. Fill in the form:
   - Team Name: "QA Testing Team"
   - Description: "Team for QA activities"
   - Project: Select from dropdown
3. Click "Create"

**Expected Results:**
- ✅ Team created successfully
- ✅ Team ID auto-generated
- ✅ Team appears in list

---

#### TC-M-003: Add Team Members
**Steps:**
1. Select a team from the list
2. Click "Add Member" button
3. Select user from dropdown
4. Select role (Team Lead/Developer/QA Tester)
5. Click "Add"

**Expected Results:**
- ✅ Member added successfully
- ✅ Member appears in team members list
- ✅ Member count updates
- ✅ Cannot add same user twice to same team

---

#### TC-M-004: Remove Team Member
**Steps:**
1. Select a team
2. Click "Remove" on a team member
3. Confirm removal

**Expected Results:**
- ✅ Member removed successfully
- ✅ Member count updates
- ✅ Member can be added back later

---

#### TC-M-005: Edit Team
**Steps:**
1. Click "Edit" on a team
2. Modify name or description
3. Click "Save"

**Expected Results:**
- ✅ Changes saved successfully
- ✅ Updated information displayed

---

#### TC-M-006: Deactivate Team
**Steps:**
1. Edit a team
2. Set status to "Inactive"
3. Save changes

**Expected Results:**
- ✅ Team marked as inactive
- ✅ Team still visible but marked inactive
- ✅ Cannot assign inactive team to new projects

---

### Test Case 13: Assignment Management

#### TC-M-007: Assign Task to User
**Steps:**
1. Navigate to "Tasks" page
2. Create or edit a task
3. Select user from "Assigned To" dropdown
4. Save task

**Expected Results:**
- ✅ Task assigned successfully
- ✅ User can see task in their assignments
- ✅ Task appears in user's workload

---

#### TC-M-008: Reassign Task
**Steps:**
1. Open an assigned task
2. Change "Assigned To" to different user
3. Save changes

**Expected Results:**
- ✅ Task reassigned successfully
- ✅ Previous assignee no longer sees task
- ✅ New assignee sees task in their list

---

## Sprint Functionality Testing

### Overview
Sprint functionality allows teams to organize work into time-boxed iterations. This section covers sprint configuration, creation, and management.

---

### What is a Sprint?

A **Sprint** is a time-boxed iteration (typically 1-2 weeks) where a team works on a specific set of tasks. Sprints help teams:
- Plan work in manageable chunks
- Track progress over time
- Deliver incremental value
- Maintain consistent velocity

**Sprint Lifecycle:**
1. **Planning** → Sprint is created and tasks are assigned
2. **Active** → Team works on sprint tasks
3. **Completed** → Sprint ends, tasks are reviewed
4. **Closed** → Sprint is archived

---

### Sprint Configuration

Before creating sprints, you must configure sprint settings for each project.

#### TC-S-001: Access Sprint Configuration
**Prerequisites:** Login as Admin or Product Owner

**Steps:**
1. Navigate to "Sprint Configuration" from sidebar
2. Review the configuration page

**Expected Results:**
- ✅ Page loads successfully
- ✅ Two tabs visible: "Configuration" and "Create Sprint"
- ✅ Non-admin users see access denied message

---

#### TC-S-002: Configure Sprint Settings
**Prerequisites:** At least one project exists

**Steps:**
1. Go to "Sprint Configuration" page
2. Click "Configuration" tab
3. Select a project from dropdown
4. Configure settings:
   - Sprint Length: Select "1 Week" or "2 Weeks"
   - Sprint Starting Day: Select day of week (e.g., "Monday")
5. Review the preview section
6. Click "Save Sprint Configuration"

**Expected Results:**
- ✅ Configuration saved successfully
- ✅ Success message displayed
- ✅ Preview shows correct sprint schedule
- ✅ End day calculated correctly (e.g., 2 weeks from Monday = Sunday)

---

#### TC-S-003: Verify Sprint Configuration Persistence
**Steps:**
1. Configure sprint settings for a project
2. Save configuration
3. Navigate away from the page
4. Return to Sprint Configuration
5. Select the same project

**Expected Results:**
- ✅ Previously saved settings are displayed
- ✅ Sprint length matches saved value
- ✅ Starting day matches saved value

---

### Sprint Creation

#### TC-S-004: Create Sprint with Default Dates
**Prerequisites:** Project has sprint configuration set

**Steps:**
1. Go to "Sprint Configuration" page
2. Click "Create Sprint" tab
3. Select a project from dropdown
4. Review auto-populated fields:
   - Sprint Name (auto-generated)
   - Start Date (calculated from configuration)
   - End Date (calculated from configuration)
5. Optionally modify:
   - Sprint Name: "Sprint 1 - Authentication"
   - Sprint Goal: "Implement user authentication"
6. Click "Create Sprint"

**Expected Results:**
- ✅ Sprint created successfully
- ✅ Sprint ID auto-generated (format: SPR-XXX or similar)
- ✅ Dates in DD/MM/YYYY format
- ✅ Sprint appears in "Existing Sprints" list
- ✅ Sprint status is "Planning"

---

#### TC-S-005: Create Sprint with Custom Dates
**Steps:**
1. Go to "Create Sprint" tab
2. Select a project
3. Modify the auto-populated dates:
   - Start Date: 20/01/2026
   - End Date: 03/02/2026
4. Enter sprint name and goal
5. Click "Create Sprint"

**Expected Results:**
- ✅ Sprint created with custom dates
- ✅ Dates validated (end date must be after start date)
- ✅ Sprint appears in list

---

#### TC-S-006: Date Validation in Sprint Creation
**Steps:**
1. Try to create sprint with end date before start date
2. Try to create sprint with invalid date format
3. Try to create sprint with overlapping dates

**Expected Results:**
- ✅ Error message: "Start date must be before end date"
- ✅ Date auto-corrects or shows validation error
- ✅ System prevents overlapping sprints for same project

---

#### TC-S-007: View Existing Sprints
**Steps:**
1. On "Create Sprint" tab
2. Select a project
3. Scroll to "Existing Sprints" section

**Expected Results:**
- ✅ All sprints for selected project displayed
- ✅ Sprint information shown:
  - Sprint ID and Name
  - Start and End dates (DD/MM/YYYY format)
  - Status (Planning/Active/Completed/Closed)
  - Task count
- ✅ Delete button visible for each sprint

---

#### TC-S-008: Delete Sprint (Empty)
**Steps:**
1. Create a new sprint (no tasks assigned)
2. Click "Delete" button on the sprint
3. Confirm deletion

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Sprint deleted successfully
- ✅ Sprint removed from list
- ✅ Success message displayed

---

#### TC-S-009: Delete Sprint (With Tasks)
**Steps:**
1. Select a sprint that has tasks assigned
2. Click "Delete" button
3. Review error message

**Expected Results:**
- ✅ Error message: "Cannot delete sprint with assigned tasks"
- ✅ Sprint not deleted
- ✅ Alert shows task count
- ✅ User must unassign tasks first

---

### Sprint Board

The Sprint Board is where teams manage their sprint work.

#### TC-S-010: Access Sprint Board
**Steps:**
1. Navigate to "Sprint" page from sidebar
2. Review the sprint board interface

**Expected Results:**
- ✅ Page loads successfully
- ✅ Project selection dropdown visible
- ✅ Sprint selection dropdown visible
- ✅ Instructions shown when no project selected

---

#### TC-S-011: Select Project and Sprint
**Steps:**
1. On Sprint Board page
2. Select a project from dropdown
3. Wait for sprints to load
4. Select a sprint from dropdown

**Expected Results:**
- ✅ Sprints filtered by selected project
- ✅ Sprint dropdown shows format: "SPR-001 (01-JAN-2026 to 14-JAN-2026)"
- ✅ Sprint overview section appears
- ✅ Sprint statistics displayed

---

#### TC-S-012: View Sprint Overview
**Steps:**
1. Select a project and sprint
2. Review the Sprint Overview section

**Expected Results:**
- ✅ Sprint name displayed
- ✅ Duration shown (start date - end date)
- ✅ Statistics visible:
  - Total Tasks
  - Completed Tasks
  - In Progress Tasks
  - To Do Tasks
- ✅ All dates in DD/MM/YYYY format

---

#### TC-S-013: View Sprint Progress
**Steps:**
1. Select a sprint with tasks
2. Review the Sprint Progress section

**Expected Results:**
- ✅ Completion percentage displayed (large number)
- ✅ Progress bar shows visual representation
- ✅ Percentage calculated correctly: (Completed / Total) × 100
- ✅ Progress updates when task status changes

---

#### TC-S-014: View Sprint Tasks
**Steps:**
1. Select a sprint
2. Scroll to "Sprint Tasks" section

**Expected Results:**
- ✅ All assigned tasks displayed
- ✅ Each task shows:
  - Task title
  - Due date (if set)
  - Status badge (color-coded)
  - Remove button
- ✅ Empty state message if no tasks assigned
- ✅ Status colors:
  - Done: Green
  - In Progress: Blue
  - To Do: Gray

---

#### TC-S-015: Assign Task to Sprint
**Prerequisites:** Sprint exists with unassigned tasks available

**Steps:**
1. Select a sprint
2. Scroll to "Available Tasks (Unassigned)" section
3. Find a task to assign
4. Click "Add to Sprint" button on the task

**Expected Results:**
- ✅ Task assigned successfully
- ✅ Task moves from "Available Tasks" to "Sprint Tasks"
- ✅ Task count updates in sprint overview
- ✅ Task's sprint_id updated in database

---

#### TC-S-016: Search Available Tasks
**Steps:**
1. Select a sprint
2. In "Available Tasks" section, use search bar
3. Type task title or description keywords
4. Review filtered results

**Expected Results:**
- ✅ Tasks filtered in real-time
- ✅ Matching tasks displayed
- ✅ Non-matching tasks hidden
- ✅ Task count shows "X of Y tasks"
- ✅ Clear search to show all tasks

---

#### TC-S-017: Remove Task from Sprint
**Steps:**
1. Select a sprint with assigned tasks
2. In "Sprint Tasks" section, click "Remove" on a task
3. Confirm removal (if prompted)

**Expected Results:**
- ✅ Task removed from sprint
- ✅ Task moves to "Available Tasks" section
- ✅ Task count updates in sprint overview
- ✅ Task's sprint_id cleared in database

---

#### TC-S-018: Sprint Task Status Update
**Steps:**
1. Assign tasks to a sprint
2. Go to "Tasks" page
3. Update task status (e.g., To Do → In Progress → Done)
4. Return to Sprint Board
5. Review sprint statistics

**Expected Results:**
- ✅ Sprint statistics update automatically
- ✅ Completed count increases when task marked Done
- ✅ In Progress count updates correctly
- ✅ Progress percentage recalculates
- ✅ Progress bar updates visually

---

#### TC-S-019: Multiple Sprint Management
**Steps:**
1. Create multiple sprints for same project
2. Assign different tasks to each sprint
3. Switch between sprints on Sprint Board

**Expected Results:**
- ✅ Each sprint shows only its assigned tasks
- ✅ No task appears in multiple sprints
- ✅ Statistics calculated independently per sprint
- ✅ Sprint selection works smoothly

---

#### TC-S-020: Sprint Workflow End-to-End
**Complete workflow test**

**Steps:**
1. **Configuration Phase:**
   - Login as Admin/Product Owner
   - Go to Sprint Configuration
   - Configure sprint settings for a project (2 weeks, Monday start)
   - Save configuration

2. **Creation Phase:**
   - Go to "Create Sprint" tab
   - Select the project
   - Create "Sprint 1" with default dates
   - Add sprint goal: "Complete authentication module"

3. **Planning Phase:**
   - Go to Sprint Board
   - Select project and Sprint 1
   - Search for authentication-related tasks
   - Assign 5-10 tasks to the sprint

4. **Execution Phase:**
   - Go to Tasks page
   - Update task statuses as work progresses:
     - Mark 2 tasks as "In Progress"
     - Mark 3 tasks as "Done"
   - Return to Sprint Board
   - Verify progress updates

5. **Completion Phase:**
   - Mark all remaining tasks as "Done"
   - Verify sprint shows 100% completion
   - Review sprint statistics

**Expected Results:**
- ✅ All phases complete without errors
- ✅ Data flows correctly between pages
- ✅ Statistics update in real-time
- ✅ Sprint progress tracked accurately
- ✅ No data loss or inconsistencies

---

### Sprint Testing - Edge Cases

#### TC-S-021: Empty Sprint Handling
**Steps:**
1. Create a sprint
2. Don't assign any tasks
3. View sprint on Sprint Board

**Expected Results:**
- ✅ Sprint displays with 0 tasks
- ✅ Progress shows 0%
- ✅ "No tasks assigned" message shown
- ✅ Available tasks section works normally

---

#### TC-S-022: Sprint Date Boundaries
**Steps:**
1. Create sprint ending today
2. Create sprint starting tomorrow
3. View both sprints

**Expected Results:**
- ✅ Both sprints created successfully
- ✅ No overlap validation errors
- ✅ Dates displayed correctly
- ✅ Can assign tasks to both sprints

---

#### TC-S-023: Task Assignment Limits
**Steps:**
1. Create a sprint
2. Try to assign same task to multiple sprints
3. Verify task assignment

**Expected Results:**
- ✅ Task can only be in one sprint at a time
- ✅ Assigning to new sprint removes from old sprint
- ✅ Or error message prevents multiple assignments

---

#### TC-S-024: Sprint Configuration Changes
**Steps:**
1. Configure sprint settings (2 weeks, Monday)
2. Create a sprint with these settings
3. Change configuration (1 week, Wednesday)
4. Create another sprint

**Expected Results:**
- ✅ Existing sprint unaffected by configuration change
- ✅ New sprint uses new configuration
- ✅ Both sprints coexist correctly

---

## Common Testing Scenarios

### Date Format Testing (Critical)

All dates throughout the application must display in **DD/MM/YYYY** format.

#### TC-COMMON-001: Date Format Verification
**Test all pages with dates:**

1. **Programs Page:**
   - Create program with dates
   - Verify display format: DD/MM/YYYY
   - Edit program, verify dates load correctly

2. **Projects Page:**
   - Create project with dates
   - Verify display format: DD/MM/YYYY
   - Edit project, verify dates load correctly

3. **Tasks Page:**
   - Create task with due date
   - Verify display format: DD/MM/YYYY
   - Edit task, verify date loads correctly

4. **Subtasks Page:**
   - Create subtask with due date
   - Verify display format: DD/MM/YYYY

5. **Sprint Configuration:**
   - Create sprint with dates
   - Verify display format: DD/MM/YYYY
   - Verify sprint list shows dates correctly

6. **Sprint Board:**
   - View sprint dates
   - Verify format: DD-MMM-YYYY (e.g., 01-JAN-2026)

**Expected Results:**
- ✅ All dates display in DD/MM/YYYY format
- ✅ Date input accepts DD/MM/YYYY format
- ✅ Date validation works correctly
- ✅ No "NaN/NaN/NaN" errors
- ✅ Dates save and load correctly

---

### Authentication & Session Testing

#### TC-COMMON-002: Session Expiration Handling
**Steps:**
1. Login to application
2. Wait for 30 minutes (token expiration time)
3. Try to navigate to any page (e.g., Subtasks)

**Expected Results:**
- ✅ Session expired modal appears
- ✅ Modal blocks interaction with page
- ✅ "Go to Login" button redirects to login page
- ✅ No automatic logout without user action
- ✅ After re-login, can access all features

---

#### TC-COMMON-003: Role-Based Access Control
**Test with different user roles:**

| Feature | Admin | Product Owner | Developer | QA Tester |
|---------|-------|---------------|-----------|-----------|
| View Clients | ✅ | ✅ | ✅ | ✅ |
| Create Client | ✅ | ❌ | ❌ | ❌ |
| View Projects | ✅ | ✅ | ✅ | ✅ |
| Create Project | ✅ | ✅ | ❌ | ❌ |
| View Tasks | ✅ | ✅ | ✅ | ✅ |
| Create Task | ✅ | ✅ | ✅ | ❌ |
| Update Task Status | ✅ | ✅ | ✅ | ✅ |
| Manage Phases | ✅ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Sprint Configuration | ✅ | ✅ | ❌ | ❌ |
| Sprint Board | ✅ | ✅ | ✅ | ✅ |
| Manage Teams | ✅ | ✅ | ❌ | ❌ |

**Expected Results:**
- ✅ Each role has appropriate access
- ✅ Unauthorized actions show error message
- ✅ UI hides/disables restricted features

---

### Data Validation Testing

#### TC-COMMON-004: Required Field Validation
**Test on all forms:**

**Steps:**
1. Open any create/edit form
2. Leave required fields empty
3. Try to submit

**Expected Results:**
- ✅ Form validation prevents submission
- ✅ Error messages shown for empty required fields
- ✅ Fields marked with red asterisk (*)
- ✅ Clear error messages (e.g., "Name is required")

---

#### TC-COMMON-005: Data Type Validation
**Test various input types:**

1. **Email Fields:**
   - Enter invalid email → Error message
   - Enter valid email → Accepted

2. **Phone Fields:**
   - Enter letters → Validation error or auto-format
   - Enter valid phone → Accepted

3. **Number Fields:**
   - Enter text → Validation error
   - Enter negative numbers (where not allowed) → Error
   - Enter valid numbers → Accepted

4. **Date Fields:**
   - Enter invalid format → Auto-correct or error
   - Enter future date (where not allowed) → Error
   - Enter valid date → Accepted

**Expected Results:**
- ✅ All validations work correctly
- ✅ Clear error messages
- ✅ No data corruption

---

### Performance Testing

#### TC-COMMON-006: Page Load Performance
**Steps:**
1. Clear browser cache
2. Login to application
3. Navigate to each major page
4. Measure load time

**Expected Results:**
- ✅ Dashboard loads in < 2 seconds
- ✅ List pages (Clients, Projects, Tasks) load in < 3 seconds
- ✅ Detail pages load in < 2 seconds
- ✅ No infinite loading states
- ✅ Loading indicators shown during data fetch

---

#### TC-COMMON-007: Large Dataset Handling
**Steps:**
1. Create 50+ clients
2. Create 100+ projects
3. Create 500+ tasks
4. Navigate through pages
5. Use search and filters

**Expected Results:**
- ✅ Pages load without crashing
- ✅ Pagination works correctly
- ✅ Search performs reasonably fast
- ✅ No browser freezing
- ✅ Smooth scrolling

---

### Browser Compatibility Testing

#### TC-COMMON-008: Cross-Browser Testing
**Test on multiple browsers:**

1. **Chrome (Latest)**
   - All features work
   - UI renders correctly
   - No console errors

2. **Firefox (Latest)**
   - All features work
   - UI renders correctly
   - No console errors

3. **Edge (Latest)**
   - All features work
   - UI renders correctly
   - No console errors

4. **Safari (if available)**
   - All features work
   - UI renders correctly
   - No console errors

**Expected Results:**
- ✅ Consistent behavior across browsers
- ✅ No browser-specific bugs
- ✅ UI looks consistent

---

## Test Execution Checklist

### Pre-Testing Setup
- [ ] Docker Desktop running
- [ ] Database container healthy
- [ ] API container healthy
- [ ] UI server running on port 3007
- [ ] Test user accounts created for each role
- [ ] Browser developer tools open for monitoring

### Hierarchy Section
- [ ] TC-H-001: Create Client (Admin)
- [ ] TC-H-002: View Client Details
- [ ] TC-H-003: Edit Client
- [ ] TC-H-004: Delete Client
- [ ] TC-H-005: Create Program
- [ ] TC-H-006: View Program Details
- [ ] TC-H-007: Create Project
- [ ] TC-H-008: Assign Team to Project
- [ ] TC-H-009: Create Use Case
- [ ] TC-H-010: Create User Story
- [ ] TC-H-011: Create Task
- [ ] TC-H-012: Create Subtask
- [ ] TC-H-013: View Complete Hierarchy
- [ ] TC-H-014: Navigate Through Hierarchy

### Administration Section
- [ ] TC-A-001: View Phases
- [ ] TC-A-002: Create New Phase
- [ ] TC-A-003: Edit Phase
- [ ] TC-A-004: Delete Phase
- [ ] TC-A-005: View Users
- [ ] TC-A-006: Create New User
- [ ] TC-A-007: Edit User
- [ ] TC-A-008: Deactivate User
- [ ] TC-A-009: View Organizations
- [ ] TC-A-010: Create Organization
- [ ] TC-A-011: Edit Organization
- [ ] TC-A-012: Access Control Test

### Management Section
- [ ] TC-M-001: View Teams
- [ ] TC-M-002: Create Team
- [ ] TC-M-003: Add Team Members
- [ ] TC-M-004: Remove Team Member
- [ ] TC-M-005: Edit Team
- [ ] TC-M-006: Deactivate Team
- [ ] TC-M-007: Assign Task to User
- [ ] TC-M-008: Reassign Task

### Sprint Functionality
- [ ] TC-S-001: Access Sprint Configuration
- [ ] TC-S-002: Configure Sprint Settings
- [ ] TC-S-003: Verify Configuration Persistence
- [ ] TC-S-004: Create Sprint with Default Dates
- [ ] TC-S-005: Create Sprint with Custom Dates
- [ ] TC-S-006: Date Validation in Sprint Creation
- [ ] TC-S-007: View Existing Sprints
- [ ] TC-S-008: Delete Sprint (Empty)
- [ ] TC-S-009: Delete Sprint (With Tasks)
- [ ] TC-S-010: Access Sprint Board
- [ ] TC-S-011: Select Project and Sprint
- [ ] TC-S-012: View Sprint Overview
- [ ] TC-S-013: View Sprint Progress
- [ ] TC-S-014: View Sprint Tasks
- [ ] TC-S-015: Assign Task to Sprint
- [ ] TC-S-016: Search Available Tasks
- [ ] TC-S-017: Remove Task from Sprint
- [ ] TC-S-018: Sprint Task Status Update
- [ ] TC-S-019: Multiple Sprint Management
- [ ] TC-S-020: Sprint Workflow End-to-End
- [ ] TC-S-021: Empty Sprint Handling
- [ ] TC-S-022: Sprint Date Boundaries
- [ ] TC-S-023: Task Assignment Limits
- [ ] TC-S-024: Sprint Configuration Changes

### Common Scenarios
- [ ] TC-COMMON-001: Date Format Verification
- [ ] TC-COMMON-002: Session Expiration Handling
- [ ] TC-COMMON-003: Role-Based Access Control
- [ ] TC-COMMON-004: Required Field Validation
- [ ] TC-COMMON-005: Data Type Validation
- [ ] TC-COMMON-006: Page Load Performance
- [ ] TC-COMMON-007: Large Dataset Handling
- [ ] TC-COMMON-008: Cross-Browser Testing

---

## Bug Reporting Template

When you find a bug during testing, report it using this template:

### Bug Report Format

**Bug ID:** BUG-XXX  
**Test Case:** TC-X-XXX  
**Severity:** Critical / High / Medium / Low  
**Priority:** P1 / P2 / P3 / P4

**Title:** [Short description of the bug]

**Environment:**
- Browser: [Chrome/Firefox/Edge/Safari]
- Browser Version: [Version number]
- OS: [Windows/Mac/Linux]
- User Role: [Admin/Product Owner/Developer/QA Tester]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Screenshots/Videos:**
[Attach if available]

**Console Errors:**
[Copy any browser console errors]

**Additional Notes:**
[Any other relevant information]

---

## Test Results Summary Template

### Test Execution Summary

**Test Date:** [Date]  
**Tester Name:** [Name]  
**Environment:** [Development/Staging/Production]

**Overall Statistics:**
- Total Test Cases: XX
- Passed: XX
- Failed: XX
- Blocked: XX
- Not Executed: XX
- Pass Rate: XX%

**Section-wise Results:**

| Section | Total | Passed | Failed | Pass Rate |
|---------|-------|--------|--------|-----------|
| Hierarchy | 14 | XX | XX | XX% |
| Administration | 12 | XX | XX | XX% |
| Management | 8 | XX | XX | XX% |
| Sprint Functionality | 24 | XX | XX | XX% |
| Common Scenarios | 8 | XX | XX | XX% |

**Critical Issues Found:**
1. [Issue 1]
2. [Issue 2]

**Recommendations:**
- [Recommendation 1]
- [Recommendation 2]

**Sign-off:**
- QA Lead: ________________
- Product Owner: ________________
- Date: ________________

---

## Production Readiness Criteria

Before moving to production, ensure all the following criteria are met:

### Functional Completeness
- [ ] All hierarchy levels (Client → Subtask) working correctly
- [ ] All CRUD operations functional
- [ ] Date formats consistent (DD/MM/YYYY) across application
- [ ] Sprint configuration and management working
- [ ] Sprint board fully functional
- [ ] Team management operational
- [ ] User management working
- [ ] Role-based access control enforced

### Data Integrity
- [ ] No data loss during operations
- [ ] Relationships maintained correctly
- [ ] Foreign key constraints working
- [ ] Cascade deletes working as expected
- [ ] Data validation preventing invalid entries

### Security
- [ ] Authentication working correctly
- [ ] Session management functional
- [ ] Session expiration handled gracefully
- [ ] Role-based permissions enforced
- [ ] No unauthorized access possible
- [ ] Sensitive data protected

### Performance
- [ ] Pages load within acceptable time
- [ ] No memory leaks
- [ ] Large datasets handled correctly
- [ ] Search and filters perform well
- [ ] No browser crashes or freezes

### User Experience
- [ ] UI consistent across pages
- [ ] Error messages clear and helpful
- [ ] Loading states shown appropriately
- [ ] Forms validate correctly
- [ ] Navigation intuitive
- [ ] Responsive design working

### Browser Compatibility
- [ ] Works on Chrome (latest)
- [ ] Works on Firefox (latest)
- [ ] Works on Edge (latest)
- [ ] Works on Safari (if applicable)

### Documentation
- [ ] User manual available
- [ ] Admin guide available
- [ ] API documentation complete
- [ ] Deployment guide ready

### Testing Coverage
- [ ] All test cases executed
- [ ] Pass rate > 95%
- [ ] All critical bugs fixed
- [ ] All high-priority bugs fixed
- [ ] Medium/low bugs documented

---

## Known Issues & Workarounds

### Issue 1: Session Expiration After 30 Minutes
**Description:** Authentication token expires after 30 minutes of inactivity.

**Workaround:**
1. When session expired modal appears
2. Click "Go to Login"
3. Log in again with credentials
4. Continue working

**Status:** Working as designed. Consider implementing token refresh in future.

---

### Issue 2: PowerShell Execution Policy (Windows)
**Description:** UI server may not start due to PowerShell execution policy.

**Workaround:**
Use CMD instead:
```bash
cd ui
cmd /c "npm run dev"
```

**Status:** Environment-specific issue, not application bug.

---

## Testing Tips & Best Practices

### 1. Test Data Management
- Use consistent naming conventions (e.g., "Test Client 001")
- Create test data in logical order (Client → Program → Project → etc.)
- Clean up test data after testing
- Don't use production-like data in testing

### 2. Browser Developer Tools
- Keep console open to catch JavaScript errors
- Monitor Network tab for API failures
- Check Application tab for storage issues
- Use React DevTools for component debugging

### 3. Test Execution
- Follow test cases in order
- Document deviations from expected results
- Take screenshots of bugs
- Note exact steps to reproduce issues
- Test both positive and negative scenarios

### 4. Regression Testing
- After bug fixes, re-run related test cases
- Verify fix doesn't break other features
- Test edge cases around the fix

### 5. Exploratory Testing
- Try unexpected user actions
- Test with different data combinations
- Attempt to break the application
- Think like an end user

---

## Glossary

**Sprint:** Time-boxed iteration (1-2 weeks) for completing work  
**Hierarchy:** Structured levels from Client to Subtask  
**CRUD:** Create, Read, Update, Delete operations  
**Role-Based Access Control (RBAC):** Permissions based on user role  
**Session:** User's authenticated period in the application  
**Token:** Authentication credential with expiration time  
**Validation:** Checking data meets requirements before saving  
**Edge Case:** Unusual or extreme scenario that might cause issues

---

## Contact & Support

**For Questions:**
- Development Team: [Contact Info]
- QA Lead: [Contact Info]
- Product Owner: [Contact Info]

**For Bug Reports:**
- Use bug tracking system
- Follow bug report template
- Include all required information

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | January 2026 | QA Team | Initial release |

---

**End of QA Testing Guide**


-- Worky Database Schema - Migration 010
-- Version: 010
-- Description: Add metadata for UI field grouping and collapsible sections

-- This migration adds comments to document field categories for UI rendering
-- UI should group fields into collapsible sections based on these categories

-- Field Categories for All Entities:
-- 1. Basic Information (always expanded by default)
-- 2. Dates & Timeline (collapsible)
-- 3. Assignment & Ownership (collapsible)
-- 4. Status & Priority (collapsible)
-- 5. Descriptions (collapsible)
-- 6. Metadata (collapsible, read-only)

-- CLIENTS
COMMENT ON COLUMN clients.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN clients.name IS 'Category: Basic Information | Client name (required)';
COMMENT ON COLUMN clients.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN clients.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN clients.is_active IS 'Category: Status & Priority | Active status';
COMMENT ON COLUMN clients.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN clients.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN clients.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN clients.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN clients.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- PROGRAMS
COMMENT ON COLUMN programs.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN programs.client_id IS 'Category: Basic Information | Parent client (required)';
COMMENT ON COLUMN programs.name IS 'Category: Basic Information | Program name (required)';
COMMENT ON COLUMN programs.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN programs.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN programs.start_date IS 'Category: Dates & Timeline | Program start date';
COMMENT ON COLUMN programs.end_date IS 'Category: Dates & Timeline | Program end date';
COMMENT ON COLUMN programs.status IS 'Category: Status & Priority | Program status (Planning, Active, On Hold, Completed, Cancelled)';
COMMENT ON COLUMN programs.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN programs.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN programs.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN programs.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN programs.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- PROJECTS
COMMENT ON COLUMN projects.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN projects.program_id IS 'Category: Basic Information | Parent program (required)';
COMMENT ON COLUMN projects.name IS 'Category: Basic Information | Project name (required)';
COMMENT ON COLUMN projects.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN projects.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN projects.repository_url IS 'Category: Basic Information | Git repository URL';
COMMENT ON COLUMN projects.start_date IS 'Category: Dates & Timeline | Project start date';
COMMENT ON COLUMN projects.end_date IS 'Category: Dates & Timeline | Project end date';
COMMENT ON COLUMN projects.status IS 'Category: Status & Priority | Project status (Planning, Active, On Hold, Completed, Cancelled)';
COMMENT ON COLUMN projects.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN projects.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN projects.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN projects.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN projects.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- USECASES
COMMENT ON COLUMN usecases.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN usecases.project_id IS 'Category: Basic Information | Parent project (required)';
COMMENT ON COLUMN usecases.name IS 'Category: Basic Information | Use case name (required)';
COMMENT ON COLUMN usecases.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN usecases.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN usecases.priority IS 'Category: Status & Priority | Priority level (Critical, High, Medium, Low)';
COMMENT ON COLUMN usecases.status IS 'Category: Status & Priority | Use case status (Draft, In Review, Approved, In Progress, Completed)';
COMMENT ON COLUMN usecases.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN usecases.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN usecases.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN usecases.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN usecases.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- USER_STORIES
COMMENT ON COLUMN user_stories.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN user_stories.usecase_id IS 'Category: Basic Information | Parent use case (required)';
COMMENT ON COLUMN user_stories.name IS 'Category: Basic Information | User story name (required)';
COMMENT ON COLUMN user_stories.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN user_stories.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN user_stories.acceptance_criteria IS 'Category: Descriptions | Acceptance criteria';
COMMENT ON COLUMN user_stories.story_points IS 'Category: Status & Priority | Story points for estimation';
COMMENT ON COLUMN user_stories.priority IS 'Category: Status & Priority | Priority level (Critical, High, Medium, Low)';
COMMENT ON COLUMN user_stories.status IS 'Category: Status & Priority | User story status (Backlog, Ready, In Progress, In Review, Done)';
COMMENT ON COLUMN user_stories.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN user_stories.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN user_stories.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN user_stories.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN user_stories.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- TASKS
COMMENT ON COLUMN tasks.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN tasks.user_story_id IS 'Category: Basic Information | Parent user story (required)';
COMMENT ON COLUMN tasks.name IS 'Category: Basic Information | Task name (required)';
COMMENT ON COLUMN tasks.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN tasks.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN tasks.phase_id IS 'Category: Status & Priority | Work phase (required: Development, Analysis, Design, Testing)';
COMMENT ON COLUMN tasks.status IS 'Category: Status & Priority | Task status (To Do, In Progress, In Review, Done, Blocked)';
COMMENT ON COLUMN tasks.priority IS 'Category: Status & Priority | Priority level (Critical, High, Medium, Low)';
COMMENT ON COLUMN tasks.assigned_to IS 'Category: Assignment & Ownership | Assigned user';
COMMENT ON COLUMN tasks.estimated_hours IS 'Category: Dates & Timeline | Estimated effort in hours';
COMMENT ON COLUMN tasks.actual_hours IS 'Category: Dates & Timeline | Actual effort in hours';
COMMENT ON COLUMN tasks.start_date IS 'Category: Dates & Timeline | Task start date';
COMMENT ON COLUMN tasks.due_date IS 'Category: Dates & Timeline | Task due date';
COMMENT ON COLUMN tasks.completed_at IS 'Category: Dates & Timeline | Completion timestamp';
COMMENT ON COLUMN tasks.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN tasks.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN tasks.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN tasks.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN tasks.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- SUBTASKS
COMMENT ON COLUMN subtasks.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN subtasks.task_id IS 'Category: Basic Information | Parent task (required)';
COMMENT ON COLUMN subtasks.name IS 'Category: Basic Information | Subtask name (required)';
COMMENT ON COLUMN subtasks.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN subtasks.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN subtasks.phase_id IS 'Category: Status & Priority | Work phase (required: Development, Analysis, Design, Testing)';
COMMENT ON COLUMN subtasks.status IS 'Category: Status & Priority | Subtask status (To Do, In Progress, Done, Blocked)';
COMMENT ON COLUMN subtasks.assigned_to IS 'Category: Assignment & Ownership | Assigned user';
COMMENT ON COLUMN subtasks.estimated_hours IS 'Category: Dates & Timeline | Estimated effort in hours';
COMMENT ON COLUMN subtasks.actual_hours IS 'Category: Dates & Timeline | Actual effort in hours';
COMMENT ON COLUMN subtasks.completed_at IS 'Category: Dates & Timeline | Completion timestamp';
COMMENT ON COLUMN subtasks.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN subtasks.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN subtasks.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN subtasks.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN subtasks.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- PHASES
COMMENT ON COLUMN phases.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN phases.name IS 'Category: Basic Information | Phase name (required, unique)';
COMMENT ON COLUMN phases.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN phases.long_description IS 'Category: Descriptions | Detailed description';
COMMENT ON COLUMN phases.color IS 'Category: Basic Information | Display color (hex code)';
COMMENT ON COLUMN phases.is_active IS 'Category: Status & Priority | Active status';
COMMENT ON COLUMN phases.display_order IS 'Category: Basic Information | Sort order for display';
COMMENT ON COLUMN phases.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN phases.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN phases.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN phases.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN phases.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- BUGS
COMMENT ON COLUMN bugs.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN bugs.entity_type IS 'Category: Basic Information | Related entity type (required)';
COMMENT ON COLUMN bugs.entity_id IS 'Category: Basic Information | Related entity ID (required)';
COMMENT ON COLUMN bugs.title IS 'Category: Basic Information | Bug title (required)';
COMMENT ON COLUMN bugs.short_description IS 'Category: Descriptions | Brief summary (max 500 chars)';
COMMENT ON COLUMN bugs.long_description IS 'Category: Descriptions | Detailed description with steps to reproduce';
COMMENT ON COLUMN bugs.severity IS 'Category: Status & Priority | Severity level (Critical, High, Medium, Low)';
COMMENT ON COLUMN bugs.priority IS 'Category: Status & Priority | Priority level (P0, P1, P2, P3)';
COMMENT ON COLUMN bugs.status IS 'Category: Status & Priority | Bug status (New, Assigned, In Progress, Fixed, Verified, Closed, Reopened)';
COMMENT ON COLUMN bugs.assigned_to IS 'Category: Assignment & Ownership | Assigned user';
COMMENT ON COLUMN bugs.reported_by IS 'Category: Assignment & Ownership | Reporter user (required)';
COMMENT ON COLUMN bugs.resolution_notes IS 'Category: Descriptions | Resolution notes';
COMMENT ON COLUMN bugs.closed_at IS 'Category: Dates & Timeline | Closure timestamp';
COMMENT ON COLUMN bugs.is_deleted IS 'Category: Metadata | Soft delete flag (system managed)';
COMMENT ON COLUMN bugs.created_at IS 'Category: Metadata | Creation timestamp (read-only)';
COMMENT ON COLUMN bugs.updated_at IS 'Category: Metadata | Last update timestamp (read-only)';
COMMENT ON COLUMN bugs.created_by IS 'Category: Metadata | Created by user (read-only)';
COMMENT ON COLUMN bugs.updated_by IS 'Category: Metadata | Last updated by user (read-only)';

-- ENTITY_NOTES
COMMENT ON COLUMN entity_notes.id IS 'Category: Metadata | Auto-generated unique identifier';
COMMENT ON COLUMN entity_notes.entity_type IS 'Category: Basic Information | Related entity type (required)';
COMMENT ON COLUMN entity_notes.entity_id IS 'Category: Basic Information | Related entity ID (required)';
COMMENT ON COLUMN entity_notes.note_text IS 'Category: Basic Information | Note content (required)';
COMMENT ON COLUMN entity_notes.created_by IS 'Category: Metadata | Author user (read-only)';
COMMENT ON COLUMN entity_notes.created_at IS 'Category: Metadata | Creation timestamp (read-only)';

-- Add table-level comments for UI guidance
COMMENT ON TABLE clients IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE programs IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Dates & Timeline (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE projects IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Dates & Timeline (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE usecases IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE user_stories IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE tasks IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Assignment & Ownership (collapsed), Dates & Timeline (collapsed), Metadata (collapsed)';
COMMENT ON TABLE subtasks IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Assignment & Ownership (collapsed), Dates & Timeline (collapsed), Metadata (collapsed)';
COMMENT ON TABLE phases IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Metadata (collapsed)';
COMMENT ON TABLE bugs IS 'UI Categories: Basic Information (expanded), Descriptions (collapsed), Status & Priority (collapsed), Assignment & Ownership (collapsed), Dates & Timeline (collapsed), Metadata (collapsed)';
COMMENT ON TABLE entity_notes IS 'UI Categories: Basic Information (expanded), Metadata (collapsed, read-only)';

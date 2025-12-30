-- ============================================================================
-- Worky Database - Consolidated Baseline Schema
-- ============================================================================
-- This file consolidates all migrations (001-031) into a single baseline schema
-- Use this for new deployments. For existing deployments, use incremental migrations.
-- 
-- Created: 2025-12-29
-- Description: Complete database schema for Worky project management system
-- ============================================================================

-- ============================================================================
-- SECTION 1: EXTENSIONS AND FUNCTIONS
-- ============================================================================

-- Enable UUID extension (for chat_audit_logs table)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create function to generate string IDs (format: PREFIX-XXXXXX)
CREATE OR REPLACE FUNCTION generate_string_id(prefix TEXT, seq_name TEXT)
RETURNS TEXT AS $$
DECLARE
    next_val INTEGER;
    string_id TEXT;
BEGIN
    EXECUTE format('SELECT nextval(%L)', seq_name) INTO next_val;
    string_id := prefix || '-' || LPAD(next_val::TEXT, 6, '0');
    RETURN string_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function to prevent note modification (entity_notes are immutable)
CREATE OR REPLACE FUNCTION prevent_note_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Notes are immutable and cannot be modified or deleted';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create function for default notification preferences
CREATE OR REPLACE FUNCTION create_default_notification_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO notification_preferences (user_id, notification_type, email_enabled, in_app_enabled, push_enabled)
    VALUES 
        (NEW.id, 'assignment_created', TRUE, TRUE, FALSE),
        (NEW.id, 'assignment_removed', TRUE, TRUE, FALSE),
        (NEW.id, 'team_member_added', TRUE, TRUE, FALSE),
        (NEW.id, 'team_member_removed', TRUE, TRUE, FALSE),
        (NEW.id, 'assignment_conflict', TRUE, TRUE, FALSE),
        (NEW.id, 'bulk_assignment_completed', TRUE, TRUE, FALSE),
        (NEW.id, 'bulk_assignment_failed', TRUE, TRUE, FALSE);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function to update notification preferences timestamp
CREATE OR REPLACE FUNCTION update_notification_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECTION 2: SEQUENCES FOR ID GENERATION
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS clients_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS programs_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS projects_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS usecases_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS user_stories_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS tasks_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS subtasks_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS phases_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bugs_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS audit_logs_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS entity_history_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS entity_notes_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS sprints_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS company_settings_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS organizations_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS todo_items_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS adhoc_notes_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notifications_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_preferences_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_history_id_seq START 1;

-- ============================================================================
-- SECTION 3: CORE ENTITY TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Clients Table
-- ----------------------------------------------------------------------------
CREATE TABLE clients (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CLI', 'clients_id_seq'),
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Users Table
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('USR', 'users_id_seq'),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer')),
    primary_role VARCHAR(50) DEFAULT 'Developer',
    secondary_roles TEXT[],
    is_contact_person BOOLEAN DEFAULT FALSE,
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(50) DEFAULT 'snow',
    view_preferences JSONB DEFAULT '{"defaultView": "tile", "entityViews": {"clients": "tile", "programs": "tile", "projects": "tile", "usecases": "list", "userstories": "list", "tasks": "list", "subtasks": "list", "bugs": "list"}}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Phases Table
-- ----------------------------------------------------------------------------
CREATE TABLE phases (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PHS', 'phases_id_seq'),
    name VARCHAR(100) NOT NULL UNIQUE,
    short_description VARCHAR(500),
    long_description TEXT,
    color VARCHAR(7) NOT NULL DEFAULT '#4A90E2',
    is_active BOOLEAN DEFAULT true NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Programs Table
-- ----------------------------------------------------------------------------
CREATE TABLE programs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PRG', 'programs_id_seq'),
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planning',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Projects Table
-- ----------------------------------------------------------------------------
CREATE TABLE projects (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PRJ', 'projects_id_seq'),
    program_id VARCHAR(20) NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    repository_url VARCHAR(500),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planning',
    sprint_length_weeks VARCHAR(10) DEFAULT '2',
    sprint_starting_day VARCHAR(20) DEFAULT 'Monday',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Usecases Table
-- ----------------------------------------------------------------------------
CREATE TABLE usecases (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('USC', 'usecases_id_seq'),
    project_id VARCHAR(20) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Draft',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- User Stories Table
-- ----------------------------------------------------------------------------
CREATE TABLE user_stories (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('UST', 'user_stories_id_seq'),
    usecase_id VARCHAR(20) NOT NULL REFERENCES usecases(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    acceptance_criteria TEXT,
    story_points INTEGER,
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Backlog',
    phase_id VARCHAR(20) NOT NULL REFERENCES phases(id),
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Tasks Table
-- ----------------------------------------------------------------------------
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TSK', 'tasks_id_seq'),
    user_story_id VARCHAR(20) NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    phase_id VARCHAR(20) NOT NULL REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'To Do',
    priority VARCHAR(20) DEFAULT 'Medium',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    start_date DATE,
    due_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    sprint_id VARCHAR(20) REFERENCES sprints(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Subtasks Table
-- ----------------------------------------------------------------------------
CREATE TABLE subtasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SUB', 'subtasks_id_seq'),
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    phase_id VARCHAR(20) REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'To Do',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    duration_days INTEGER,
    scrum_points NUMERIC(5, 2),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20),
    updated_by VARCHAR(20)
);

-- ============================================================================
-- SECTION 4: SUPPORTING TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Dependencies Table
-- ----------------------------------------------------------------------------
CREATE TABLE dependencies (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('DEP', 'dependencies_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    entity_id VARCHAR(20) NOT NULL,
    depends_on_type VARCHAR(50) NOT NULL CHECK (depends_on_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    depends_on_id VARCHAR(20) NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'finish_to_start' CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Commits Table (Git Integration)
-- ----------------------------------------------------------------------------
CREATE TABLE commits (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('COM', 'commits_id_seq'),
    task_id VARCHAR(20) REFERENCES tasks(id) ON DELETE SET NULL,
    repository VARCHAR(255) NOT NULL,
    commit_hash VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    author_email VARCHAR(255),
    message TEXT NOT NULL,
    committed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    branch VARCHAR(255),
    url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Pull Requests Table
-- ----------------------------------------------------------------------------
CREATE TABLE pull_requests (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PR', 'pull_requests_id_seq'),
    task_id VARCHAR(20) REFERENCES tasks(id) ON DELETE SET NULL,
    repository VARCHAR(255) NOT NULL,
    pr_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    merged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Bugs Table (Enhanced with QA fields)
-- ----------------------------------------------------------------------------
CREATE TABLE bugs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BUG', 'bugs_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask')),
    entity_id VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    description TEXT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('P0', 'P1', 'P2', 'P3')),
    status VARCHAR(50) DEFAULT 'New' CHECK (status IN ('New', 'Assigned', 'In Progress', 'Fixed', 'Verified', 'Closed', 'Reopened')),
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    reported_by VARCHAR(20) NOT NULL REFERENCES users(id),
    resolution_notes TEXT,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id),
    -- QA Enhancement Fields
    test_run_id VARCHAR(20) REFERENCES test_runs(id),
    test_case_id VARCHAR(20) REFERENCES test_cases(id),
    client_id VARCHAR(20) REFERENCES clients(id),
    program_id VARCHAR(20) REFERENCES programs(id),
    project_id VARCHAR(20) REFERENCES projects(id),
    usecase_id VARCHAR(20) REFERENCES usecases(id),
    user_story_id VARCHAR(20) REFERENCES user_stories(id),
    task_id VARCHAR(20) REFERENCES tasks(id),
    subtask_id VARCHAR(20) REFERENCES subtasks(id),
    category VARCHAR(50),
    reporter_id VARCHAR(20) REFERENCES users(id),
    assignee_id VARCHAR(20) REFERENCES users(id),
    qa_owner_id VARCHAR(20) REFERENCES users(id),
    reproduction_steps TEXT,
    expected_result TEXT,
    actual_result TEXT,
    linked_task_id VARCHAR(20),
    linked_commit VARCHAR(255),
    linked_pr VARCHAR(255),
    component_attached_to VARCHAR(255),
    environment VARCHAR(255),
    reopen_count INTEGER DEFAULT 0,
    bug_type VARCHAR(50),
    resolution_type VARCHAR(50),
    found_in_version VARCHAR(50),
    fixed_in_version VARCHAR(50),
    browser VARCHAR(50),
    os VARCHAR(50),
    device_type VARCHAR(50),
    steps_to_reproduce TEXT,
    expected_behavior TEXT,
    actual_behavior TEXT
);

-- ----------------------------------------------------------------------------
-- Documentation Table
-- ----------------------------------------------------------------------------
CREATE TABLE documentation (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('DOC', 'documentation_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Client', 'Program', 'Project', 'Usecase', 'UserStory', 'Task')),
    entity_id VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    format VARCHAR(20) DEFAULT 'markdown' CHECK (format IN ('markdown', 'html', 'plain')),
    version INTEGER DEFAULT 1,
    author_id VARCHAR(20) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Entity Notes Table (Immutable)
-- ----------------------------------------------------------------------------
CREATE TABLE entity_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOT', 'entity_notes_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug')),
    entity_id VARCHAR(20) NOT NULL,
    note_text TEXT NOT NULL,
    is_decision BOOLEAN DEFAULT FALSE NOT NULL,
    decision_status VARCHAR(20) DEFAULT 'Active',
    created_by VARCHAR(20) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ----------------------------------------------------------------------------
-- Audit Logs Table (Immutable)
-- ----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('AUD', 'audit_logs_id_seq'),
    user_id VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    client_id VARCHAR(20) REFERENCES clients(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'VIEW')),
    changes JSONB,
    request_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Entity History Table (Field-level change tracking)
-- ----------------------------------------------------------------------------
CREATE TABLE entity_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('HIS', 'entity_history_id_seq'),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(20) REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Report Snapshots Table
-- ----------------------------------------------------------------------------
CREATE TABLE report_snapshots (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('RPT', 'report_snapshots_id_seq'),
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    parameters JSONB,
    data JSONB NOT NULL,
    generated_by VARCHAR(20) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Sprints Table
-- ----------------------------------------------------------------------------
CREATE TABLE sprints (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SPR', 'sprints_id_seq'),
    project_id VARCHAR(20) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Planning' CHECK (status IN ('Planning', 'Active', 'Completed', 'Cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Sprint Tasks Table (Many-to-many)
-- ----------------------------------------------------------------------------
CREATE TABLE sprint_tasks (
    sprint_id VARCHAR(20) NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (sprint_id, task_id)
);

-- ============================================================================
-- SECTION 5: CONFIGURATION AND SETTINGS TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Company Settings Table
-- ----------------------------------------------------------------------------
CREATE TABLE company_settings (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CMP', 'company_settings_id_seq'),
    client_id VARCHAR(20) NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    company_logo_url VARCHAR(500),
    company_logo_data TEXT,
    primary_color VARCHAR(7) DEFAULT '#4A90E2',
    secondary_color VARCHAR(7) DEFAULT '#2C3E50',
    report_header_text TEXT,
    report_footer_text TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    currency VARCHAR(3) DEFAULT 'USD',
    sprint_length_weeks VARCHAR(10) DEFAULT '2',
    sprint_starting_day VARCHAR(20) DEFAULT 'Monday',
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Organizations Table
-- ----------------------------------------------------------------------------
CREATE TABLE organizations (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('ORG', 'organizations_id_seq'),
    name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    logo_data TEXT,
    description TEXT,
    website VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTION 6: TODO AND NOTES TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Todo Items Table
-- ----------------------------------------------------------------------------
CREATE TABLE todo_items (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TODO', 'todo_items_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    visibility VARCHAR(10) NOT NULL CHECK (visibility IN ('public', 'private')),
    linked_entity_type VARCHAR(20) CHECK (linked_entity_type IN ('task', 'subtask')),
    linked_entity_id VARCHAR(20),
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Adhoc Notes Table
-- ----------------------------------------------------------------------------
CREATE TABLE adhoc_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTE', 'adhoc_notes_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    color VARCHAR(7) DEFAULT '#FFEB3B',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTION 7: CHAT ASSISTANT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Chat Messages Table
-- ----------------------------------------------------------------------------
CREATE TABLE chat_messages (
    id VARCHAR(20) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities JSONB,
    actions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ----------------------------------------------------------------------------
-- Chat Audit Logs Table
-- ----------------------------------------------------------------------------
CREATE TABLE chat_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    session_id VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities_accessed JSONB,
    action_performed VARCHAR(100),
    action_result VARCHAR(20) CHECK (action_result IN ('success', 'failed', 'denied')),
    response_summary TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- ----------------------------------------------------------------------------
-- Reminders Table
-- ----------------------------------------------------------------------------
CREATE TABLE reminders (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('task', 'bug', 'project', 'user_story', 'subtask')),
    entity_id VARCHAR(20) NOT NULL,
    message TEXT,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
    created_via VARCHAR(20) NOT NULL DEFAULT 'chat' CHECK (created_via IN ('chat', 'ui', 'api')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- SECTION 8: TEAM MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Teams Table
-- ----------------------------------------------------------------------------
CREATE TABLE teams (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id VARCHAR(50) REFERENCES projects(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) REFERENCES users(id),
    updated_by VARCHAR(50) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Team Members Table
-- ----------------------------------------------------------------------------
CREATE TABLE team_members (
    id VARCHAR(50) PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100) DEFAULT 'Member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50) REFERENCES users(id),
    CONSTRAINT uk_team_members_unique UNIQUE(team_id, user_id)
);

-- ----------------------------------------------------------------------------
-- Assignments Table
-- ----------------------------------------------------------------------------
CREATE TABLE assignments (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_type VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50) REFERENCES users(id),
    updated_by VARCHAR(50) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Assignment History Table
-- ----------------------------------------------------------------------------
CREATE TABLE assignment_history (
    id VARCHAR(50) PRIMARY KEY,
    assignment_id VARCHAR(50) REFERENCES assignments(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id),
    assignment_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    previous_user_id VARCHAR(50) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) REFERENCES users(id)
);

-- ============================================================================
-- SECTION 9: NOTIFICATION SYSTEM TABLES
-- ============================================================================

-- Create notification enums
CREATE TYPE notification_type AS ENUM (
    'assignment_created',
    'assignment_removed',
    'team_member_added',
    'team_member_removed',
    'assignment_conflict',
    'bulk_assignment_completed',
    'bulk_assignment_failed'
);

CREATE TYPE notification_status AS ENUM (
    'pending',
    'sent',
    'failed',
    'read'
);

CREATE TYPE notification_channel AS ENUM (
    'email',
    'in_app',
    'push'
);

-- ----------------------------------------------------------------------------
-- Notifications Table
-- ----------------------------------------------------------------------------
CREATE TABLE notifications (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTIF', 'notifications_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(20),
    status notification_status NOT NULL DEFAULT 'pending',
    channel notification_channel NOT NULL DEFAULT 'in_app',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id),
    context_data TEXT
);

-- ----------------------------------------------------------------------------
-- Notification Preferences Table
-- ----------------------------------------------------------------------------
CREATE TABLE notification_preferences (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NPREF', 'notification_preferences_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    email_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    push_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Notification History Table
-- ----------------------------------------------------------------------------
CREATE TABLE notification_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NHIST', 'notification_history_id_seq'),
    notification_id VARCHAR(20) NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    status notification_status NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    error_code VARCHAR(50),
    external_id VARCHAR(255)
);

-- ============================================================================
-- SECTION 10: TEST MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Test Runs Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_runs (
    id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(id),
    usecase_id VARCHAR(20) REFERENCES usecases(id),
    user_story_id VARCHAR(20) REFERENCES user_stories(id),
    task_id VARCHAR(20) REFERENCES tasks(id),
    subtask_id VARCHAR(20) REFERENCES subtasks(id),
    name VARCHAR(255) NOT NULL,
    purpose TEXT,
    short_description VARCHAR(500),
    long_description TEXT,
    component_attached_to VARCHAR(255),
    run_type VARCHAR(50) DEFAULT 'Misc',
    status VARCHAR(50) DEFAULT 'In Progress',
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    total_test_cases INTEGER DEFAULT 0,
    passed_test_cases INTEGER DEFAULT 0,
    failed_test_cases INTEGER DEFAULT 0,
    blocked_test_cases INTEGER DEFAULT 0,
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Test Cases Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_cases (
    id VARCHAR(20) PRIMARY KEY,
    test_run_id VARCHAR(20) REFERENCES test_runs(id) NOT NULL,
    test_case_name VARCHAR(255) NOT NULL,
    test_case_description TEXT,
    test_case_steps TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    actual_result TEXT,
    inference TEXT,
    component_attached_to VARCHAR(255),
    remarks TEXT,
    priority VARCHAR(20),
    status VARCHAR(50) DEFAULT 'Not Executed',
    executed_by VARCHAR(20) REFERENCES users(id),
    executed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    updated_by VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Test Executions Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_executions (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) REFERENCES test_cases(id) NOT NULL,
    test_run_id VARCHAR(20) REFERENCES test_runs(id),
    executed_by VARCHAR(20) REFERENCES users(id) NOT NULL,
    execution_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    execution_status VARCHAR(50) NOT NULL,
    actual_result TEXT,
    execution_notes TEXT,
    environment VARCHAR(100),
    browser VARCHAR(50),
    os VARCHAR(50),
    device_type VARCHAR(50),
    screenshots TEXT,
    log_files TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Test Case Bugs Junction Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_case_bugs (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) REFERENCES test_cases(id) NOT NULL,
    bug_id VARCHAR(20) REFERENCES bugs(id) NOT NULL,
    test_execution_id VARCHAR(20) REFERENCES test_executions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL
);

-- ----------------------------------------------------------------------------
-- Test Case Comments Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_case_comments (
    id VARCHAR(20) PRIMARY KEY,
    test_case_id VARCHAR(20) NOT NULL,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL,
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Bug Comments Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_comments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    comment_text TEXT NOT NULL,
    author_id VARCHAR(20) NOT NULL,
    mentioned_users TEXT,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    attachments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Bug Attachments Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_attachments (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by VARCHAR(20) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- ----------------------------------------------------------------------------
-- Bug Status History Table
-- ----------------------------------------------------------------------------
CREATE TABLE bug_status_history (
    id VARCHAR(20) PRIMARY KEY,
    bug_id VARCHAR(20) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    resolution_type VARCHAR(50),
    notes TEXT,
    changed_by VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTION 11: INDEXES
-- ============================================================================

-- Clients indexes
CREATE INDEX idx_clients_is_deleted ON clients(is_deleted);
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_phone ON clients(phone);

-- Users indexes
CREATE INDEX idx_users_client_id ON users(client_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_primary_role ON users(primary_role);
CREATE INDEX idx_users_contact_person ON users(is_contact_person) WHERE is_contact_person = TRUE;
CREATE INDEX idx_users_view_preferences ON users USING GIN (view_preferences);

-- Phases indexes
CREATE INDEX idx_phases_is_active ON phases(is_active);
CREATE INDEX idx_phases_is_deleted ON phases(is_deleted);
CREATE INDEX idx_phases_display_order ON phases(display_order);

-- Programs indexes
CREATE INDEX idx_programs_client_id ON programs(client_id);
CREATE INDEX idx_programs_status ON programs(status);
CREATE INDEX idx_programs_is_deleted ON programs(is_deleted);
CREATE INDEX idx_programs_created_by ON programs(created_by);

-- Projects indexes
CREATE INDEX idx_projects_program_id ON projects(program_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_is_deleted ON projects(is_deleted);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- Usecases indexes
CREATE INDEX idx_usecases_project_id ON usecases(project_id);
CREATE INDEX idx_usecases_status ON usecases(status);
CREATE INDEX idx_usecases_is_deleted ON usecases(is_deleted);
CREATE INDEX idx_usecases_created_by ON usecases(created_by);

-- User Stories indexes
CREATE INDEX idx_user_stories_usecase_id ON user_stories(usecase_id);
CREATE INDEX idx_user_stories_status ON user_stories(status);
CREATE INDEX idx_user_stories_is_deleted ON user_stories(is_deleted);
CREATE INDEX idx_user_stories_created_by ON user_stories(created_by);
CREATE INDEX idx_user_stories_phase_id ON user_stories(phase_id);

-- Tasks indexes
CREATE INDEX idx_tasks_user_story_id ON tasks(user_story_id);
CREATE INDEX idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_is_deleted ON tasks(is_deleted);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_sprint_id ON tasks(sprint_id);

-- Subtasks indexes
CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX idx_subtasks_phase_id ON subtasks(phase_id);
CREATE INDEX idx_subtasks_assigned_to ON subtasks(assigned_to);
CREATE INDEX idx_subtasks_status ON subtasks(status);
CREATE INDEX idx_subtasks_is_deleted ON subtasks(is_deleted);

-- Dependencies indexes
CREATE INDEX idx_dependencies_entity ON dependencies(entity_type, entity_id);
CREATE INDEX idx_dependencies_depends_on ON dependencies(depends_on_type, depends_on_id);

-- Commits indexes
CREATE INDEX idx_commits_task_id ON commits(task_id);
CREATE INDEX idx_commits_hash ON commits(commit_hash);
CREATE INDEX idx_commits_repository ON commits(repository);

-- Pull Requests indexes
CREATE INDEX idx_pull_requests_task_id ON pull_requests(task_id);
CREATE INDEX idx_pull_requests_status ON pull_requests(status);

-- Bugs indexes
CREATE INDEX idx_bugs_entity ON bugs(entity_type, entity_id);
CREATE INDEX idx_bugs_status ON bugs(status);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_priority ON bugs(priority);
CREATE INDEX idx_bugs_assigned_to ON bugs(assigned_to);
CREATE INDEX idx_bugs_reported_by ON bugs(reported_by);
CREATE INDEX idx_bugs_is_deleted ON bugs(is_deleted);
CREATE INDEX idx_bugs_created_at ON bugs(created_at);

-- Documentation indexes
CREATE INDEX idx_documentation_entity ON documentation(entity_type, entity_id);
CREATE INDEX idx_documentation_author_id ON documentation(author_id);

-- Entity Notes indexes
CREATE INDEX idx_entity_notes_entity ON entity_notes(entity_type, entity_id);
CREATE INDEX idx_entity_notes_created_at ON entity_notes(created_at DESC);
CREATE INDEX idx_entity_notes_created_by ON entity_notes(created_by);
CREATE INDEX idx_entity_notes_decisions ON entity_notes(is_decision, decision_status) WHERE is_decision = TRUE;
CREATE INDEX idx_entity_notes_entity_decisions ON entity_notes(entity_type, entity_id, is_decision) WHERE is_decision = TRUE;

-- Audit Logs indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_client_id ON audit_logs(client_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_request_id ON audit_logs(request_id);

-- Entity History indexes
CREATE INDEX idx_entity_history_entity ON entity_history(entity_type, entity_id);
CREATE INDEX idx_entity_history_changed_at ON entity_history(changed_at);
CREATE INDEX idx_entity_history_changed_by ON entity_history(changed_by);
CREATE INDEX idx_entity_history_field_name ON entity_history(field_name);

-- Report Snapshots indexes
CREATE INDEX idx_report_snapshots_type ON report_snapshots(report_type);
CREATE INDEX idx_report_snapshots_generated_by ON report_snapshots(generated_by);

-- Sprints indexes
CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);
CREATE INDEX idx_sprints_status ON sprints(status);

-- Sprint Tasks indexes
CREATE INDEX idx_sprint_tasks_sprint_id ON sprint_tasks(sprint_id);
CREATE INDEX idx_sprint_tasks_task_id ON sprint_tasks(task_id);

-- Company Settings indexes
CREATE INDEX idx_company_settings_client_id ON company_settings(client_id);
CREATE INDEX idx_company_settings_is_active ON company_settings(is_active);

-- Organizations indexes
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);
CREATE INDEX idx_organizations_is_deleted ON organizations(is_deleted);

-- Todo Items indexes
CREATE INDEX idx_todo_items_user_id ON todo_items(user_id);
CREATE INDEX idx_todo_items_target_date ON todo_items(target_date);
CREATE INDEX idx_todo_items_visibility ON todo_items(visibility);
CREATE INDEX idx_todo_items_user_date ON todo_items(user_id, target_date) WHERE is_deleted = false;
CREATE INDEX idx_todo_items_linked_entity ON todo_items(linked_entity_type, linked_entity_id) WHERE linked_entity_id IS NOT NULL;
CREATE INDEX idx_todo_items_is_deleted ON todo_items(is_deleted);

-- Adhoc Notes indexes
CREATE INDEX idx_adhoc_notes_user_id ON adhoc_notes(user_id);
CREATE INDEX idx_adhoc_notes_position ON adhoc_notes(user_id, position) WHERE is_deleted = false;
CREATE INDEX idx_adhoc_notes_is_deleted ON adhoc_notes(is_deleted);

-- Chat Messages indexes
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at);

-- Chat Audit Logs indexes
CREATE INDEX idx_chat_audit_logs_request ON chat_audit_logs(request_id);
CREATE INDEX idx_chat_audit_logs_user ON chat_audit_logs(user_id);
CREATE INDEX idx_chat_audit_logs_client ON chat_audit_logs(client_id);
CREATE INDEX idx_chat_audit_logs_session ON chat_audit_logs(session_id);
CREATE INDEX idx_chat_audit_logs_timestamp ON chat_audit_logs(timestamp);

-- Reminders indexes
CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX idx_reminders_is_sent ON reminders(is_sent);
CREATE INDEX idx_reminders_entity ON reminders(entity_type, entity_id);

-- Teams indexes
CREATE INDEX idx_teams_project ON teams(project_id);
CREATE INDEX idx_teams_active ON teams(is_active);

-- Team Members indexes
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
CREATE INDEX idx_team_members_active ON team_members(is_active);

-- Assignments indexes
CREATE INDEX idx_assignments_entity ON assignments(entity_type, entity_id);
CREATE INDEX idx_assignments_user ON assignments(user_id);
CREATE INDEX idx_assignments_type ON assignments(assignment_type);
CREATE UNIQUE INDEX idx_assignments_unique_user_entity ON assignments(entity_type, entity_id, user_id, assignment_type) WHERE is_active = TRUE;

-- Assignment History indexes
CREATE INDEX idx_assignment_history_entity ON assignment_history(entity_type, entity_id);
CREATE INDEX idx_assignment_history_user ON assignment_history(user_id);
CREATE INDEX idx_assignment_history_date ON assignment_history(created_at);

-- Notifications indexes
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at);
CREATE INDEX idx_notifications_entity ON notifications(entity_type, entity_id);
CREATE INDEX idx_notifications_type_status ON notifications(type, status);

-- Notification Preferences indexes
CREATE UNIQUE INDEX idx_notification_preferences_user_type ON notification_preferences(user_id, notification_type);

-- Notification History indexes
CREATE INDEX idx_notification_history_notification ON notification_history(notification_id);
CREATE INDEX idx_notification_history_status ON notification_history(status, attempted_at);

-- Test Runs indexes
CREATE INDEX idx_test_runs_project ON test_runs(project_id);
CREATE INDEX idx_test_runs_status ON test_runs(status);

-- Test Cases indexes
CREATE INDEX idx_test_cases_run ON test_cases(test_run_id);
CREATE INDEX idx_test_cases_status ON test_cases(status);

-- Test Executions indexes
CREATE INDEX idx_test_executions_case ON test_executions(test_case_id);

-- Bug Comments indexes
CREATE INDEX idx_bug_comments_bug ON bug_comments(bug_id);

-- Bug Attachments indexes
CREATE INDEX idx_bug_attachments_bug ON bug_attachments(bug_id);

-- Bug Status History indexes
CREATE INDEX idx_bug_status_history_bug ON bug_status_history(bug_id);

-- ============================================================================
-- SECTION 12: TRIGGERS
-- ============================================================================

-- Updated_at triggers for all tables
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usecases_updated_at BEFORE UPDATE ON usecases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_stories_updated_at BEFORE UPDATE ON user_stories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subtasks_updated_at BEFORE UPDATE ON subtasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_phases_updated_at BEFORE UPDATE ON phases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bugs_updated_at BEFORE UPDATE ON bugs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pull_requests_updated_at BEFORE UPDATE ON pull_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documentation_updated_at BEFORE UPDATE ON documentation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sprints_updated_at BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todo_items_updated_at BEFORE UPDATE ON todo_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adhoc_notes_updated_at BEFORE UPDATE ON adhoc_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Immutability triggers for entity_notes
CREATE TRIGGER prevent_entity_notes_update
    BEFORE UPDATE ON entity_notes
    FOR EACH ROW
    EXECUTE FUNCTION prevent_note_modification();

CREATE TRIGGER prevent_entity_notes_delete
    BEFORE DELETE ON entity_notes
    FOR EACH ROW
    EXECUTE FUNCTION prevent_note_modification();

-- Notification preferences triggers
CREATE TRIGGER trigger_create_default_notification_preferences
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_notification_preferences();

CREATE TRIGGER trigger_update_notification_preferences_timestamp
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_preferences_timestamp();

-- ============================================================================
-- SECTION 13: VIEWS
-- ============================================================================

-- Recent Entity Notes View
CREATE OR REPLACE VIEW recent_entity_notes AS
SELECT 
    n.id,
    n.entity_type,
    n.entity_id,
    n.note_text,
    n.created_at,
    u.full_name as created_by_name,
    u.email as created_by_email
FROM entity_notes n
JOIN users u ON n.created_by = u.id
ORDER BY n.created_at DESC;

-- ============================================================================
-- SECTION 14: DEFAULT DATA
-- ============================================================================

-- Insert default phases
INSERT INTO phases (name, short_description, color, display_order) VALUES
('Development', 'Software development and coding tasks', '#3498db', 1),
('Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2),
('Design', 'UI/UX and architecture design tasks', '#e67e22', 3),
('Testing', 'Quality assurance and testing tasks', '#1abc9c', 4)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- SECTION 15: COMMENTS AND DOCUMENTATION
-- ============================================================================

-- Table comments
COMMENT ON TABLE clients IS 'Client organizations';
COMMENT ON TABLE users IS 'System users with authentication and role management';
COMMENT ON TABLE phases IS 'Work phases for categorizing tasks and subtasks';
COMMENT ON TABLE programs IS 'Programs belonging to clients';
COMMENT ON TABLE projects IS 'Projects within programs';
COMMENT ON TABLE usecases IS 'Use cases within projects';
COMMENT ON TABLE user_stories IS 'User stories within use cases';
COMMENT ON TABLE tasks IS 'Tasks within user stories';
COMMENT ON TABLE subtasks IS 'Subtasks within tasks';
COMMENT ON TABLE bugs IS 'Bug tracking with comprehensive QA fields';
COMMENT ON TABLE entity_notes IS 'Immutable notes attached to any entity. Notes cannot be edited or deleted.';
COMMENT ON TABLE audit_logs IS 'Immutable audit log table. Records should never be updated or deleted. Retention policy: 7 years minimum.';
COMMENT ON TABLE entity_history IS 'Field-level change tracking for all entities. Provides detailed audit trail of what changed, when, and by whom.';
COMMENT ON TABLE sprints IS 'Sprint management for agile development';
COMMENT ON TABLE company_settings IS 'Company branding and settings per client. Only one row per client.';
COMMENT ON TABLE organizations IS 'Organizations table for managing company/organization information with full CRUD operations';
COMMENT ON TABLE todo_items IS 'Personal TODO items for users with optional links to tasks/subtasks';
COMMENT ON TABLE adhoc_notes IS 'Standalone sticky notes for quick capture of thoughts and reminders';
COMMENT ON TABLE chat_messages IS 'Stores chat conversation messages between users and the assistant';
COMMENT ON TABLE chat_audit_logs IS 'Audit trail for all chat interactions and actions performed';
COMMENT ON TABLE reminders IS 'User reminders created via chat or other interfaces';
COMMENT ON TABLE teams IS 'Teams for project management';
COMMENT ON TABLE assignments IS 'Entity-user assignments for ownership and contact person roles';
COMMENT ON TABLE notifications IS 'User notifications for various system events';
COMMENT ON TABLE notification_preferences IS 'User preferences for notification types and channels';
COMMENT ON TABLE test_runs IS 'Test run executions';
COMMENT ON TABLE test_cases IS 'Individual test cases';
COMMENT ON TABLE test_executions IS 'Execution records for test cases';
COMMENT ON TABLE bug_comments IS 'Comments on bugs';
COMMENT ON TABLE bug_attachments IS 'File attachments for bugs';
COMMENT ON TABLE bug_status_history IS 'History of bug status changes';

-- Column comments for users table
COMMENT ON COLUMN users.role IS 'User role determines permissions: Admin (full access), Architect (programs/projects/usecases/stories), Designer (usecases/stories), Developer (tasks/subtasks/bugs), Tester (bugs)';
COMMENT ON COLUMN users.primary_role IS 'Primary role of the user for assignment purposes';
COMMENT ON COLUMN users.secondary_roles IS 'Array of additional roles the user can perform';
COMMENT ON COLUMN users.is_contact_person IS 'Flag indicating if user can be assigned as client contact person';
COMMENT ON COLUMN users.view_preferences IS 'User UI preferences stored as JSON. Includes defaultView (tile/list) and per-entity view preferences.';

-- Column comments for subtasks
COMMENT ON COLUMN subtasks.created_by IS 'User ID who created the subtask (string, not FK)';
COMMENT ON COLUMN subtasks.updated_by IS 'User ID who last updated the subtask (string, not FK)';
COMMENT ON COLUMN subtasks.phase_id IS 'Optional phase ID for subtask (nullable)';
COMMENT ON COLUMN subtasks.duration_days IS 'Expected duration in days for this subtask';
COMMENT ON COLUMN subtasks.scrum_points IS 'Scrum story points assigned to this subtask';

-- Column comments for entity_notes
COMMENT ON COLUMN entity_notes.is_decision IS 'Flag to indicate if this note is a decision';
COMMENT ON COLUMN entity_notes.decision_status IS 'Status of the decision: Active, Canceled, Postponed, On-Hold, Closed';

-- Column comments for clients
COMMENT ON COLUMN clients.email IS 'Primary contact email for the client organization';
COMMENT ON COLUMN clients.phone IS 'Primary contact phone number for the client organization';

-- Column comments for projects
COMMENT ON COLUMN projects.sprint_length_weeks IS 'Sprint length in weeks: "1" or "2"';
COMMENT ON COLUMN projects.sprint_starting_day IS 'Day of week when sprints start: Monday, Tuesday, Wednesday, etc.';

-- Column comments for company_settings
COMMENT ON COLUMN company_settings.company_logo_url IS 'URL to company logo image (e.g., S3, CDN, or local path)';
COMMENT ON COLUMN company_settings.company_logo_data IS 'Base64 encoded logo image data for embedded storage';
COMMENT ON COLUMN company_settings.sprint_length_weeks IS 'Sprint length in weeks: "1" or "2"';
COMMENT ON COLUMN company_settings.sprint_starting_day IS 'Day of week when sprints start: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday';

-- Column comments for user_stories
COMMENT ON COLUMN user_stories.phase_id IS 'Category: Status & Priority | Work phase (required: Development, Analysis, Design, Testing)';

-- View comments
COMMENT ON VIEW recent_entity_notes IS 'View showing all notes with user details, ordered by most recent first';

-- ============================================================================
-- END OF BASELINE SCHEMA
-- ============================================================================





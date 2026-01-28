-- ============================================================================
-- Worky Database - CORRECTED Baseline Schema
-- ============================================================================
-- This file contains the corrected baseline schema that matches the current
-- API schemas and UI types as of 2026-01-22
-- 
-- Key Corrections:
-- - All IDs are VARCHAR(20) with string format (CLI-000001, USR-000001, etc.)
-- - Status values match API validation: Planning, In Progress, Completed, etc.
-- - All fields from API schemas and UI types are included
-- - Foreign key constraints are properly ordered
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
CREATE SEQUENCE IF NOT EXISTS dependencies_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS commits_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS pull_requests_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS documentation_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS report_snapshots_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_runs_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_cases_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_executions_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_case_bugs_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS test_case_comments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bug_comments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bug_attachments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bug_status_history_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS teams_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS team_members_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS assignments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS assignment_history_id_seq START 1;

-- ============================================================================
-- SECTION 3: CORE ENTITY TABLES (Ordered to avoid FK conflicts)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Clients Table (First - no dependencies)
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
    created_by VARCHAR(20),
    updated_by VARCHAR(20)
);

-- ----------------------------------------------------------------------------
-- Users Table (Second - depends on clients)
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
-- Phases Table (Third - no dependencies on other entities)
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
-- Sprints Table (Must come before tasks that reference it)
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
    phase_id VARCHAR(20) REFERENCES phases(id),
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Tasks Table (CORRECTED with all fields from API schema)
-- ----------------------------------------------------------------------------
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TSK', 'tasks_id_seq'),
    user_story_id VARCHAR(20) NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    phase_id VARCHAR(20) REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'Planning' CHECK (status IN ('Planning', 'In Progress', 'Completed', 'Blocked', 'In Review', 'On-Hold', 'Canceled')),
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
-- Subtasks Table (CORRECTED with all fields from API schema)
-- ----------------------------------------------------------------------------
CREATE TABLE subtasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SUB', 'subtasks_id_seq'),
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    phase_id VARCHAR(20) REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'Planning' CHECK (status IN ('Planning', 'In Progress', 'Completed', 'Blocked', 'In Review', 'On-Hold', 'Canceled')),
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    duration_days INTEGER,
    scrum_points NUMERIC(5, 2),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Add foreign key constraints for clients table (circular dependency resolution)
ALTER TABLE clients ADD CONSTRAINT fk_clients_created_by FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE clients ADD CONSTRAINT fk_clients_updated_by FOREIGN KEY (updated_by) REFERENCES users(id);

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
    test_run_id VARCHAR(20),
    test_case_id VARCHAR(20),
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
-- Sprint Tasks Table (Many-to-many)
-- ----------------------------------------------------------------------------
CREATE TABLE sprint_tasks (
    sprint_id VARCHAR(20) NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (sprint_id, task_id)
);

-- ============================================================================
-- SECTION 5: DEFAULT DATA
-- ============================================================================

-- Insert default phases (matching API expectations)
INSERT INTO phases (name, short_description, color, display_order) VALUES
('Development', 'Software development and coding tasks', '#3498db', 1),
('Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2),
('Design', 'UI/UX and architecture design tasks', '#e67e22', 3),
('Testing', 'Quality assurance and testing tasks', '#1abc9c', 4)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- SECTION 6: INDEXES FOR PERFORMANCE
-- ============================================================================

-- Core entity indexes
CREATE INDEX idx_clients_is_deleted ON clients(is_deleted);
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_users_client_id ON users(client_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_phases_is_active ON phases(is_active);
CREATE INDEX idx_programs_client_id ON programs(client_id);
CREATE INDEX idx_projects_program_id ON projects(program_id);
CREATE INDEX idx_usecases_project_id ON usecases(project_id);
CREATE INDEX idx_user_stories_usecase_id ON user_stories(usecase_id);
CREATE INDEX idx_tasks_user_story_id ON tasks(user_story_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_sprint_id ON tasks(sprint_id);
CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX idx_subtasks_assigned_to ON subtasks(assigned_to);
CREATE INDEX idx_subtasks_status ON subtasks(status);
CREATE INDEX idx_bugs_entity ON bugs(entity_type, entity_id);
CREATE INDEX idx_bugs_status ON bugs(status);
CREATE INDEX idx_bugs_assigned_to ON bugs(assigned_to);
CREATE INDEX idx_sprints_project_id ON sprints(project_id);

-- ============================================================================
-- SECTION 7: TRIGGERS
-- ============================================================================

-- Updated_at triggers for all main tables
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

CREATE TRIGGER update_sprints_updated_at BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SECTION 8: COMMENTS AND DOCUMENTATION
-- ============================================================================

-- Table comments
COMMENT ON TABLE clients IS 'Client organizations with contact information';
COMMENT ON TABLE users IS 'System users with authentication, roles, and preferences';
COMMENT ON TABLE phases IS 'Work phases for categorizing tasks and subtasks';
COMMENT ON TABLE programs IS 'Programs belonging to clients';
COMMENT ON TABLE projects IS 'Projects within programs with sprint configuration';
COMMENT ON TABLE usecases IS 'Use cases within projects';
COMMENT ON TABLE user_stories IS 'User stories within use cases';
COMMENT ON TABLE tasks IS 'Tasks within user stories with sprint assignment';
COMMENT ON TABLE subtasks IS 'Subtasks within tasks with duration and scrum points';
COMMENT ON TABLE bugs IS 'Bug tracking with comprehensive QA fields';
COMMENT ON TABLE sprints IS 'Sprint management for agile development';

-- Column comments for key fields
COMMENT ON COLUMN users.role IS 'User role: Admin, Developer, Tester, Architect, Designer';
COMMENT ON COLUMN users.view_preferences IS 'User UI preferences stored as JSON';
COMMENT ON COLUMN tasks.status IS 'Task status: Planning, In Progress, Completed, Blocked, In Review, On-Hold, Canceled';
COMMENT ON COLUMN subtasks.status IS 'Subtask status: Planning, In Progress, Completed, Blocked, In Review, On-Hold, Canceled';
COMMENT ON COLUMN subtasks.duration_days IS 'Expected duration in days for this subtask';
COMMENT ON COLUMN subtasks.scrum_points IS 'Scrum story points assigned to this subtask';

-- ============================================================================
-- SECTION 9: DEFAULT DATA CREATION
-- ============================================================================

-- Create default client for admin access
INSERT INTO clients (
    id, 
    name, 
    short_description, 
    email, 
    is_active, 
    created_at, 
    updated_at
) VALUES (
    'CLI-000001',
    'DataLegos',
    'Default client for admin access',
    'admin@datalegos.com',
    true,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Create default admin user
-- Password: "password" (proper bcrypt hash with salt rounds=12)
INSERT INTO users (
    id, 
    email, 
    hashed_password, 
    full_name, 
    role, 
    primary_role,
    client_id,
    is_active, 
    created_at, 
    updated_at
) VALUES (
    'USR-000001',
    'admin@datalegos.com',
    '$2b$12$LdKRRuZSyld/dzgpaGWKpuJqwAwIHKNOdZ79uc8931I3kZHZ.ScRa',
    'Admin User',
    'Admin',
    'Admin',
    'CLI-000001',
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    hashed_password = '$2b$12$LdKRRuZSyld/dzgpaGWKpuJqwAwIHKNOdZ79uc8931I3kZHZ.ScRa',
    updated_at = NOW();

-- Create default phases
INSERT INTO phases (id, name, short_description, color, display_order, is_active) VALUES
    ('PHS-000001', 'Planning', 'Initial planning and design phase', '#6B7280', 1, true),
    ('PHS-000002', 'Development', 'Active development phase', '#3B82F6', 2, true),
    ('PHS-000003', 'Testing', 'Quality assurance and testing phase', '#F59E0B', 3, true),
    ('PHS-000004', 'Deployment', 'Deployment and release phase', '#10B981', 4, true),
    ('PHS-000005', 'Maintenance', 'Post-deployment maintenance phase', '#8B5CF6', 5, true)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- END OF CORRECTED BASELINE SCHEMA
-- ============================================================================
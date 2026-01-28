-- ============================================================================
-- Worky Database - Extended Features Schema
-- ============================================================================
-- This file contains additional tables for extended features:
-- - Audit logging and entity history
-- - Notification system
-- - Test management
-- - Team management
-- - Chat assistant
-- - TODO and notes
-- - Company settings and organizations
-- ============================================================================

-- Create sequences for extended features
CREATE SEQUENCE IF NOT EXISTS chat_audit_logs_id_seq START 1;

-- ============================================================================
-- SECTION 1: AUDIT AND HISTORY TABLES
-- ============================================================================

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

-- ============================================================================
-- SECTION 2: NOTIFICATION SYSTEM
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
    user_id VARCHAR(20) REFERENCES users(id) ON DELETE CASCADE,
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
-- SECTION 3: TEST MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Test Runs Table
-- ----------------------------------------------------------------------------
CREATE TABLE test_runs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TR', 'test_runs_id_seq'),
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
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TC', 'test_cases_id_seq'),
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
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TE', 'test_executions_id_seq'),
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
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TCB', 'test_case_bugs_id_seq'),
    test_case_id VARCHAR(20) REFERENCES test_cases(id) NOT NULL,
    bug_id VARCHAR(20) REFERENCES bugs(id) NOT NULL,
    test_execution_id VARCHAR(20) REFERENCES test_executions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id) NOT NULL
);

-- Add foreign key constraints for test_runs references in bugs table
ALTER TABLE bugs ADD CONSTRAINT fk_bugs_test_run_id FOREIGN KEY (test_run_id) REFERENCES test_runs(id);
ALTER TABLE bugs ADD CONSTRAINT fk_bugs_test_case_id FOREIGN KEY (test_case_id) REFERENCES test_cases(id);

-- ============================================================================
-- SECTION 4: TEAM MANAGEMENT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Teams Table
-- ----------------------------------------------------------------------------
CREATE TABLE teams (
    id VARCHAR(50) PRIMARY KEY DEFAULT generate_string_id('TEAM', 'teams_id_seq'),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id VARCHAR(20) REFERENCES projects(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Team Members Table
-- ----------------------------------------------------------------------------
CREATE TABLE team_members (
    id VARCHAR(50) PRIMARY KEY DEFAULT generate_string_id('TM', 'team_members_id_seq'),
    team_id VARCHAR(20) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100) DEFAULT 'Member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(20) REFERENCES users(id),
    CONSTRAINT uk_team_members_unique UNIQUE(team_id, user_id)
);

-- ----------------------------------------------------------------------------
-- Assignments Table
-- ----------------------------------------------------------------------------
CREATE TABLE assignments (
    id VARCHAR(50) PRIMARY KEY DEFAULT generate_string_id('ASSIGN', 'assignments_id_seq'),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_type VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- ----------------------------------------------------------------------------
-- Assignment History Table
-- ----------------------------------------------------------------------------
CREATE TABLE assignment_history (
    id VARCHAR(50) PRIMARY KEY DEFAULT generate_string_id('AH', 'assignment_history_id_seq'),
    assignment_id VARCHAR(50) REFERENCES assignments(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id),
    assignment_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    previous_user_id VARCHAR(20) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(20) REFERENCES users(id)
);

-- ============================================================================
-- SECTION 5: CHAT ASSISTANT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Chat Messages Table
-- ----------------------------------------------------------------------------
CREATE TABLE chat_messages (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CHAT', 'chat_messages_id_seq'),
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
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CAL', 'chat_audit_logs_id_seq'),
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
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('REM', 'reminders_id_seq'),
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
-- SECTION 7: CONFIGURATION AND SETTINGS TABLES
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

-- ============================================================================
-- SECTION 8: ADDITIONAL INDEXES
-- ============================================================================

-- Audit and history indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_entity_history_entity ON entity_history(entity_type, entity_id);
CREATE INDEX idx_entity_notes_entity ON entity_notes(entity_type, entity_id);

-- Notification indexes
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX idx_notification_preferences_user_type ON notification_preferences(user_id, notification_type);

-- Test management indexes
CREATE INDEX idx_test_runs_project ON test_runs(project_id);
CREATE INDEX idx_test_cases_run ON test_cases(test_run_id);
CREATE INDEX idx_test_executions_case ON test_executions(test_case_id);

-- Team management indexes
CREATE INDEX idx_teams_project ON teams(project_id);
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
CREATE INDEX idx_assignments_entity ON assignments(entity_type, entity_id);
CREATE INDEX idx_assignments_user ON assignments(user_id);

-- Chat and reminders indexes
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);

-- TODO and notes indexes
CREATE INDEX idx_todo_items_user_date ON todo_items(user_id, target_date);
CREATE INDEX idx_adhoc_notes_user ON adhoc_notes(user_id);

-- Settings indexes
CREATE INDEX idx_company_settings_client_id ON company_settings(client_id);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);

-- ============================================================================
-- SECTION 9: ADDITIONAL TRIGGERS
-- ============================================================================

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

-- Updated_at triggers for extended tables
CREATE TRIGGER update_test_runs_updated_at BEFORE UPDATE ON test_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todo_items_updated_at BEFORE UPDATE ON todo_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adhoc_notes_updated_at BEFORE UPDATE ON adhoc_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SECTION 10: VIEWS
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
-- SECTION 11: COMMENTS
-- ============================================================================

-- Extended table comments
COMMENT ON TABLE audit_logs IS 'Immutable audit log table. Records should never be updated or deleted. Retention policy: 7 years minimum.';
COMMENT ON TABLE entity_history IS 'Field-level change tracking for all entities. Provides detailed audit trail of what changed, when, and by whom.';
COMMENT ON TABLE entity_notes IS 'Immutable notes attached to any entity. Notes cannot be edited or deleted.';
COMMENT ON TABLE notifications IS 'User notifications for various system events';
COMMENT ON TABLE test_runs IS 'Test run executions with metrics tracking';
COMMENT ON TABLE test_cases IS 'Individual test cases within test runs';
COMMENT ON TABLE teams IS 'Teams for project management and collaboration';
COMMENT ON TABLE chat_messages IS 'Stores chat conversation messages between users and the assistant';
COMMENT ON TABLE todo_items IS 'Personal TODO items for users with optional links to tasks/subtasks';
COMMENT ON TABLE company_settings IS 'Company branding and settings per client. Only one row per client.';
COMMENT ON TABLE organizations IS 'Organizations table for managing company/organization information with full CRUD operations';

-- ============================================================================
-- END OF EXTENDED FEATURES SCHEMA
-- ============================================================================
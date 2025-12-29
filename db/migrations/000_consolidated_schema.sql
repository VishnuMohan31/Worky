-- =====================================================
-- WORKY DATABASE - CONSOLIDATED SCHEMA
-- =====================================================
-- This is a single consolidated schema file that creates
-- the complete database structure for fresh installations.
-- 
-- Run this file on a fresh PostgreSQL database.
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- SECTION 1: CREATE SEQUENCES (must be first)
-- =====================================================
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
CREATE SEQUENCE IF NOT EXISTS organizations_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS teams_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS team_members_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS assignments_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS assignment_history_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notifications_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_preferences_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_history_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS decisions_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS todo_items_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS adhoc_notes_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS reminders_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS chat_messages_id_seq START 1;

-- =====================================================
-- SECTION 2: CREATE HELPER FUNCTIONS
-- =====================================================

-- Function to generate string IDs with prefix
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

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SECTION 3: CREATE TABLES (in dependency order)
-- =====================================================

-- CLIENTS table (no dependencies)
CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CLI', 'clients_id_seq'),
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_by VARCHAR(20),
    updated_by VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- USERS table (depends on clients)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('USR', 'users_id_seq'),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    primary_role VARCHAR(50) DEFAULT 'Developer',
    secondary_roles TEXT[],
    is_contact_person BOOLEAN DEFAULT FALSE,
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(50) DEFAULT 'snow',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PHASES table (no dependencies)
CREATE TABLE IF NOT EXISTS phases (
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

-- PROGRAMS table (depends on clients)
CREATE TABLE IF NOT EXISTS programs (
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

-- PROJECTS table (depends on programs)
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PRJ', 'projects_id_seq'),
    program_id VARCHAR(20) NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planning',
    repository_url VARCHAR(500),
    sprint_length_weeks VARCHAR(10) DEFAULT '2',
    sprint_starting_day VARCHAR(20) DEFAULT 'Monday',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- USECASES table (depends on projects)
CREATE TABLE IF NOT EXISTS usecases (
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

-- SPRINTS table (depends on projects)
CREATE TABLE IF NOT EXISTS sprints (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SPR', 'sprints_id_seq'),
    project_id VARCHAR(20) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Planning',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- USER_STORIES table (depends on usecases, phases)
CREATE TABLE IF NOT EXISTS user_stories (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('UST', 'user_stories_id_seq'),
    usecase_id VARCHAR(20) NOT NULL REFERENCES usecases(id) ON DELETE CASCADE,
    phase_id VARCHAR(20) REFERENCES phases(id),
    title VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    acceptance_criteria TEXT,
    story_points INTEGER,
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Backlog',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- TASKS table (depends on user_stories, phases, users, sprints)
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TSK', 'tasks_id_seq'),
    user_story_id VARCHAR(20) NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    phase_id VARCHAR(20) REFERENCES phases(id),
    title VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    status VARCHAR(50) DEFAULT 'To Do',
    priority VARCHAR(20) DEFAULT 'Medium',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    sprint_id VARCHAR(20) REFERENCES sprints(id),
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    start_date DATE,
    due_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- SUBTASKS table (depends on tasks, phases, users)
CREATE TABLE IF NOT EXISTS subtasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SUB', 'subtasks_id_seq'),
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    phase_id VARCHAR(20) REFERENCES phases(id),
    title VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    status VARCHAR(50) DEFAULT 'To Do',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    duration_days INTEGER,
    scrum_points DECIMAL(5, 2),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- BUGS table
CREATE TABLE IF NOT EXISTS bugs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BUG', 'bugs_id_seq'),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description VARCHAR(500),
    long_description TEXT,
    severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
    priority VARCHAR(20) NOT NULL DEFAULT 'P2',
    status VARCHAR(50) DEFAULT 'New',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    reported_by VARCHAR(20) NOT NULL REFERENCES users(id),
    resolution_notes TEXT,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- TEAMS table (depends on projects)
CREATE TABLE IF NOT EXISTS teams (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id VARCHAR(50), -- Nullable: teams can exist without project
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    CONSTRAINT fk_teams_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_teams_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_teams_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- TEAM_MEMBERS table (depends on teams, users)
CREATE TABLE IF NOT EXISTS team_members (
    id VARCHAR(50) PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(100) DEFAULT 'Member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    CONSTRAINT fk_team_members_team FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    CONSTRAINT fk_team_members_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_team_members_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT uk_team_members_unique UNIQUE(team_id, user_id)
);

-- ASSIGNMENTS table
CREATE TABLE IF NOT EXISTS assignments (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    CONSTRAINT fk_assignments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignments_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_assignments_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- ASSIGNMENT_HISTORY table
CREATE TABLE IF NOT EXISTS assignment_history (
    id VARCHAR(50) PRIMARY KEY,
    assignment_id VARCHAR(50),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    previous_user_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    CONSTRAINT fk_assignment_history_assignment FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE SET NULL,
    CONSTRAINT fk_assignment_history_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_assignment_history_previous_user FOREIGN KEY (previous_user_id) REFERENCES users(id),
    CONSTRAINT fk_assignment_history_created_by FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ENTITY_NOTES table
CREATE TABLE IF NOT EXISTS entity_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOT', 'entity_notes_id_seq'),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    note_text TEXT NOT NULL,
    created_by VARCHAR(20) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- AUDIT_LOGS table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('AUD', 'audit_logs_id_seq'),
    user_id VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    client_id VARCHAR(20) REFERENCES clients(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL,
    changes JSONB,
    request_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ENTITY_HISTORY table
CREATE TABLE IF NOT EXISTS entity_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('HIS', 'entity_history_id_seq'),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(20) REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ORGANIZATIONS table
CREATE TABLE IF NOT EXISTS organizations (
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
    created_by VARCHAR(20),
    updated_by VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TODO_ITEMS table
CREATE TABLE IF NOT EXISTS todo_items (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TODO', 'todo_items_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    visibility VARCHAR(10) NOT NULL DEFAULT 'private',
    linked_entity_type VARCHAR(20),
    linked_entity_id VARCHAR(20),
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_visibility CHECK (visibility IN ('public', 'private')),
    CONSTRAINT check_entity_type CHECK (linked_entity_type IN ('task', 'subtask') OR linked_entity_type IS NULL)
);

-- ADHOC_NOTES table
CREATE TABLE IF NOT EXISTS adhoc_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTE', 'adhoc_notes_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    color VARCHAR(7) DEFAULT '#FFEB3B',
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_position_positive CHECK (position >= 0)
);

-- REMINDERS table
CREATE TABLE IF NOT EXISTS reminders (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('REM', 'reminders_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    message TEXT,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_sent BOOLEAN DEFAULT false,
    created_via VARCHAR(20) DEFAULT 'chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CHAT tables
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('MSG', 'chat_messages_id_seq'),
    session_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities JSONB,
    actions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    session_id VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities_accessed JSONB,
    action_performed VARCHAR(100),
    action_result VARCHAR(20),
    response_summary TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- SPRINT_TASKS junction table
CREATE TABLE IF NOT EXISTS sprint_tasks (
    id VARCHAR(50) PRIMARY KEY,
    sprint_id VARCHAR(20) NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by VARCHAR(20) REFERENCES users(id),
    UNIQUE(sprint_id, task_id)
);

-- Create notification enums
DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM (
        'assignment_created', 'assignment_removed', 'team_member_added', 
        'team_member_removed', 'assignment_conflict', 'bulk_assignment_completed', 
        'bulk_assignment_failed'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'failed', 'read');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_channel AS ENUM ('email', 'in_app', 'push');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- NOTIFICATIONS table
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTIF', 'notifications_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(20),
    status notification_status DEFAULT 'pending' NOT NULL,
    channel notification_channel DEFAULT 'in_app' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id),
    context_data TEXT
);

-- NOTIFICATION_PREFERENCES table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NPREF', 'notification_preferences_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    email_enabled BOOLEAN DEFAULT true NOT NULL,
    in_app_enabled BOOLEAN DEFAULT true NOT NULL,
    push_enabled BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- NOTIFICATION_HISTORY table
CREATE TABLE IF NOT EXISTS notification_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NHIST', 'notification_history_id_seq'),
    notification_id VARCHAR(20) NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    status notification_status NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    error_code VARCHAR(50),
    external_id VARCHAR(255)
);

-- DECISIONS table
CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    decision_date DATE,
    decision_maker VARCHAR(20) REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    impact VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- =====================================================
-- SECTION 4: CREATE INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_users_client_id ON users(client_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_primary_role ON users(primary_role);

CREATE INDEX IF NOT EXISTS idx_clients_is_deleted ON clients(is_deleted);
CREATE INDEX IF NOT EXISTS idx_programs_client_id ON programs(client_id);
CREATE INDEX IF NOT EXISTS idx_programs_status ON programs(status);
CREATE INDEX IF NOT EXISTS idx_programs_is_deleted ON programs(is_deleted);

CREATE INDEX IF NOT EXISTS idx_projects_program_id ON projects(program_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_is_deleted ON projects(is_deleted);

CREATE INDEX IF NOT EXISTS idx_usecases_project_id ON usecases(project_id);
CREATE INDEX IF NOT EXISTS idx_usecases_status ON usecases(status);
CREATE INDEX IF NOT EXISTS idx_usecases_is_deleted ON usecases(is_deleted);

CREATE INDEX IF NOT EXISTS idx_user_stories_usecase_id ON user_stories(usecase_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_status ON user_stories(status);
CREATE INDEX IF NOT EXISTS idx_user_stories_is_deleted ON user_stories(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_stories_phase_id ON user_stories(phase_id);

CREATE INDEX IF NOT EXISTS idx_tasks_user_story_id ON tasks(user_story_id);
CREATE INDEX IF NOT EXISTS idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_is_deleted ON tasks(is_deleted);
CREATE INDEX IF NOT EXISTS idx_tasks_sprint_id ON tasks(sprint_id);

CREATE INDEX IF NOT EXISTS idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_phase_id ON subtasks(phase_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_assigned_to ON subtasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_subtasks_status ON subtasks(status);
CREATE INDEX IF NOT EXISTS idx_subtasks_is_deleted ON subtasks(is_deleted);

CREATE INDEX IF NOT EXISTS idx_bugs_entity ON bugs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status);
CREATE INDEX IF NOT EXISTS idx_bugs_assigned_to ON bugs(assigned_to);
CREATE INDEX IF NOT EXISTS idx_bugs_is_deleted ON bugs(is_deleted);

CREATE INDEX IF NOT EXISTS idx_teams_project ON teams(project_id);
CREATE INDEX IF NOT EXISTS idx_teams_active ON teams(is_active);
CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_active ON team_members(is_active);

CREATE INDEX IF NOT EXISTS idx_assignments_entity ON assignments(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user ON assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_type ON assignments(assignment_type);

CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_unique_user_entity 
ON assignments(entity_type, entity_id, user_id, assignment_type) 
WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_assignment_history_entity ON assignment_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_assignment_history_user ON assignment_history(user_id);

CREATE INDEX IF NOT EXISTS idx_entity_notes_entity ON entity_notes(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_notes_created_at ON entity_notes(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_entity ON notifications(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_notification_history_notification ON notification_history(notification_id);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user_type ON notification_preferences(user_id, notification_type);

CREATE INDEX IF NOT EXISTS idx_sprints_project ON sprints(project_id);
CREATE INDEX IF NOT EXISTS idx_sprints_status ON sprints(status);

-- =====================================================
-- SECTION 5: CREATE TRIGGERS
-- =====================================================

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

-- =====================================================
-- SECTION 6: INSERT DEFAULT DATA
-- =====================================================

-- Insert default phases
INSERT INTO phases (id, name, short_description, color, display_order, is_active) VALUES
    ('PHS-000001', 'Development', 'Software development and coding tasks', '#3498db', 1, true),
    ('PHS-000002', 'Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2, true),
    ('PHS-000003', 'Design', 'UI/UX and architecture design tasks', '#e67e22', 3, true),
    ('PHS-000004', 'Testing', 'Quality assurance and testing tasks', '#1abc9c', 4, true)
ON CONFLICT (id) DO NOTHING;

-- Update sequences to start after default data
SELECT setval('phases_id_seq', 5, false);

-- =====================================================
-- SECTION 7: SEED DATA (Development Only)
-- =====================================================

-- Insert default client
INSERT INTO clients (id, name, short_description, is_active) VALUES
    ('CLI-000001', 'DataLegos', 'Default development client', true)
ON CONFLICT (id) DO NOTHING;

-- Insert default admin user (password: password)
INSERT INTO users (id, email, hashed_password, full_name, role, primary_role, client_id, is_active) VALUES
    ('USR-000001', 'admin@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G8n4M8y4Y8y4Y8', 'Admin User', 'Admin', 'Admin', 'CLI-000001', true)
ON CONFLICT (id) DO NOTHING;

-- Update sequences
SELECT setval('clients_id_seq', 2, false);
SELECT setval('users_id_seq', 2, false);

-- =====================================================
-- COMPLETED
-- =====================================================
DO $$ BEGIN RAISE NOTICE 'Consolidated schema created successfully!'; END $$;


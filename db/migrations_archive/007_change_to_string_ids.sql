-- Worky Database Schema - Migration 007
-- Version: 007
-- Description: Change from UUID to string-based integer IDs for all tables

-- This migration converts all UUID primary keys to VARCHAR with auto-incrementing integers
-- Format: entity_type prefix + zero-padded number (e.g., CLI-0001, PRG-0001, PRJ-0001)

-- Create sequences for each entity type
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

-- Create function to generate string IDs
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

-- Note: This migration requires dropping and recreating tables with data preservation
-- For production, this would need a more careful migration strategy
-- For development, we'll create new schema

-- Drop existing foreign key constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_client_id_fkey;
ALTER TABLE programs DROP CONSTRAINT IF EXISTS programs_client_id_fkey;
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_program_id_fkey;
ALTER TABLE usecases DROP CONSTRAINT IF EXISTS usecases_project_id_fkey;
ALTER TABLE user_stories DROP CONSTRAINT IF EXISTS user_stories_usecase_id_fkey;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_user_story_id_fkey;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_assigned_to_fkey;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_phase_id_fkey;
ALTER TABLE subtasks DROP CONSTRAINT IF EXISTS subtasks_task_id_fkey;
ALTER TABLE subtasks DROP CONSTRAINT IF EXISTS subtasks_assigned_to_fkey;
ALTER TABLE subtasks DROP CONSTRAINT IF EXISTS subtasks_phase_id_fkey;
ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_assigned_to_fkey;
ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_reported_by_fkey;

-- Backup existing data (if any)
CREATE TABLE IF NOT EXISTS _backup_clients AS SELECT * FROM clients;
CREATE TABLE IF NOT EXISTS _backup_users AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS _backup_programs AS SELECT * FROM programs;
CREATE TABLE IF NOT EXISTS _backup_projects AS SELECT * FROM projects;
CREATE TABLE IF NOT EXISTS _backup_usecases AS SELECT * FROM usecases;
CREATE TABLE IF NOT EXISTS _backup_user_stories AS SELECT * FROM user_stories;
CREATE TABLE IF NOT EXISTS _backup_tasks AS SELECT * FROM tasks;
CREATE TABLE IF NOT EXISTS _backup_subtasks AS SELECT * FROM subtasks;
CREATE TABLE IF NOT EXISTS _backup_phases AS SELECT * FROM phases;
CREATE TABLE IF NOT EXISTS _backup_bugs AS SELECT * FROM bugs;

-- Drop existing tables
DROP TABLE IF EXISTS entity_history CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS bugs CASCADE;
DROP TABLE IF EXISTS subtasks CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS user_stories CASCADE;
DROP TABLE IF EXISTS usecases CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS programs CASCADE;
DROP TABLE IF EXISTS phases CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- Recreate clients table with string ID
CREATE TABLE clients (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('CLI', 'clients_id_seq'),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20),
    updated_by VARCHAR(20)
);

-- Recreate users table with string ID
CREATE TABLE users (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('USR', 'users_id_seq'),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer')),
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(50) DEFAULT 'snow',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recreate phases table with string ID
CREATE TABLE phases (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PHS', 'phases_id_seq'),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) NOT NULL DEFAULT '#4A90E2',
    is_active BOOLEAN DEFAULT true NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate programs table with string ID
CREATE TABLE programs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PRG', 'programs_id_seq'),
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planning',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate projects table with string ID
CREATE TABLE projects (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('PRJ', 'projects_id_seq'),
    program_id VARCHAR(20) NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Planning',
    repository_url VARCHAR(500),
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate usecases table with string ID
CREATE TABLE usecases (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('USC', 'usecases_id_seq'),
    project_id VARCHAR(20) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Draft',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate user_stories table with string ID
CREATE TABLE user_stories (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('UST', 'user_stories_id_seq'),
    usecase_id VARCHAR(20) NOT NULL REFERENCES usecases(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
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

-- Recreate tasks table with string ID
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TSK', 'tasks_id_seq'),
    user_story_id VARCHAR(20) NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    phase_id VARCHAR(20) NOT NULL REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'To Do',
    priority VARCHAR(20) DEFAULT 'Medium',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
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

-- Recreate subtasks table with string ID
CREATE TABLE subtasks (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('SUB', 'subtasks_id_seq'),
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    phase_id VARCHAR(20) NOT NULL REFERENCES phases(id),
    status VARCHAR(50) DEFAULT 'To Do',
    assigned_to VARCHAR(20) REFERENCES users(id) ON DELETE SET NULL,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(20) REFERENCES users(id),
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate bugs table with string ID
CREATE TABLE bugs (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('BUG', 'bugs_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask')),
    entity_id VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
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
    updated_by VARCHAR(20) REFERENCES users(id)
);

-- Recreate audit_logs table with string ID
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

-- Recreate entity_history table with string ID
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

-- Recreate all indexes
CREATE INDEX idx_users_client_id ON users(client_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE INDEX idx_clients_is_deleted ON clients(is_deleted);
CREATE INDEX idx_programs_client_id ON programs(client_id);
CREATE INDEX idx_programs_status ON programs(status);
CREATE INDEX idx_programs_is_deleted ON programs(is_deleted);

CREATE INDEX idx_projects_program_id ON projects(program_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_is_deleted ON projects(is_deleted);

CREATE INDEX idx_usecases_project_id ON usecases(project_id);
CREATE INDEX idx_usecases_status ON usecases(status);
CREATE INDEX idx_usecases_is_deleted ON usecases(is_deleted);

CREATE INDEX idx_user_stories_usecase_id ON user_stories(usecase_id);
CREATE INDEX idx_user_stories_status ON user_stories(status);
CREATE INDEX idx_user_stories_is_deleted ON user_stories(is_deleted);

CREATE INDEX idx_tasks_user_story_id ON tasks(user_story_id);
CREATE INDEX idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_is_deleted ON tasks(is_deleted);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX idx_subtasks_phase_id ON subtasks(phase_id);
CREATE INDEX idx_subtasks_assigned_to ON subtasks(assigned_to);
CREATE INDEX idx_subtasks_status ON subtasks(status);
CREATE INDEX idx_subtasks_is_deleted ON subtasks(is_deleted);

CREATE INDEX idx_phases_is_active ON phases(is_active);
CREATE INDEX idx_phases_is_deleted ON phases(is_deleted);
CREATE INDEX idx_phases_display_order ON phases(display_order);

CREATE INDEX idx_bugs_entity ON bugs(entity_type, entity_id);
CREATE INDEX idx_bugs_status ON bugs(status);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_priority ON bugs(priority);
CREATE INDEX idx_bugs_assigned_to ON bugs(assigned_to);
CREATE INDEX idx_bugs_reported_by ON bugs(reported_by);
CREATE INDEX idx_bugs_is_deleted ON bugs(is_deleted);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_client_id ON audit_logs(client_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

CREATE INDEX idx_entity_history_entity ON entity_history(entity_type, entity_id);
CREATE INDEX idx_entity_history_changed_at ON entity_history(changed_at);
CREATE INDEX idx_entity_history_changed_by ON entity_history(changed_by);

-- Recreate triggers
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

-- Insert default phases
INSERT INTO phases (name, description, color, display_order) VALUES
('Development', 'Software development and coding tasks', '#3498db', 1),
('Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2),
('Design', 'UI/UX and architecture design tasks', '#e67e22', 3),
('Testing', 'Quality assurance and testing tasks', '#1abc9c', 4);

-- Add comments
COMMENT ON TABLE audit_logs IS 'Immutable audit log table. Records should never be updated or deleted. Retention policy: 7 years minimum.';
COMMENT ON TABLE entity_history IS 'Field-level change tracking for all entities. Provides detailed audit trail of what changed, when, and by whom.';
COMMENT ON TABLE subtasks IS 'Subtasks can only be created under Tasks, not under other Subtasks. This constraint is enforced at the application level.';
COMMENT ON COLUMN users.role IS 'User role determines permissions: Admin (full access), Architect (programs/projects/usecases/stories), Designer (usecases/stories), Developer (tasks/subtasks/bugs), Tester (bugs)';

-- Clean up backup tables (optional - comment out if you want to keep backups)
-- DROP TABLE IF EXISTS _backup_clients;
-- DROP TABLE IF EXISTS _backup_users;
-- DROP TABLE IF EXISTS _backup_programs;
-- DROP TABLE IF EXISTS _backup_projects;
-- DROP TABLE IF EXISTS _backup_usecases;
-- DROP TABLE IF EXISTS _backup_user_stories;
-- DROP TABLE IF EXISTS _backup_tasks;
-- DROP TABLE IF EXISTS _backup_subtasks;
-- DROP TABLE IF EXISTS _backup_phases;
-- DROP TABLE IF EXISTS _backup_bugs;

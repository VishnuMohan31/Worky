-- Migration: Create Team Management and Assignment System Schema
-- Date: 2025-01-14
-- Description: Add tables for team management and assignment tracking

-- Create teams table
-- Note: project_id is nullable to allow teams to be created before assigning to a project
CREATE TABLE IF NOT EXISTS teams (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id VARCHAR(50), -- Nullable: teams can exist without project assignment
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    CONSTRAINT fk_teams_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_teams_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_teams_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Create team_members table for user-team associations
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
    CONSTRAINT uk_team_members_unique UNIQUE(team_id, user_id) -- Prevent duplicate memberships
);

-- Create assignments table for entity-user assignments
CREATE TABLE IF NOT EXISTS assignments (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'client', 'program', 'project', 'usecase', 'userstory', 'task', 'subtask'
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL, -- 'owner', 'contact_person', 'developer'
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    CONSTRAINT fk_assignments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignments_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_assignments_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Create assignment_history table for audit trail
CREATE TABLE IF NOT EXISTS assignment_history (
    id VARCHAR(50) PRIMARY KEY,
    assignment_id VARCHAR(50),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'assigned', 'unassigned', 'updated'
    previous_user_id VARCHAR(50), -- For reassignments
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    CONSTRAINT fk_assignment_history_assignment FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE SET NULL,
    CONSTRAINT fk_assignment_history_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_assignment_history_previous_user FOREIGN KEY (previous_user_id) REFERENCES users(id),
    CONSTRAINT fk_assignment_history_created_by FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Add indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_teams_project ON teams(project_id);
CREATE INDEX IF NOT EXISTS idx_teams_active ON teams(is_active);
CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_active ON team_members(is_active);
CREATE INDEX IF NOT EXISTS idx_assignments_entity ON assignments(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user ON assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_type ON assignments(assignment_type);
CREATE INDEX IF NOT EXISTS idx_assignment_history_entity ON assignment_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_assignment_history_user ON assignment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_assignment_history_date ON assignment_history(created_at);

-- Add unique constraint to prevent duplicate user-entity-type assignments
-- This allows multiple owners/assignees but prevents same user from being assigned multiple times
CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_unique_user_entity 
ON assignments(entity_type, entity_id, user_id, assignment_type) 
WHERE is_active = TRUE;

-- Note: Sample team creation moved to seed data (999_seed_dev_data.sql)
-- Teams can be created without project assignment and assigned later
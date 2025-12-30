-- Worky Database Schema - Migration 013
-- Version: 013
-- Description: Fix sprints table schema to use VARCHAR(20) instead of UUID

-- Create sequence for sprints if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS sprints_id_seq START 1;

-- Create custom function for sprint IDs (SPR_01 format)
CREATE OR REPLACE FUNCTION generate_sprint_id()
RETURNS TEXT AS $$
DECLARE
    next_val INTEGER;
    string_id TEXT;
BEGIN
    EXECUTE format('SELECT nextval(%L)', 'sprints_id_seq') INTO next_val;
    string_id := 'SPR_' || LPAD(next_val::TEXT, 2, '0');
    RETURN string_id;
END;
$$ LANGUAGE plpgsql;

-- First, drop foreign key constraints that reference sprints
ALTER TABLE sprint_tasks DROP CONSTRAINT IF EXISTS sprint_tasks_sprint_id_fkey;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_sprint_id_fkey;

-- Drop the existing sprints table and recreate with correct schema
DROP TABLE IF EXISTS sprints CASCADE;

-- Recreate sprints table with VARCHAR(20) IDs
CREATE TABLE sprints (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_sprint_id(),
    project_id VARCHAR(20) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Planning',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);
CREATE INDEX idx_sprints_status ON sprints(status);

-- Recreate sprint_tasks table with VARCHAR(20) IDs
DROP TABLE IF EXISTS sprint_tasks CASCADE;

CREATE TABLE sprint_tasks (
    sprint_id VARCHAR(20) NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id VARCHAR(20) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (sprint_id, task_id)
);

-- Add back the sprint_id column to tasks if it doesn't exist
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS sprint_id VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_tasks_sprint_id ON tasks(sprint_id);

-- Add comments
COMMENT ON TABLE sprints IS 'Sprint management table';
COMMENT ON COLUMN sprints.id IS 'Sprint ID in format SPR_01';
COMMENT ON COLUMN sprints.project_id IS 'Reference to the project this sprint belongs to';
COMMENT ON COLUMN sprints.status IS 'Sprint status: Planning, Active, Completed, Cancelled';



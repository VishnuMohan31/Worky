-- Worky Database Schema - Migration 012
-- Version: 012
-- Description: Add sprint configuration to company settings, update sprint model, add sprint_id to tasks

-- Add sprint configuration columns to company_settings
ALTER TABLE company_settings
ADD COLUMN IF NOT EXISTS sprint_length_weeks VARCHAR(10) DEFAULT '2',
ADD COLUMN IF NOT EXISTS sprint_starting_day VARCHAR(20) DEFAULT 'Monday';

-- Create sequence for sprints if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS sprints_id_seq START 1;

-- Update sprints table to use string ID generation (if not already done)
-- Note: This assumes sprints table already exists. If the id column needs to be changed,
-- you may need to drop and recreate it or use ALTER COLUMN with appropriate constraints.

-- Add sprint_id column to tasks table (without foreign key constraint initially)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS sprint_id VARCHAR(20);

-- Add foreign key constraint only if sprints table uses VARCHAR(20) for id
-- Note: If sprints.id is UUID, you'll need to update sprints table first
-- ALTER TABLE tasks ADD CONSTRAINT tasks_sprint_id_fkey FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL;

-- Create index for sprint_id on tasks
CREATE INDEX IF NOT EXISTS idx_tasks_sprint_id ON tasks(sprint_id);

-- Add comments
COMMENT ON COLUMN company_settings.sprint_length_weeks IS 'Sprint length in weeks: "1" or "2"';
COMMENT ON COLUMN company_settings.sprint_starting_day IS 'Day of week when sprints start: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday';
COMMENT ON COLUMN tasks.sprint_id IS 'Reference to the sprint this task belongs to';


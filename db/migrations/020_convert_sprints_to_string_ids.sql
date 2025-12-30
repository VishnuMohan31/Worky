-- Worky Database Schema - Migration 020
-- Version: 020
-- Description: Convert sprints table from UUID to string IDs

-- Drop existing foreign key constraints that reference sprints
ALTER TABLE IF EXISTS tasks DROP CONSTRAINT IF EXISTS tasks_sprint_id_fkey;
ALTER TABLE IF EXISTS sprint_tasks DROP CONSTRAINT IF EXISTS sprint_tasks_sprint_id_fkey;

-- Drop existing sprints table (since we need to change the primary key type)
DROP TABLE IF EXISTS sprints CASCADE;

-- Create sprints table with string IDs
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

-- Create indexes
CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);
CREATE INDEX idx_sprints_status ON sprints(status);

-- Create updated_at trigger
CREATE TRIGGER update_sprints_updated_at 
    BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Recreate sprint_tasks table with string IDs
DROP TABLE IF EXISTS sprint_tasks CASCADE;
CREATE TABLE sprint_tasks (
    sprint_id VARCHAR(20) REFERENCES sprints(id) ON DELETE CASCADE,
    task_id VARCHAR(20) REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (sprint_id, task_id)
);

-- Create indexes for sprint_tasks
CREATE INDEX idx_sprint_tasks_sprint_id ON sprint_tasks(sprint_id);
CREATE INDEX idx_sprint_tasks_task_id ON sprint_tasks(task_id);

-- Update tasks table to use VARCHAR(20) for sprint_id if not already done
ALTER TABLE tasks ALTER COLUMN sprint_id TYPE VARCHAR(20);

-- Add foreign key constraint for tasks.sprint_id
ALTER TABLE tasks ADD CONSTRAINT tasks_sprint_id_fkey 
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL;

-- Add comments
COMMENT ON TABLE sprints IS 'Sprints for project management with string-based IDs';
COMMENT ON COLUMN sprints.id IS 'Sprint ID in format SPR-XXXXXX';
COMMENT ON COLUMN sprints.project_id IS 'Reference to the project this sprint belongs to';
COMMENT ON COLUMN sprints.status IS 'Sprint status: Planning, Active, Completed, or Cancelled';

COMMENT ON TABLE sprint_tasks IS 'Many-to-many relationship between sprints and tasks';
COMMENT ON COLUMN sprint_tasks.sprint_id IS 'Reference to sprint';
COMMENT ON COLUMN sprint_tasks.task_id IS 'Reference to task';
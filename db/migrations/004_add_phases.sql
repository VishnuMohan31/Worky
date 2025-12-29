-- Worky Database Schema - Migration 004
-- Version: 004
-- Description: Add phases table and link tasks/subtasks to phases

-- Create phases table
CREATE TABLE phases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) NOT NULL DEFAULT '#4A90E2',
    is_active BOOLEAN DEFAULT true NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Create indexes on phases table
CREATE INDEX idx_phases_is_active ON phases(is_active);
CREATE INDEX idx_phases_is_deleted ON phases(is_deleted);
CREATE INDEX idx_phases_display_order ON phases(display_order);

-- Create updated_at trigger for phases
CREATE TRIGGER update_phases_updated_at BEFORE UPDATE ON phases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default phases
INSERT INTO phases (name, description, color, display_order) VALUES
('Development', 'Software development and coding tasks', '#3498db', 1),
('Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2),
('Design', 'UI/UX and architecture design tasks', '#e67e22', 3),
('Testing', 'Quality assurance and testing tasks', '#1abc9c', 4);

-- Add phase_id column to tasks table
ALTER TABLE tasks
ADD COLUMN phase_id UUID REFERENCES phases(id);

-- Add phase_id column to subtasks table
ALTER TABLE subtasks
ADD COLUMN phase_id UUID REFERENCES phases(id);

-- Set default phase for existing tasks (Development)
UPDATE tasks
SET phase_id = (SELECT id FROM phases WHERE name = 'Development' LIMIT 1)
WHERE phase_id IS NULL;

-- Set default phase for existing subtasks (Development)
UPDATE subtasks
SET phase_id = (SELECT id FROM phases WHERE name = 'Development' LIMIT 1)
WHERE phase_id IS NULL;

-- Make phase_id NOT NULL after setting defaults
ALTER TABLE tasks
ALTER COLUMN phase_id SET NOT NULL;

ALTER TABLE subtasks
ALTER COLUMN phase_id SET NOT NULL;

-- Create indexes on phase_id
CREATE INDEX idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX idx_subtasks_phase_id ON subtasks(phase_id);

-- Add constraint to prevent subtasks under subtasks
-- This is enforced at application level, but we add a comment for documentation
COMMENT ON TABLE subtasks IS 'Subtasks can only be created under Tasks, not under other Subtasks. This constraint is enforced at the application level.';

-- Add estimated_hours and actual_hours to subtasks if not exists
ALTER TABLE subtasks
ADD COLUMN IF NOT EXISTS estimated_hours DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS actual_hours DECIMAL(10, 2);

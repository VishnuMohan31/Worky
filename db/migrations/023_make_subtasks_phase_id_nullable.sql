-- Migration 023: Make subtasks phase_id nullable
-- The phase_id field should be optional for subtasks

-- Make phase_id nullable in subtasks table
ALTER TABLE subtasks ALTER COLUMN phase_id DROP NOT NULL;

-- Add comment for clarity
COMMENT ON COLUMN subtasks.phase_id IS 'Optional phase ID for subtask (nullable)';
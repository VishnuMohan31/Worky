-- Migration 022: Fix subtasks audit fields foreign key constraints
-- Remove foreign key constraints from created_by and updated_by fields
-- These should be simple string fields, not foreign keys

-- Drop foreign key constraints on created_by and updated_by
ALTER TABLE subtasks DROP CONSTRAINT IF EXISTS subtasks_created_by_fkey;
ALTER TABLE subtasks DROP CONSTRAINT IF EXISTS subtasks_updated_by_fkey;

-- Add comments for clarity
COMMENT ON COLUMN subtasks.created_by IS 'User ID who created the subtask (string, not FK)';
COMMENT ON COLUMN subtasks.updated_by IS 'User ID who last updated the subtask (string, not FK)';
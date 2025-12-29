-- Migration: Add duration_days and scrum_points columns to subtasks table
-- These columns are expected by the API but were missing from the database schema

-- Add duration_days column
ALTER TABLE subtasks ADD COLUMN IF NOT EXISTS duration_days INTEGER;

-- Add scrum_points column
ALTER TABLE subtasks ADD COLUMN IF NOT EXISTS scrum_points NUMERIC(5, 2);

-- Add comments for documentation
COMMENT ON COLUMN subtasks.duration_days IS 'Expected duration in days for this subtask';
COMMENT ON COLUMN subtasks.scrum_points IS 'Scrum story points assigned to this subtask';


-- Worky Database Schema - Migration 014
-- Version: 014
-- Description: Add sprint configuration columns to projects table

-- Add sprint configuration columns to projects table
ALTER TABLE projects ADD COLUMN IF NOT EXISTS sprint_length_weeks VARCHAR(10) DEFAULT '2';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS sprint_starting_day VARCHAR(20) DEFAULT 'Monday';

-- Add comments
COMMENT ON COLUMN projects.sprint_length_weeks IS 'Sprint length in weeks: "1" or "2"';
COMMENT ON COLUMN projects.sprint_starting_day IS 'Day of week when sprints start: Monday, Tuesday, Wednesday, etc.';


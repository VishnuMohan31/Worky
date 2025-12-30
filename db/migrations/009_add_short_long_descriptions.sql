-- Worky Database Schema - Migration 009
-- Version: 009
-- Description: Add short_description and long_description to all entity tables

-- Add short and long descriptions to clients table
ALTER TABLE clients
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to programs table
ALTER TABLE programs
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to projects table
ALTER TABLE projects
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to usecases table
ALTER TABLE usecases
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to user_stories table
ALTER TABLE user_stories
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to tasks table
ALTER TABLE tasks
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to subtasks table
ALTER TABLE subtasks
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to bugs table
ALTER TABLE bugs
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add short and long descriptions to phases table
ALTER TABLE phases
DROP COLUMN IF EXISTS description,
ADD COLUMN short_description VARCHAR(500),
ADD COLUMN long_description TEXT;

-- Add comments explaining the fields
COMMENT ON COLUMN clients.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN clients.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN programs.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN programs.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN projects.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN projects.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN usecases.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN usecases.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN user_stories.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN user_stories.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN tasks.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN tasks.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN subtasks.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN subtasks.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN bugs.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN bugs.long_description IS 'Detailed description with unlimited length for full entity view';

COMMENT ON COLUMN phases.short_description IS 'Brief summary (max 500 chars) displayed in lists and cards';
COMMENT ON COLUMN phases.long_description IS 'Detailed description with unlimited length for full entity view';

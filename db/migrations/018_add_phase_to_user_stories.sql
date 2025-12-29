-- Migration: Add Phase to User Stories
-- Description: Adds phase_id column to user_stories table for work phase tracking
-- Date: 2025-11-30

-- Add phase_id column to user_stories table
ALTER TABLE user_stories
ADD COLUMN phase_id VARCHAR(20) REFERENCES phases(id);

-- Set default phase for existing user stories (Development)
UPDATE user_stories
SET phase_id = (SELECT id FROM phases WHERE name = 'Development' LIMIT 1)
WHERE phase_id IS NULL;

-- Make phase_id NOT NULL after setting defaults
ALTER TABLE user_stories
ALTER COLUMN phase_id SET NOT NULL;

-- Create index on phase_id
CREATE INDEX IF NOT EXISTS idx_user_stories_phase_id ON user_stories(phase_id);

-- Add comment for documentation
COMMENT ON COLUMN user_stories.phase_id IS 'Category: Status & Priority | Work phase (required: Development, Analysis, Design, Testing)';

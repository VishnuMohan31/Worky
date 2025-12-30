-- Worky Database Schema - Migration 010
-- Version: 010
-- Description: Add user view preferences for tile/list view toggle

-- Add view_preferences column to users table to store UI preferences
ALTER TABLE users
ADD COLUMN view_preferences JSONB DEFAULT '{
  "defaultView": "tile",
  "entityViews": {
    "clients": "tile",
    "programs": "tile",
    "projects": "tile",
    "usecases": "list",
    "userstories": "list",
    "tasks": "list",
    "subtasks": "list",
    "bugs": "list"
  }
}'::jsonb;

-- Add comment explaining the structure
COMMENT ON COLUMN users.view_preferences IS 'User UI preferences stored as JSON. Includes defaultView (tile/list) and per-entity view preferences. Example: {"defaultView": "tile", "entityViews": {"clients": "tile", "projects": "list"}}';

-- Create index for faster JSON queries
CREATE INDEX idx_users_view_preferences ON users USING GIN (view_preferences);

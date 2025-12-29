-- Worky Database Schema - Migration 006
-- Version: 006
-- Description: Update user roles to match new requirements

-- Drop the old CHECK constraint on users.role
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add new CHECK constraint with updated roles
ALTER TABLE users
ADD CONSTRAINT users_role_check CHECK (role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer'));

-- Update existing roles to new values
UPDATE users SET role = 'Developer' WHERE role = 'Project Manager';
UPDATE users SET role = 'Developer' WHERE role = 'Product Owner';
UPDATE users SET role = 'Developer' WHERE role = 'DevOps';
UPDATE users SET role = 'Developer' WHERE role = 'Business Analyst';

-- Add comment explaining role permissions
COMMENT ON COLUMN users.role IS 'User role determines permissions: Admin (full access), Architect (programs/projects/usecases/stories), Designer (usecases/stories), Developer (tasks/subtasks/bugs), Tester (bugs)';

-- Worky Database Schema - Migration 003
-- Version: 003
-- Description: Add audit columns (created_by, updated_by) and soft delete (is_deleted) to all entity tables

-- Add audit and soft delete columns to clients table
ALTER TABLE clients
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to programs table
ALTER TABLE programs
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to projects table
ALTER TABLE projects
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to usecases table
ALTER TABLE usecases
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to user_stories table
ALTER TABLE user_stories
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to tasks table
ALTER TABLE tasks
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add audit and soft delete columns to subtasks table
ALTER TABLE subtasks
ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN created_by UUID REFERENCES users(id),
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Create indexes on is_deleted for efficient filtering
CREATE INDEX idx_clients_is_deleted ON clients(is_deleted);
CREATE INDEX idx_programs_is_deleted ON programs(is_deleted);
CREATE INDEX idx_projects_is_deleted ON projects(is_deleted);
CREATE INDEX idx_usecases_is_deleted ON usecases(is_deleted);
CREATE INDEX idx_user_stories_is_deleted ON user_stories(is_deleted);
CREATE INDEX idx_tasks_is_deleted ON tasks(is_deleted);
CREATE INDEX idx_subtasks_is_deleted ON subtasks(is_deleted);

-- Create indexes on created_by and updated_by for audit queries
CREATE INDEX idx_programs_created_by ON programs(created_by);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_usecases_created_by ON usecases(created_by);
CREATE INDEX idx_user_stories_created_by ON user_stories(created_by);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_subtasks_created_by ON subtasks(created_by);

-- Update user_stories table to rename 'title' to 'name' for consistency
ALTER TABLE user_stories RENAME COLUMN title TO name;

-- Update subtasks table to rename 'title' to 'name' for consistency  
ALTER TABLE subtasks RENAME COLUMN title TO name;

-- Update tasks table to rename 'title' to 'name' for consistency
ALTER TABLE tasks RENAME COLUMN title TO name;

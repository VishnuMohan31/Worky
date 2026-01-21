-- Migration: Expand User Role Constraint
-- Date: 2025-01-15
-- Description: Update the role field constraint to match primary_role, allowing all supported roles

-- Drop the existing constraint on users.role
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add new CHECK constraint with expanded roles (matching primary_role)
ALTER TABLE users
ADD CONSTRAINT users_role_check 
CHECK (role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer', 'Owner', 'Contact Person', 'Project Manager', 'DevOps'));

-- Add comment explaining the expanded roles
COMMENT ON COLUMN users.role IS 'User role determines permissions. Supported roles: Admin (full access), Project Manager (programs/projects), Architect (programs/projects/usecases/stories), Designer (usecases/stories), Developer (tasks/subtasks/bugs), Tester (bugs), DevOps (infrastructure), Owner (client owner), Contact Person (client contact)';




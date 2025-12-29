-- Migration: Extend Users Table for Team Management
-- Date: 2025-01-14
-- Description: Add role management columns to users table for team assignment system

-- Add primary_role column to users table (replacing the existing single role)
-- Note: We'll keep the existing 'role' column for backward compatibility
ALTER TABLE users ADD COLUMN IF NOT EXISTS primary_role VARCHAR(50) DEFAULT 'Developer';

-- Add secondary_roles array column for multiple roles
ALTER TABLE users ADD COLUMN IF NOT EXISTS secondary_roles TEXT[];

-- Add is_contact_person boolean flag
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_contact_person BOOLEAN DEFAULT FALSE;

-- Update primary_role to match existing role values for backward compatibility
UPDATE users SET primary_role = role WHERE primary_role = 'Developer';

-- Add check constraint for primary_role (including existing values)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_users_primary_role' 
        AND table_name = 'users'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT chk_users_primary_role 
        CHECK (primary_role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer', 'Owner', 'Contact Person', 'Project Manager', 'DevOps'));
    END IF;
END $$;

-- Add check constraint for secondary_roles (validate array elements)
-- Note: PostgreSQL doesn't support CHECK constraints on array elements directly,
-- so we'll handle validation in the application layer

-- Create index for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_primary_role ON users(primary_role);
CREATE INDEX IF NOT EXISTS idx_users_contact_person ON users(is_contact_person) WHERE is_contact_person = TRUE;

-- Update existing users to set appropriate contact person flags
-- This is a placeholder - in production, this would be done based on business rules
UPDATE users SET is_contact_person = TRUE WHERE role = 'Admin';

-- Add comments for documentation
COMMENT ON COLUMN users.primary_role IS 'Primary role of the user for assignment purposes';
COMMENT ON COLUMN users.secondary_roles IS 'Array of additional roles the user can perform';
COMMENT ON COLUMN users.is_contact_person IS 'Flag indicating if user can be assigned as client contact person';
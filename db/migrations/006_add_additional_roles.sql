-- Add additional user roles
-- This migration adds HR, Product Manager, DevOps, Owner, and Contact Person roles

BEGIN;

-- Drop the existing constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add the new constraint with additional roles
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (
    role IN (
        'Admin',
        'Developer', 
        'Tester',
        'Architect',
        'Designer',
        'HR',
        'Product Manager',
        'DevOps',
        'Owner',
        'Contact Person'
    )
);

-- Update the comment on the role column
COMMENT ON COLUMN users.role IS 'User role: Admin, Developer, Tester, Architect, Designer, HR, Product Manager, DevOps, Owner, Contact Person';

COMMIT;

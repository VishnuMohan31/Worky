-- Migration: Update user roles constraint to include missing roles and HR
-- This fixes the 500 error when creating users with Project Manager, DevOps, Owner, Contact Person roles
-- and adds the new HR role
-- Date: 2026-01-31

-- Drop the existing constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add the updated constraint with all required roles
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN (
    'Admin', 
    'Developer', 
    'Tester', 
    'Architect', 
    'Designer',
    'Project Manager',
    'DevOps',
    'Owner',
    'Contact Person',
    'HR'
));

-- Update primary_role constraint if it exists (it should match role options)
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_primary_role_check;
ALTER TABLE users ADD CONSTRAINT users_primary_role_check 
CHECK (primary_role IN (
    'Admin', 
    'Developer', 
    'Tester', 
    'Architect', 
    'Designer',
    'Project Manager',
    'DevOps',
    'Owner',
    'Contact Person',
    'HR'
));
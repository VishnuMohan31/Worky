-- Migration: Fix Team Management and Assignment Schema
-- Date: 2025-01-15
-- Description: Fix schema issues for cross-device compatibility
--   1. Make teams.project_id nullable to allow unassigned teams
--   2. Remove single-owner constraint to allow multiple owners
--   3. Add unique constraint to prevent duplicate user-entity assignments

-- Step 1: Make teams.project_id nullable (allows teams to exist without project assignment)
DO $$
BEGIN
    -- Check if the column exists and is NOT NULL
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'teams' 
        AND column_name = 'project_id' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE teams ALTER COLUMN project_id DROP NOT NULL;
        RAISE NOTICE 'Made teams.project_id nullable';
    ELSE
        RAISE NOTICE 'teams.project_id is already nullable or does not exist';
    END IF;
END $$;

-- Step 2: Remove the old single-owner constraint if it exists
-- This constraint prevented multiple owners per entity, which we now allow
DROP INDEX IF EXISTS idx_assignments_unique_owner;

-- Step 3: Add new unique constraint to prevent duplicate user-entity-type assignments
-- This allows multiple owners but prevents same user from being assigned multiple times
-- to the same entity with the same assignment type
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_assignments_unique_user_entity'
    ) THEN
        CREATE UNIQUE INDEX idx_assignments_unique_user_entity 
        ON assignments(entity_type, entity_id, user_id, assignment_type) 
        WHERE is_active = TRUE;
        RAISE NOTICE 'Created idx_assignments_unique_user_entity index';
    ELSE
        RAISE NOTICE 'idx_assignments_unique_user_entity index already exists';
    END IF;
END $$;

-- Step 4: Ensure primary_role column exists in users table (added for role validation)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'primary_role'
    ) THEN
        ALTER TABLE users ADD COLUMN primary_role VARCHAR(100);
        RAISE NOTICE 'Added primary_role column to users';
    ELSE
        RAISE NOTICE 'primary_role column already exists in users';
    END IF;
END $$;

-- Step 5: Ensure secondary_roles column exists in users table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'secondary_roles'
    ) THEN
        ALTER TABLE users ADD COLUMN secondary_roles TEXT[];
        RAISE NOTICE 'Added secondary_roles column to users';
    ELSE
        RAISE NOTICE 'secondary_roles column already exists in users';
    END IF;
END $$;

-- Step 6: Update primary_role from role if not set
UPDATE users 
SET primary_role = role 
WHERE primary_role IS NULL AND role IS NOT NULL;

-- Migration completed successfully
DO $$ BEGIN RAISE NOTICE 'Migration 029_fix_team_assignment_schema completed successfully'; END $$;


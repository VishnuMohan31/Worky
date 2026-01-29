-- ============================================================================
-- Fix Notification Preferences Trigger
-- ============================================================================
-- This script fixes the issue where the first user creation fails due to
-- the notification preferences trigger trying to insert into a table that
-- might not be ready yet during database initialization.
-- ============================================================================

-- Drop and recreate the function with error handling
DROP FUNCTION IF EXISTS create_default_notification_preferences() CASCADE;

CREATE OR REPLACE FUNCTION create_default_notification_preferences()
RETURNS TRIGGER AS $
BEGIN
    -- Check if notification_preferences table exists and has the required enum type
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'notification_preferences'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.types 
        WHERE type_name = 'notification_type'
    ) THEN
        BEGIN
            INSERT INTO notification_preferences (user_id, notification_type, email_enabled, in_app_enabled, push_enabled)
            VALUES 
                (NEW.id, 'assignment_created', TRUE, TRUE, FALSE),
                (NEW.id, 'assignment_removed', TRUE, TRUE, FALSE),
                (NEW.id, 'team_member_added', TRUE, TRUE, FALSE),
                (NEW.id, 'team_member_removed', TRUE, TRUE, FALSE),
                (NEW.id, 'assignment_conflict', TRUE, TRUE, FALSE),
                (NEW.id, 'bulk_assignment_completed', TRUE, TRUE, FALSE),
                (NEW.id, 'bulk_assignment_failed', TRUE, TRUE, FALSE);
        EXCEPTION
            WHEN OTHERS THEN
                -- Log the error but don't fail the user creation
                RAISE NOTICE 'Failed to create notification preferences for user %: %', NEW.id, SQLERRM;
        END;
    END IF;
    
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

-- Recreate the trigger if it doesn't exist
DROP TRIGGER IF EXISTS trigger_create_default_notification_preferences ON users;

CREATE TRIGGER trigger_create_default_notification_preferences
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_notification_preferences();

-- ============================================================================
-- Create missing notification preferences for existing users
-- ============================================================================
-- This will create notification preferences for any users that were created
-- before the notification system was fully set up
-- ============================================================================

DO $
BEGIN
    -- Only run if both tables exist
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'notification_preferences') 
       AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') 
       AND EXISTS (SELECT 1 FROM information_schema.types WHERE type_name = 'notification_type') THEN
        
        -- Create notification preferences for users who don't have them
        INSERT INTO notification_preferences (user_id, notification_type, email_enabled, in_app_enabled, push_enabled)
        SELECT 
            u.id,
            unnest(ARRAY[
                'assignment_created'::notification_type,
                'assignment_removed'::notification_type,
                'team_member_added'::notification_type,
                'team_member_removed'::notification_type,
                'assignment_conflict'::notification_type,
                'bulk_assignment_completed'::notification_type,
                'bulk_assignment_failed'::notification_type
            ]),
            TRUE,
            TRUE,
            FALSE
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM notification_preferences np 
            WHERE np.user_id = u.id
        );
        
        RAISE NOTICE 'Created missing notification preferences for existing users';
    END IF;
END;
$;
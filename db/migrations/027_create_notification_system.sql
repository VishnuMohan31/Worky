-- Migration: Create notification system tables
-- Description: Add tables for notifications, notification preferences, and notification history

-- Create notification types enum
CREATE TYPE notification_type AS ENUM (
    'assignment_created',
    'assignment_removed',
    'team_member_added',
    'team_member_removed',
    'assignment_conflict',
    'bulk_assignment_completed',
    'bulk_assignment_failed'
);

-- Create notification status enum
CREATE TYPE notification_status AS ENUM (
    'pending',
    'sent',
    'failed',
    'read'
);

-- Create notification channel enum
CREATE TYPE notification_channel AS ENUM (
    'email',
    'in_app',
    'push'
);

-- Create notifications table
CREATE TABLE notifications (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTIF', 'notifications_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(20),
    status notification_status NOT NULL DEFAULT 'pending',
    channel notification_channel NOT NULL DEFAULT 'in_app',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(20) REFERENCES users(id),
    context_data TEXT -- JSON string for additional context
);

-- Create notification preferences table
CREATE TABLE notification_preferences (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NPREF', 'notification_preferences_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    email_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    push_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create notification history table
CREATE TABLE notification_history (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NHIST', 'notification_history_id_seq'),
    notification_id VARCHAR(20) NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    status notification_status NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    error_code VARCHAR(50),
    external_id VARCHAR(255) -- ID from email service, push service, etc.
);

-- Create indexes for performance
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at);
CREATE INDEX idx_notifications_entity ON notifications(entity_type, entity_id);
CREATE INDEX idx_notifications_type_status ON notifications(type, status);

CREATE UNIQUE INDEX idx_notification_preferences_user_type ON notification_preferences(user_id, notification_type);

CREATE INDEX idx_notification_history_notification ON notification_history(notification_id);
CREATE INDEX idx_notification_history_status ON notification_history(status, attempted_at);

-- Create sequence for notification IDs
CREATE SEQUENCE IF NOT EXISTS notifications_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_preferences_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS notification_history_id_seq START 1;

-- Insert default notification preferences for existing users
INSERT INTO notification_preferences (user_id, notification_type, email_enabled, in_app_enabled, push_enabled)
SELECT 
    u.id,
    nt.type,
    TRUE,  -- email_enabled
    TRUE,  -- in_app_enabled
    FALSE  -- push_enabled
FROM users u
CROSS JOIN (
    VALUES 
        ('assignment_created'::notification_type),
        ('assignment_removed'::notification_type),
        ('team_member_added'::notification_type),
        ('team_member_removed'::notification_type),
        ('assignment_conflict'::notification_type),
        ('bulk_assignment_completed'::notification_type),
        ('bulk_assignment_failed'::notification_type)
) AS nt(type)
WHERE u.is_active = TRUE;

-- Add trigger to automatically create notification preferences for new users
CREATE OR REPLACE FUNCTION create_default_notification_preferences()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert default notification preferences for the new user
    INSERT INTO notification_preferences (user_id, notification_type, email_enabled, in_app_enabled, push_enabled)
    VALUES 
        (NEW.id, 'assignment_created', TRUE, TRUE, FALSE),
        (NEW.id, 'assignment_removed', TRUE, TRUE, FALSE),
        (NEW.id, 'team_member_added', TRUE, TRUE, FALSE),
        (NEW.id, 'team_member_removed', TRUE, TRUE, FALSE),
        (NEW.id, 'assignment_conflict', TRUE, TRUE, FALSE),
        (NEW.id, 'bulk_assignment_completed', TRUE, TRUE, FALSE),
        (NEW.id, 'bulk_assignment_failed', TRUE, TRUE, FALSE);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_default_notification_preferences
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_notification_preferences();

-- Add trigger to update notification preferences updated_at timestamp
CREATE OR REPLACE FUNCTION update_notification_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_notification_preferences_timestamp
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_preferences_timestamp();
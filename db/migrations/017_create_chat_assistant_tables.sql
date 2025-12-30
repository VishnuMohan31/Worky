-- Migration: Create Chat Assistant Tables
-- Description: Creates tables for chat messages, audit logs, and reminders
-- Date: 2025-11-30

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(20) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities JSONB,
    actions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for chat_messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at);

-- Create chat_audit_logs table
CREATE TABLE IF NOT EXISTS chat_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id VARCHAR(20) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    session_id VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    intent_type VARCHAR(50),
    entities_accessed JSONB,
    action_performed VARCHAR(100),
    action_result VARCHAR(20) CHECK (action_result IN ('success', 'failed', 'denied')),
    response_summary TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create indexes for chat_audit_logs
CREATE INDEX IF NOT EXISTS idx_chat_audit_logs_request ON chat_audit_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_chat_audit_logs_user ON chat_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_audit_logs_client ON chat_audit_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_chat_audit_logs_session ON chat_audit_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_audit_logs_timestamp ON chat_audit_logs(timestamp);

-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('task', 'bug', 'project', 'user_story', 'subtask')),
    entity_id VARCHAR(20) NOT NULL,
    message TEXT,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
    created_via VARCHAR(20) NOT NULL DEFAULT 'chat' CHECK (created_via IN ('chat', 'ui', 'api')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for reminders
CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX IF NOT EXISTS idx_reminders_is_sent ON reminders(is_sent);
CREATE INDEX IF NOT EXISTS idx_reminders_entity ON reminders(entity_type, entity_id);

-- Add comments for documentation
COMMENT ON TABLE chat_messages IS 'Stores chat conversation messages between users and the assistant';
COMMENT ON TABLE chat_audit_logs IS 'Audit trail for all chat interactions and actions performed';
COMMENT ON TABLE reminders IS 'User reminders created via chat or other interfaces';

COMMENT ON COLUMN chat_messages.session_id IS 'Unique identifier for the chat session';
COMMENT ON COLUMN chat_messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN chat_messages.intent_type IS 'Detected intent type from NLP processing';
COMMENT ON COLUMN chat_messages.entities IS 'Extracted entities from the message';
COMMENT ON COLUMN chat_messages.actions IS 'Actions to be performed based on the message';

COMMENT ON COLUMN chat_audit_logs.request_id IS 'Unique identifier for the request';
COMMENT ON COLUMN chat_audit_logs.entities_accessed IS 'List of entities accessed during the request';
COMMENT ON COLUMN chat_audit_logs.action_result IS 'Result of the action: success, failed, or denied';

COMMENT ON COLUMN reminders.entity_type IS 'Type of entity the reminder is for';
COMMENT ON COLUMN reminders.entity_id IS 'ID of the entity the reminder is for';
COMMENT ON COLUMN reminders.created_via IS 'Source of reminder creation: chat, ui, or api';

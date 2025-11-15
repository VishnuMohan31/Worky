-- Worky Database Schema - Migration 008
-- Version: 008
-- Description: Add immutable notes table for all entities

-- Create entity_notes table with polymorphic entity association
-- Notes are immutable - once created, they cannot be edited or deleted
CREATE TABLE entity_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOT', 'entity_notes_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug')),
    entity_id VARCHAR(20) NOT NULL,
    note_text TEXT NOT NULL,
    created_by VARCHAR(20) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create sequence for entity_notes
CREATE SEQUENCE IF NOT EXISTS entity_notes_id_seq START 1;

-- Create indexes for efficient querying
CREATE INDEX idx_entity_notes_entity ON entity_notes(entity_type, entity_id);
CREATE INDEX idx_entity_notes_created_at ON entity_notes(created_at DESC);
CREATE INDEX idx_entity_notes_created_by ON entity_notes(created_by);

-- Add comment explaining immutability
COMMENT ON TABLE entity_notes IS 'Immutable notes table. Notes can be attached to any entity. Once created, notes cannot be edited or deleted. Display in reverse chronological order on UI.';

-- Prevent updates and deletes on entity_notes table
CREATE OR REPLACE FUNCTION prevent_note_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Notes are immutable and cannot be modified or deleted';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to prevent updates and deletes
CREATE TRIGGER prevent_entity_notes_update
    BEFORE UPDATE ON entity_notes
    FOR EACH ROW
    EXECUTE FUNCTION prevent_note_modification();

CREATE TRIGGER prevent_entity_notes_delete
    BEFORE DELETE ON entity_notes
    FOR EACH ROW
    EXECUTE FUNCTION prevent_note_modification();

-- Add helpful view for recent notes across all entities
CREATE OR REPLACE VIEW recent_entity_notes AS
SELECT 
    n.id,
    n.entity_type,
    n.entity_id,
    n.note_text,
    n.created_at,
    u.full_name as created_by_name,
    u.email as created_by_email
FROM entity_notes n
JOIN users u ON n.created_by = u.id
ORDER BY n.created_at DESC;

COMMENT ON VIEW recent_entity_notes IS 'View showing all notes with user details, ordered by most recent first';

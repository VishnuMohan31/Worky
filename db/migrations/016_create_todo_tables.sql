-- Worky Database Schema - Migration 016
-- Version: 016
-- Description: Create TODO feature tables (todo_items and adhoc_notes) for personal work organization

-- Create function for updating updated_at timestamp if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequences for ID generation
CREATE SEQUENCE IF NOT EXISTS todo_items_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS adhoc_notes_id_seq START 1;

-- Create todo_items table
CREATE TABLE todo_items (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('TODO', 'todo_items_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    visibility VARCHAR(10) NOT NULL CHECK (visibility IN ('public', 'private')),
    linked_entity_type VARCHAR(20) CHECK (linked_entity_type IN ('task', 'subtask')),
    linked_entity_id VARCHAR(20),
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create adhoc_notes table
CREATE TABLE adhoc_notes (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('NOTE', 'adhoc_notes_id_seq'),
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    color VARCHAR(7) DEFAULT '#FFEB3B',
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for todo_items
CREATE INDEX idx_todo_items_user_id ON todo_items(user_id);
CREATE INDEX idx_todo_items_target_date ON todo_items(target_date);
CREATE INDEX idx_todo_items_visibility ON todo_items(visibility);
CREATE INDEX idx_todo_items_user_date ON todo_items(user_id, target_date) WHERE is_deleted = false;
CREATE INDEX idx_todo_items_linked_entity ON todo_items(linked_entity_type, linked_entity_id) WHERE linked_entity_id IS NOT NULL;
CREATE INDEX idx_todo_items_is_deleted ON todo_items(is_deleted);

-- Create indexes for adhoc_notes
CREATE INDEX idx_adhoc_notes_user_id ON adhoc_notes(user_id);
CREATE INDEX idx_adhoc_notes_position ON adhoc_notes(user_id, position) WHERE is_deleted = false;
CREATE INDEX idx_adhoc_notes_is_deleted ON adhoc_notes(is_deleted);

-- Create triggers for updated_at
CREATE TRIGGER update_todo_items_updated_at BEFORE UPDATE ON todo_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adhoc_notes_updated_at BEFORE UPDATE ON adhoc_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add constraints
ALTER TABLE adhoc_notes ADD CONSTRAINT check_position_positive CHECK (position >= 0);

-- Add comments
COMMENT ON TABLE todo_items IS 'Personal TODO items for users with optional links to tasks/subtasks';
COMMENT ON TABLE adhoc_notes IS 'Standalone sticky notes for quick capture of thoughts and reminders';

COMMENT ON COLUMN todo_items.user_id IS 'Owner of the TODO item';
COMMENT ON COLUMN todo_items.title IS 'Short title of the TODO item (required, max 255 chars)';
COMMENT ON COLUMN todo_items.description IS 'Detailed description of the TODO item (optional)';
COMMENT ON COLUMN todo_items.target_date IS 'The date this TODO item is planned for';
COMMENT ON COLUMN todo_items.visibility IS 'Controls who can see this item (public or private)';
COMMENT ON COLUMN todo_items.linked_entity_type IS 'Type of linked entity (task or subtask), null if standalone';
COMMENT ON COLUMN todo_items.linked_entity_id IS 'ID of the linked task or subtask, null if standalone';
COMMENT ON COLUMN todo_items.is_deleted IS 'Soft delete flag';

COMMENT ON COLUMN adhoc_notes.user_id IS 'Owner of the ADHOC note';
COMMENT ON COLUMN adhoc_notes.title IS 'Short title of the note (required, max 255 chars)';
COMMENT ON COLUMN adhoc_notes.content IS 'Full content of the note (optional)';
COMMENT ON COLUMN adhoc_notes.position IS 'Display order within user''s ADHOC pane (for reordering)';
COMMENT ON COLUMN adhoc_notes.color IS 'Hex color code for sticky note appearance (default: #FFEB3B)';
COMMENT ON COLUMN adhoc_notes.is_deleted IS 'Soft delete flag';

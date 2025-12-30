-- Migration: Add decision tracking fields to entity_notes table
-- Date: 2025-12-15
-- Description: Extend entity_notes table to support decision tracking

-- Add decision tracking columns
ALTER TABLE entity_notes 
ADD COLUMN is_decision BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN decision_status VARCHAR(20) DEFAULT 'Active';

-- Create index for decision queries
CREATE INDEX idx_entity_notes_decisions ON entity_notes(is_decision, decision_status) WHERE is_decision = TRUE;

-- Create index for entity decisions
CREATE INDEX idx_entity_notes_entity_decisions ON entity_notes(entity_type, entity_id, is_decision) WHERE is_decision = TRUE;

-- Update existing notes to have is_decision = FALSE (already default, but explicit)
UPDATE entity_notes SET is_decision = FALSE WHERE is_decision IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN entity_notes.is_decision IS 'Flag to indicate if this note is a decision';
COMMENT ON COLUMN entity_notes.decision_status IS 'Status of the decision: Active, Canceled, Postponed, On-Hold, Closed';
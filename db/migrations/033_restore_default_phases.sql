-- Migration: Restore Default Phases
-- Date: 2025-01-15
-- Description: Restore default phases that are required for user stories and tasks
-- These phases were removed when seed data was cleaned, but they are essential system data

-- Insert default phases if they don't already exist
-- Using ON CONFLICT to prevent duplicates if migration runs multiple times
INSERT INTO phases (name, short_description, color, display_order, is_active) VALUES
('Development', 'Software development and coding tasks', '#3498db', 1, true),
('Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2, true),
('Design', 'UI/UX and architecture design tasks', '#e67e22', 3, true),
('Testing', 'Quality assurance and testing tasks', '#1abc9c', 4, true)
ON CONFLICT (name) DO UPDATE SET
    short_description = EXCLUDED.short_description,
    color = EXCLUDED.color,
    display_order = EXCLUDED.display_order,
    is_active = true,
    is_deleted = false,
    updated_at = NOW();

-- Add comment explaining the phases
COMMENT ON TABLE phases IS 'Phases represent different stages of work in the development lifecycle. Default phases: Development, Analysis, Design, Testing. Phases are required for user stories and tasks.';


-- Migration 024: Add sample audit logs for testing
-- This migration adds sample audit log entries for existing subtasks

-- Insert sample audit logs for subtasks
INSERT INTO audit_logs (
    id, user_id, action, entity_type, entity_id, changes, created_at
) VALUES 
(
    generate_string_id('AUD', 'audit_logs_id_seq'),
    'USR-001',
    'CREATE',
    'subtask',
    'SUB-000014',
    NULL,
    NOW() - INTERVAL '2 days'
),
(
    generate_string_id('AUD', 'audit_logs_id_seq'),
    'USR-001',
    'UPDATE',
    'subtask',
    'SUB-000014',
    '{"status": {"old": "To Do", "new": "In Progress"}, "assigned_to": {"old": null, "new": "USR-001"}}'::jsonb,
    NOW() - INTERVAL '1 day'
),
(
    generate_string_id('AUD', 'audit_logs_id_seq'),
    'USR-001',
    'UPDATE',
    'subtask',
    'SUB-000014',
    '{"status": {"old": "In Progress", "new": "Done"}, "completed_at": {"old": null, "new": "2025-01-12T16:30:00Z"}}'::jsonb,
    NOW() - INTERVAL '4 hours'
);

-- Add audit logs for other subtasks if they exist
INSERT INTO audit_logs (
    id, user_id, action, entity_type, entity_id, changes, created_at
)
SELECT 
    generate_string_id('AUD', 'audit_logs_id_seq'),
    'USR-001',
    'CREATE',
    'subtask',
    s.id,
    NULL,
    s.created_at
FROM subtasks s 
WHERE s.id != 'SUB-000014' 
AND s.is_deleted = false
LIMIT 10;

-- Add some update audit logs for existing subtasks
INSERT INTO audit_logs (
    id, user_id, action, entity_type, entity_id, changes, created_at
)
SELECT 
    generate_string_id('AUD', 'audit_logs_id_seq'),
    COALESCE(s.assigned_to, 'USR-001'),
    'UPDATE',
    'subtask',
    s.id,
    ('{"status": {"old": "To Do", "new": "' || s.status || '"}}')::jsonb,
    s.updated_at
FROM subtasks s 
WHERE s.status != 'To Do'
AND s.is_deleted = false
LIMIT 5;
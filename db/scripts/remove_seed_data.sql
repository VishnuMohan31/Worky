-- Remove all seed data from the database EXCEPT admin user
-- This script deletes all data inserted by the seed migration
-- It preserves the database schema (tables, columns, etc.)
-- It keeps ONLY the admin user (admin@datalegos.com) and its client (DataLegos)

BEGIN;

-- Delete in reverse dependency order (child records first)

-- Delete dependencies
DELETE FROM dependencies;

-- Delete adhoc notes (keep admin's notes if any, but seed data doesn't have admin notes)
DELETE FROM adhoc_notes;

-- Delete todo items (keep admin's todos if any, but seed data doesn't have admin todos)
DELETE FROM todo_items;

-- Delete entity notes (temporarily disable trigger since notes are immutable)
ALTER TABLE entity_notes DISABLE TRIGGER prevent_entity_notes_delete;
DELETE FROM entity_notes;
ALTER TABLE entity_notes ENABLE TRIGGER prevent_entity_notes_delete;

-- Delete sprint task links
DELETE FROM sprint_tasks;

-- Delete sprints
DELETE FROM sprints;

-- Delete bugs
DELETE FROM bugs;

-- Delete subtasks
DELETE FROM subtasks;

-- Delete tasks
DELETE FROM tasks;

-- Delete user stories
DELETE FROM user_stories;

-- Delete usecases
DELETE FROM usecases;

-- Delete projects
DELETE FROM projects;

-- Delete programs
DELETE FROM programs;

-- Delete company settings (will be recreated if needed)
DELETE FROM company_settings;

-- Delete organizations
DELETE FROM organizations;

-- Delete users EXCEPT admin user (USR-000001, admin@datalegos.com)
DELETE FROM users WHERE id != 'USR-000001';

-- Delete clients EXCEPT DataLegos (CLI-000001) which the admin user needs
DELETE FROM clients WHERE id != 'CLI-000001';

-- NOTE: Phases are NOT deleted - they are essential system data required for user stories
-- Phases should always exist (Development, Analysis, Design, Testing)
-- If phases are missing, run migration 033_restore_default_phases.sql

-- Also delete any other seed-related data that might exist
DELETE FROM test_executions;
DELETE FROM test_runs;
DELETE FROM test_cases;
DELETE FROM reminders;
DELETE FROM notifications;
DELETE FROM notification_history;
DELETE FROM notification_preferences;
DELETE FROM chat_messages;
DELETE FROM chat_audit_logs;
DELETE FROM audit_logs;
DELETE FROM entity_history;
DELETE FROM report_snapshots;
DELETE FROM documentation;
DELETE FROM pull_requests;
DELETE FROM commits;
DELETE FROM assignments;
DELETE FROM assignment_history;
DELETE FROM team_members;
DELETE FROM teams;
DELETE FROM bug_attachments;
DELETE FROM bug_comments;
DELETE FROM bug_status_history;

COMMIT;

-- Verify deletion and admin user preservation
SELECT 
    '=== VERIFICATION ===' as info;

-- Check admin user exists
SELECT 
    id, email, full_name, role, client_id 
FROM users 
WHERE email = 'admin@datalegos.com';

-- Check DataLegos client exists
SELECT 
    id, name, is_active 
FROM clients 
WHERE id = 'CLI-000001';

-- Count remaining data
SELECT 
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM clients) as clients_count,
    (SELECT COUNT(*) FROM projects) as projects_count,
    (SELECT COUNT(*) FROM tasks) as tasks_count,
    (SELECT COUNT(*) FROM programs) as programs_count,
    (SELECT COUNT(*) FROM usecases) as usecases_count,
    (SELECT COUNT(*) FROM user_stories) as user_stories_count,
    (SELECT COUNT(*) FROM sprints) as sprints_count,
    (SELECT COUNT(*) FROM bugs) as bugs_count,
    (SELECT COUNT(*) FROM todo_items) as todo_items_count,
    (SELECT COUNT(*) FROM adhoc_notes) as adhoc_notes_count;


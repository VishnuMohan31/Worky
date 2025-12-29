-- =====================================================
-- WORKY DATABASE - SEED DATA
-- =====================================================
-- Development seed data for testing and demo
-- Only runs if database is fresh (no users exist)
-- =====================================================

DO $$
BEGIN
    -- Only seed if no users exist (fresh installation)
    IF NOT EXISTS (SELECT 1 FROM users WHERE id != 'USR-000001' LIMIT 1) THEN
        RAISE NOTICE 'Loading development seed data...';
        
        -- Update default client
        UPDATE clients SET 
            name = 'DataLegos',
            short_description = 'Internal projects and development tools',
            is_active = true
        WHERE id = 'CLI-000001';
        
        -- Insert additional clients
        INSERT INTO clients (id, name, short_description, is_active) VALUES
            ('CLI-000002', 'Acme Corp', 'Enterprise client - Manufacturing solutions', true),
            ('CLI-000003', 'TechStart Inc', 'Startup client - SaaS platform development', true)
        ON CONFLICT (id) DO NOTHING;

        -- Update default admin user password (password: password)
        UPDATE users SET 
            hashed_password = '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy',
            full_name = 'Admin User',
            role = 'Admin',
            primary_role = 'Admin'
        WHERE id = 'USR-000001';

        -- Insert additional users (password: password for all)
        INSERT INTO users (id, email, hashed_password, full_name, role, primary_role, client_id, language, theme, is_active) VALUES
            ('USR-000002', 'john@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'John Doe', 'Developer', 'Developer', 'CLI-000001', 'en', 'dark', true),
            ('USR-000003', 'jane@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Jane Smith', 'Project Manager', 'Project Manager', 'CLI-000001', 'en', 'water', true),
            ('USR-000004', 'bob@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Bob Johnson', 'Developer', 'Developer', 'CLI-000001', 'en', 'greenery', true),
            ('USR-000005', 'alice@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Alice Williams', 'DevOps', 'DevOps', 'CLI-000001', 'en', 'dracula', true),
            ('USR-000006', 'charlie@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Charlie Brown', 'Tester', 'Tester', 'CLI-000001', 'en', 'blackwhite', true),
            ('USR-000007', 'architect@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Sarah Architect', 'Architect', 'Architect', 'CLI-000001', 'en', 'snow', true),
            ('USR-000008', 'owner@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Mike Owner', 'Owner', 'Owner', 'CLI-000001', 'en', 'snow', true)
        ON CONFLICT (id) DO NOTHING;

        -- Insert programs
        INSERT INTO programs (id, client_id, name, short_description, start_date, end_date, status) VALUES
            ('PRG-000001', 'CLI-000001', 'Internal Tools', 'Development of internal productivity tools', '2025-01-01', '2025-12-31', 'In Progress'),
            ('PRG-000002', 'CLI-000002', 'Digital Transformation', 'Enterprise digital transformation initiative', '2024-06-01', '2026-06-30', 'In Progress'),
            ('PRG-000003', 'CLI-000003', 'Product Launch', 'New product development and launch', '2025-03-01', '2025-12-31', 'Planning')
        ON CONFLICT (id) DO NOTHING;

        -- Insert projects
        INSERT INTO projects (id, program_id, name, short_description, start_date, end_date, status, repository_url) VALUES
            ('PRJ-000001', 'PRG-000001', 'Worky Platform', 'Internal project management system', '2025-01-01', '2025-06-30', 'In Progress', 'https://github.com/datalegos/worky'),
            ('PRJ-000002', 'PRG-000001', 'Customer Portal', 'Self-service customer portal', '2025-02-01', '2025-08-31', 'Planning', 'https://github.com/datalegos/customer-portal'),
            ('PRJ-000003', 'PRG-000002', 'Mobile App', 'iOS and Android mobile application', '2024-11-01', '2025-05-31', 'In Progress', 'https://github.com/acme/mobile-app'),
            ('PRJ-000004', 'PRG-000001', 'Analytics Dashboard', 'Real-time analytics and reporting', '2025-01-15', '2025-07-31', 'In Progress', 'https://github.com/datalegos/analytics')
        ON CONFLICT (id) DO NOTHING;

        -- Insert usecases
        INSERT INTO usecases (id, project_id, name, short_description, priority, status) VALUES
            ('USC-000001', 'PRJ-000001', 'User Authentication', 'Secure user login and session management', 'High', 'In Progress'),
            ('USC-000002', 'PRJ-000001', 'Project Management', 'Create and manage projects with hierarchy', 'High', 'In Progress'),
            ('USC-000003', 'PRJ-000001', 'Task Tracking', 'Track tasks with assignments and progress', 'High', 'In Progress'),
            ('USC-000004', 'PRJ-000001', 'Reporting', 'Generate reports and analytics', 'Medium', 'Draft'),
            ('USC-000005', 'PRJ-000002', 'Customer Registration', 'Customer account registration', 'High', 'Draft')
        ON CONFLICT (id) DO NOTHING;

        -- Insert user stories
        INSERT INTO user_stories (id, usecase_id, title, short_description, story_points, priority, status, phase_id) VALUES
            ('UST-000001', 'USC-000001', 'User Login', 'As a user, I want to login with email and password', 5, 'High', 'Done', 'PHS-000001'),
            ('UST-000002', 'USC-000002', 'Create Project', 'As a PM, I want to create new projects', 3, 'High', 'In Progress', 'PHS-000001'),
            ('UST-000003', 'USC-000003', 'Assign Tasks', 'As a PM, I want to assign tasks to team members', 2, 'Medium', 'Backlog', 'PHS-000001'),
            ('UST-000004', 'USC-000001', 'Password Reset', 'As a user, I want to reset my password', 3, 'High', 'In Progress', 'PHS-000001'),
            ('UST-000005', 'USC-000003', 'Task Comments', 'As a user, I want to comment on tasks', 2, 'Medium', 'Done', 'PHS-000001')
        ON CONFLICT (id) DO NOTHING;

        -- Insert tasks
        INSERT INTO tasks (id, user_story_id, title, short_description, status, priority, assigned_to, estimated_hours, phase_id) VALUES
            ('TSK-000001', 'UST-000001', 'Design database schema', 'Create PostgreSQL schema for all entities', 'Done', 'High', 'USR-000002', 16, 'PHS-000001'),
            ('TSK-000002', 'UST-000001', 'Implement authentication', 'JWT-based auth with role-based access', 'Done', 'High', 'USR-000002', 24, 'PHS-000001'),
            ('TSK-000003', 'UST-000002', 'Create UI mockups', 'Design mockups for main pages', 'In Progress', 'Medium', 'USR-000004', 16, 'PHS-000003'),
            ('TSK-000004', 'UST-000002', 'Setup CI/CD pipeline', 'Configure GitHub Actions', 'In Progress', 'Medium', 'USR-000005', 12, 'PHS-000001'),
            ('TSK-000005', 'UST-000003', 'Design task assignment UI', 'Create interface for assigning tasks', 'To Do', 'Medium', 'USR-000004', 8, 'PHS-000003')
        ON CONFLICT (id) DO NOTHING;

        -- Insert subtasks
        INSERT INTO subtasks (id, task_id, title, short_description, status, assigned_to, estimated_hours, phase_id) VALUES
            ('SUB-000001', 'TSK-000001', 'Create users table', 'Design and create users table schema', 'Done', 'USR-000002', 4, 'PHS-000001'),
            ('SUB-000002', 'TSK-000001', 'Create projects table', 'Design and create projects table schema', 'Done', 'USR-000002', 4, 'PHS-000001'),
            ('SUB-000003', 'TSK-000002', 'Setup JWT library', 'Install and configure JWT library', 'Done', 'USR-000002', 2, 'PHS-000001'),
            ('SUB-000004', 'TSK-000002', 'Create login endpoint', 'Implement login API endpoint', 'Done', 'USR-000002', 8, 'PHS-000001')
        ON CONFLICT (id) DO NOTHING;

        -- Insert bugs
        INSERT INTO bugs (id, entity_type, entity_id, title, short_description, severity, priority, status, assigned_to, reported_by) VALUES
            ('BUG-000001', 'Task', 'TSK-000002', 'Login not responsive', 'Login form breaks on mobile screens', 'High', 'P1', 'Resolved', 'USR-000004', 'USR-000006'),
            ('BUG-000002', 'Task', 'TSK-000003', 'Task filter issue', 'Filter returns incorrect results', 'Medium', 'P2', 'Open', 'USR-000002', 'USR-000003')
        ON CONFLICT (id) DO NOTHING;

        -- Insert sprints
        INSERT INTO sprints (id, project_id, name, goal, start_date, end_date, status) VALUES
            ('SPR-000001', 'PRJ-000001', 'Sprint 1', 'Setup infrastructure and auth', '2025-01-01', '2025-01-14', 'Completed'),
            ('SPR-000002', 'PRJ-000001', 'Sprint 2', 'Core features development', '2025-01-15', '2025-01-28', 'Active'),
            ('SPR-000003', 'PRJ-000001', 'Sprint 3', 'Testing and bug fixes', '2025-01-29', '2025-02-11', 'Planning')
        ON CONFLICT (id) DO NOTHING;

        -- Update sequences to start after seed data
        PERFORM setval('clients_id_seq', 4, false);
        PERFORM setval('users_id_seq', 9, false);
        PERFORM setval('programs_id_seq', 4, false);
        PERFORM setval('projects_id_seq', 5, false);
        PERFORM setval('usecases_id_seq', 6, false);
        PERFORM setval('user_stories_id_seq', 6, false);
        PERFORM setval('tasks_id_seq', 6, false);
        PERFORM setval('subtasks_id_seq', 5, false);
        PERFORM setval('bugs_id_seq', 3, false);
        PERFORM setval('sprints_id_seq', 4, false);

        RAISE NOTICE 'Development seed data loaded successfully!';
    ELSE
        RAISE NOTICE 'Users already exist - skipping seed data';
    END IF;
END $$;


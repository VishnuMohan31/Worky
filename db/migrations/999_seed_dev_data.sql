-- Seed development data
-- This migration loads comprehensive sample data for development and demo environments
-- It will only run if the database is empty (no users exist)

DO $$
DECLARE
    phase_dev_id VARCHAR(20);
    phase_analysis_id VARCHAR(20);
    phase_design_id VARCHAR(20);
    phase_testing_id VARCHAR(20);
BEGIN
    -- Only seed if no users exist (fresh installation)
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        RAISE NOTICE 'Loading development seed data...';
        
        -- Get phase IDs from the default phases (created in migration 007)
        SELECT id INTO phase_dev_id FROM phases WHERE name = 'Development' LIMIT 1;
        SELECT id INTO phase_analysis_id FROM phases WHERE name = 'Analysis' LIMIT 1;
        SELECT id INTO phase_design_id FROM phases WHERE name = 'Design' LIMIT 1;
        SELECT id INTO phase_testing_id FROM phases WHERE name = 'Testing' LIMIT 1;
        
        -- If phases don't exist, create them
        IF phase_dev_id IS NULL THEN
            INSERT INTO phases (id, name, short_description, color, display_order) VALUES
            ('PHS-000001', 'Development', 'Software development and coding tasks', '#3498db', 1),
            ('PHS-000002', 'Analysis', 'Requirements analysis and research tasks', '#9b59b6', 2),
            ('PHS-000003', 'Design', 'UI/UX and architecture design tasks', '#e67e22', 3),
            ('PHS-000004', 'Testing', 'Quality assurance and testing tasks', '#1abc9c', 4);
            
            phase_dev_id := 'PHS-000001';
            phase_analysis_id := 'PHS-000002';
            phase_design_id := 'PHS-000003';
            phase_testing_id := 'PHS-000004';
        END IF;
        
        -- Insert clients
        INSERT INTO clients (id, name, short_description, is_active) VALUES
        ('CLI-000001', 'DataLegos', 'Internal projects and tools', true),
        ('CLI-000002', 'Acme Corp', 'Enterprise client - Manufacturing', true),
        ('CLI-000003', 'TechStart Inc', 'Startup client - SaaS platform', true),
        ('CLI-000004', 'Global Finance Ltd', 'Financial services client', true);

        -- Insert users (password is 'password' hashed with bcrypt)
        -- Hash: $2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy
        -- Valid roles: 'Admin', 'Developer', 'Tester', 'Architect', 'Designer'
        INSERT INTO users (id, email, hashed_password, full_name, role, client_id, language, theme) VALUES
        ('USR-000001', 'admin@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Admin User', 'Admin', 'CLI-000001', 'en', 'snow'),
        ('USR-000002', 'john@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'John Doe', 'Developer', 'CLI-000001', 'en', 'dark'),
        ('USR-000003', 'jane@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Jane Smith', 'Architect', 'CLI-000001', 'en', 'water'),
        ('USR-000004', 'bob@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Bob Johnson', 'Developer', 'CLI-000001', 'en', 'greenery'),
        ('USR-000005', 'alice@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Alice Williams', 'Developer', 'CLI-000001', 'en', 'dracula'),
        ('USR-000006', 'charlie@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Charlie Brown', 'Tester', 'CLI-000001', 'en', 'blackwhite'),
        ('USR-000007', 'sarah@acme.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Sarah Connor', 'Architect', 'CLI-000002', 'en', 'snow'),
        ('USR-000008', 'mike@techstart.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Mike Ross', 'Developer', 'CLI-000003', 'en', 'dark'),
        ('USR-000009', 'lisa@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Lisa Designer', 'Designer', 'CLI-000001', 'en', 'water');

        -- Insert organizations
        INSERT INTO organizations (id, name, description, is_active) VALUES
        ('ORG-000001', 'Engineering', 'Engineering and development teams', true),
        ('ORG-000002', 'Product', 'Product management and design', true),
        ('ORG-000003', 'Operations', 'DevOps and infrastructure', true);

        -- Insert company settings
        INSERT INTO company_settings (id, client_id, company_name, company_logo_url, primary_color, secondary_color) VALUES
        ('CMP-000001', 'CLI-000001', 'DataLegos', 'https://example.com/logo.png', '#3B82F6', '#10B981');

        -- Insert programs
        INSERT INTO programs (id, client_id, name, short_description, start_date, end_date, status) VALUES
        ('PRG-000001', 'CLI-000001', 'Internal Tools', 'Development of internal productivity tools', '2025-01-01', '2025-12-31', 'In Progress'),
        ('PRG-000002', 'CLI-000002', 'Digital Transformation', 'Enterprise-wide digital transformation initiative', '2024-06-01', '2026-06-30', 'In Progress'),
        ('PRG-000003', 'CLI-000003', 'Product Launch', 'New product development and launch', '2025-03-01', '2025-12-31', 'Planning');

        -- Insert projects
        INSERT INTO projects (id, program_id, name, short_description, start_date, end_date, status, repository_url) VALUES
        ('PRJ-000001', 'PRG-000001', 'Worky Platform', 'Internal project management system', '2025-01-01', '2025-06-30', 'In Progress', 'https://github.com/datalegos/worky'),
        ('PRJ-000002', 'PRG-000001', 'Customer Portal', 'Self-service customer portal', '2025-02-01', '2025-08-31', 'Planning', 'https://github.com/datalegos/customer-portal'),
        ('PRJ-000003', 'PRG-000002', 'Mobile App', 'iOS and Android mobile application', '2024-11-01', '2025-05-31', 'In Progress', 'https://github.com/acme/mobile-app'),
        ('PRJ-000004', 'PRG-000001', 'Analytics Dashboard', 'Real-time analytics and reporting dashboard', '2025-01-15', '2025-07-31', 'In Progress', 'https://github.com/datalegos/analytics'),
        ('PRJ-000005', 'PRG-000003', 'E-commerce Platform', 'Online shopping platform', '2025-03-01', '2025-11-30', 'Planning', 'https://github.com/techstart/ecommerce');

        -- Insert usecases
        INSERT INTO usecases (id, project_id, name, short_description, priority, status) VALUES
        ('USC-000001', 'PRJ-000001', 'User Authentication', 'Secure user login and session management', 'High', 'In Progress'),
        ('USC-000002', 'PRJ-000001', 'Project Management', 'Create and manage projects with hierarchy', 'High', 'In Progress'),
        ('USC-000003', 'PRJ-000001', 'Task Tracking', 'Track tasks with assignments and progress', 'High', 'In Progress'),
        ('USC-000004', 'PRJ-000001', 'Reporting', 'Generate reports and analytics', 'Medium', 'To Do'),
        ('USC-000005', 'PRJ-000002', 'Customer Registration', 'Allow customers to register and create accounts', 'High', 'Planning'),
        ('USC-000006', 'PRJ-000003', 'Push Notifications', 'Send push notifications to mobile users', 'Medium', 'In Progress'),
        ('USC-000007', 'PRJ-000004', 'Data Visualization', 'Interactive charts and graphs', 'High', 'In Progress');

        -- Insert user stories (using phase variables)
        INSERT INTO user_stories (id, usecase_id, name, short_description, acceptance_criteria, story_points, priority, status, phase_id) VALUES
        ('UST-000001', 'USC-000001', 'User Login', 'As a user, I want to login with email and password', 'User can enter credentials and access dashboard', 5, 'High', 'Done', phase_dev_id),
        ('UST-000002', 'USC-000002', 'Create Project', 'As a PM, I want to create new projects', 'PM can create project with name, dates, and description', 3, 'High', 'In Progress', phase_dev_id),
        ('UST-000003', 'USC-000003', 'Assign Tasks', 'As a PM, I want to assign tasks to team members', 'PM can select user and assign task', 2, 'Medium', 'To Do', phase_analysis_id),
        ('UST-000004', 'USC-000001', 'Password Reset', 'As a user, I want to reset my password if I forget it', 'User receives email with reset link', 3, 'High', 'In Progress', phase_dev_id),
        ('UST-000005', 'USC-000003', 'Task Comments', 'As a user, I want to comment on tasks', 'Users can add and view comments on tasks', 2, 'Medium', 'Done', phase_dev_id),
        ('UST-000006', 'USC-000004', 'Export Reports', 'As a manager, I want to export reports to PDF', 'Reports can be downloaded as PDF files', 5, 'Medium', 'To Do', phase_analysis_id),
        ('UST-000007', 'USC-000005', 'Email Verification', 'As a customer, I want to verify my email address', 'Verification email sent and link works', 3, 'High', 'Planning', phase_analysis_id),
        ('UST-000008', 'USC-000006', 'Notification Settings', 'As a user, I want to configure notification preferences', 'Users can enable/disable notification types', 2, 'Low', 'To Do', phase_analysis_id),
        ('UST-000009', 'USC-000007', 'Real-time Charts', 'As a user, I want to see real-time data updates', 'Charts update automatically without refresh', 8, 'High', 'In Progress', phase_dev_id),
        ('UST-000010', 'USC-000003', 'Task Dependencies', 'As a PM, I want to set task dependencies', 'Tasks can be linked with dependency relationships', 5, 'Medium', 'Planning', phase_analysis_id);

        -- Insert tasks (using phase variables)
        INSERT INTO tasks (id, user_story_id, name, short_description, status, priority, assigned_to, estimated_hours, actual_hours, start_date, due_date, phase_id) VALUES
        ('TSK-000001', 'UST-000001', 'Design database schema', 'Create PostgreSQL schema for all entities', 'Done', 'High', 'USR-000002', 16, 14, '2025-01-01', '2025-01-05', phase_dev_id),
        ('TSK-000002', 'UST-000001', 'Implement authentication', 'JWT-based auth with role-based access control', 'Done', 'High', 'USR-000002', 24, 22, '2025-01-06', '2025-01-15', phase_dev_id),
        ('TSK-000003', 'UST-000002', 'Create UI mockups', 'Design mockups for all main pages', 'In Progress', 'Medium', 'USR-000004', 16, 8, '2025-01-10', '2025-01-20', phase_design_id),
        ('TSK-000004', 'UST-000002', 'Setup CI/CD pipeline', 'Configure GitHub Actions for automated deployment', 'In Progress', 'Medium', 'USR-000005', 12, 8, '2025-01-08', '2025-01-18', phase_dev_id),
        ('TSK-000005', 'UST-000003', 'Design task assignment UI', 'Create interface for assigning tasks', 'To Do', 'Medium', 'USR-000004', 8, 0, '2025-01-15', '2025-01-22', phase_design_id),
        ('TSK-000006', 'UST-000004', 'Implement password reset API', 'Create API endpoints for password reset', 'In Progress', 'High', 'USR-000002', 12, 6, '2025-01-12', '2025-01-19', phase_dev_id),
        ('TSK-000007', 'UST-000004', 'Design password reset email template', 'Create HTML email template', 'Done', 'Medium', 'USR-000009', 4, 3, '2025-01-10', '2025-01-12', phase_design_id),
        ('TSK-000008', 'UST-000005', 'Add comment functionality', 'Implement comment CRUD operations', 'Done', 'Medium', 'USR-000002', 8, 7, '2025-01-05', '2025-01-10', phase_dev_id),
        ('TSK-000009', 'UST-000009', 'Setup WebSocket connection', 'Implement real-time data streaming', 'In Progress', 'High', 'USR-000002', 16, 10, '2025-01-20', '2025-02-05', phase_dev_id),
        ('TSK-000010', 'UST-000009', 'Create chart components', 'Build reusable chart components', 'In Progress', 'High', 'USR-000009', 20, 12, '2025-01-22', '2025-02-08', phase_design_id),
        ('TSK-000011', 'UST-000006', 'Research PDF libraries', 'Evaluate PDF generation libraries', 'To Do', 'Low', 'USR-000002', 4, 0, '2025-02-01', '2025-02-05', phase_analysis_id),
        ('TSK-000012', 'UST-000001', 'Write authentication tests', 'Unit and integration tests for auth', 'Done', 'High', 'USR-000006', 12, 11, '2025-01-08', '2025-01-14', phase_testing_id);

        -- Insert subtasks (phase_id is nullable, so we can omit it)
        INSERT INTO subtasks (id, task_id, name, short_description, status, assigned_to, estimated_hours, actual_hours) VALUES
        ('SUB-000001', 'TSK-000001', 'Create users table', 'Design and create users table schema', 'Done', 'USR-000002', 4, 3),
        ('SUB-000002', 'TSK-000001', 'Create projects table', 'Design and create projects table schema', 'Done', 'USR-000002', 4, 4),
        ('SUB-000003', 'TSK-000001', 'Create tasks table', 'Design and create tasks table schema', 'Done', 'USR-000002', 4, 3),
        ('SUB-000004', 'TSK-000002', 'Setup JWT library', 'Install and configure JWT library', 'Done', 'USR-000002', 2, 2),
        ('SUB-000005', 'TSK-000002', 'Create login endpoint', 'Implement login API endpoint', 'Done', 'USR-000002', 8, 7),
        ('SUB-000006', 'TSK-000002', 'Add role-based middleware', 'Implement RBAC middleware', 'Done', 'USR-000002', 6, 5),
        ('SUB-000007', 'TSK-000003', 'Design dashboard mockup', 'Create dashboard UI mockup', 'In Progress', 'USR-000009', 4, 2),
        ('SUB-000008', 'TSK-000003', 'Design project list mockup', 'Create project list UI mockup', 'In Progress', 'USR-000009', 4, 2),
        ('SUB-000009', 'TSK-000009', 'Setup Socket.IO', 'Install and configure Socket.IO', 'Done', 'USR-000002', 4, 3),
        ('SUB-000010', 'TSK-000009', 'Implement event handlers', 'Create WebSocket event handlers', 'In Progress', 'USR-000002', 8, 5);

        -- Insert bugs (using correct column names from the new schema)
        INSERT INTO bugs (id, task_id, title, description, category, severity, priority, status, assignee_id, reporter_id, environment) VALUES
        ('BUG-000001', 'TSK-000002', 'Login page not responsive on mobile', 'The login form breaks on screens smaller than 768px', 'UI', 'High', 'P1', 'Closed', 'USR-000009', 'USR-000006', 'Mobile Safari iOS 17'),
        ('BUG-000002', 'TSK-000003', 'Task filter not working', 'Filtering tasks by status returns incorrect results', 'Backend', 'Medium', 'P2', 'In Progress', 'USR-000002', 'USR-000003', 'Chrome 120'),
        ('BUG-000003', 'TSK-000008', 'Comments not saving', 'Comment submission fails silently', 'Backend', 'High', 'P1', 'Closed', 'USR-000002', 'USR-000006', 'Firefox 121'),
        ('BUG-000004', 'TSK-000009', 'WebSocket connection drops', 'Connection drops after 5 minutes of inactivity', 'Backend', 'Medium', 'P1', 'New', 'USR-000002', 'USR-000005', 'Production'),
        ('BUG-000005', 'TSK-000010', 'Chart rendering issue', 'Charts not rendering on Safari', 'UI', 'Low', 'P2', 'New', 'USR-000009', 'USR-000006', 'Safari 17');

        -- Insert sprints
        INSERT INTO sprints (id, project_id, name, goal, start_date, end_date, status) VALUES
        ('SPR-000001', 'PRJ-000001', 'Sprint 1', 'Setup infrastructure and authentication', '2025-01-01', '2025-01-14', 'Completed'),
        ('SPR-000002', 'PRJ-000001', 'Sprint 2', 'Core features and UI development', '2025-01-15', '2025-01-28', 'Active'),
        ('SPR-000003', 'PRJ-000001', 'Sprint 3', 'Testing and bug fixes', '2025-01-29', '2025-02-11', 'Planning'),
        ('SPR-000004', 'PRJ-000003', 'Mobile Sprint 1', 'Basic app structure and navigation', '2024-11-01', '2024-11-14', 'Completed'),
        ('SPR-000005', 'PRJ-000004', 'Analytics Sprint 1', 'Dashboard foundation', '2025-01-15', '2025-01-28', 'Active');

        -- Link tasks to sprint
        INSERT INTO sprint_tasks (sprint_id, task_id) VALUES
        ('SPR-000001', 'TSK-000001'),
        ('SPR-000001', 'TSK-000002'),
        ('SPR-000001', 'TSK-000007'),
        ('SPR-000001', 'TSK-000008'),
        ('SPR-000002', 'TSK-000003'),
        ('SPR-000002', 'TSK-000004'),
        ('SPR-000002', 'TSK-000006'),
        ('SPR-000005', 'TSK-000009'),
        ('SPR-000005', 'TSK-000010');

        -- NOTE: commits, pull_requests, and documentation tables still use UUID format
        -- from migration 002 and were never converted to string IDs. 
        -- Seed data for these tables is skipped to avoid type mismatches.
        -- These tables will be populated through the application when needed.

        -- Insert entity notes (using correct column: note_text)
        INSERT INTO entity_notes (entity_type, entity_id, note_text, created_by) VALUES
        ('Task', 'TSK-000002', 'Remember to update the API documentation after merging', 'USR-000003'),
        ('Task', 'TSK-000004', 'Need to configure secrets in GitHub repository settings', 'USR-000005'),
        ('Bug', 'BUG-000002', 'This might be related to the database query optimization', 'USR-000002'),
        ('UserStory', 'UST-000009', 'Consider using Chart.js or D3.js for visualization', 'USR-000009'),
        ('Project', 'PRJ-000001', 'Target launch date is June 30, 2025', 'USR-000001');

        -- Insert TODO items (using correct schema: target_date, visibility)
        INSERT INTO todo_items (user_id, title, description, target_date, visibility) VALUES
        ('USR-000001', 'Review Q1 roadmap', 'Review and approve Q1 product roadmap', '2025-01-20', 'public'),
        ('USR-000002', 'Code review for PR #2', 'Review Alice''s CI/CD pipeline PR', '2025-01-18', 'public'),
        ('USR-000002', 'Update dependencies', 'Update npm packages to latest versions', '2025-01-25', 'private'),
        ('USR-000003', 'Sprint planning meeting', 'Prepare agenda for Sprint 3 planning', '2025-01-28', 'public'),
        ('USR-000009', 'Design system documentation', 'Document UI component library', '2025-02-01', 'public'),
        ('USR-000005', 'Server maintenance', 'Schedule server maintenance window', '2025-01-22', 'public'),
        ('USR-000006', 'Write test cases', 'Create test cases for new features', '2025-01-19', 'public');

        -- Insert adhoc notes (correct columns: title, content, position, color)
        INSERT INTO adhoc_notes (user_id, title, content, position, color) VALUES
        ('USR-000001', 'Meeting Notes - Jan 15', 'Discussed project priorities and resource allocation', 1, '#FFEB3B'),
        ('USR-000002', 'Code Snippet - JWT Middleware', 'const verifyToken = (req, res, next) => { ... }', 2, '#4CAF50'),
        ('USR-000003', 'Sprint Retrospective', 'What went well: Good collaboration\nWhat to improve: Better estimation', 3, '#2196F3'),
        ('USR-000009', 'Design Ideas', 'Consider using a card-based layout for the dashboard', 4, '#FF9800'),
        ('USR-000005', 'Server Configuration', 'Production server: 4 CPU, 16GB RAM, Ubuntu 22.04', 5, '#9C27B0');

        -- Insert dependencies (using correct dependency_type values)
        -- Valid types: 'finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish'
        INSERT INTO dependencies (entity_type, entity_id, depends_on_type, depends_on_id, dependency_type) VALUES
        ('Task', 'TSK-000003', 'Task', 'TSK-000001', 'finish_to_start'),
        ('Task', 'TSK-000006', 'Task', 'TSK-000002', 'finish_to_start'),
        ('Task', 'TSK-000010', 'Task', 'TSK-000009', 'finish_to_start'),
        ('UserStory', 'UST-000004', 'UserStory', 'UST-000001', 'start_to_start'),
        ('UserStory', 'UST-000010', 'UserStory', 'UST-000003', 'finish_to_start');

        RAISE NOTICE 'Development seed data loaded successfully!';
    ELSE
        RAISE NOTICE 'Users already exist - skipping seed data';
    END IF;
END $$;

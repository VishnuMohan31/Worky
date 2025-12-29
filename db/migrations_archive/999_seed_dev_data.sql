-- Seed development data
-- This migration loads comprehensive sample data for development and demo environments
-- It will only run if the database is empty (no users exist)

DO $$
BEGIN
    -- Only seed if no users exist (fresh installation)
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        RAISE NOTICE 'Loading development seed data...';
        
        -- Insert clients
        INSERT INTO clients (id, name, description, is_active) VALUES
        ('CLI-001', 'DataLegos', 'Internal projects and tools', true),
        ('CLI-002', 'Acme Corp', 'Enterprise client - Manufacturing', true),
        ('CLI-003', 'TechStart Inc', 'Startup client - SaaS platform', true),
        ('CLI-004', 'Global Finance Ltd', 'Financial services client', true);

        -- Insert users (password is 'password' hashed with bcrypt)
        -- Hash: $2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy
        INSERT INTO users (id, email, hashed_password, full_name, role, client_id, language, theme) VALUES
        ('USR-001', 'admin@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Admin User', 'Admin', 'CLI-001', 'en', 'snow'),
        ('USR-002', 'john@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'John Doe', 'Developer', 'CLI-001', 'en', 'dark'),
        ('USR-003', 'jane@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Jane Smith', 'Project Manager', 'CLI-001', 'en', 'water'),
        ('USR-004', 'bob@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Bob Johnson', 'Developer', 'CLI-001', 'en', 'greenery'),
        ('USR-005', 'alice@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Alice Williams', 'DevOps', 'CLI-001', 'en', 'dracula'),
        ('USR-006', 'charlie@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Charlie Brown', 'Tester', 'CLI-001', 'en', 'blackwhite'),
        ('USR-007', 'sarah@acme.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Sarah Connor', 'Project Manager', 'CLI-002', 'en', 'snow'),
        ('USR-008', 'mike@techstart.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Mike Ross', 'Developer', 'CLI-003', 'en', 'dark');

        -- Insert organizations
        INSERT INTO organizations (id, name, description, is_active) VALUES
        ('ORG-001', 'Engineering', 'Engineering and development teams', true),
        ('ORG-002', 'Product', 'Product management and design', true),
        ('ORG-003', 'Operations', 'DevOps and infrastructure', true);

        -- Insert company settings
        INSERT INTO company_settings (id, client_id, company_name, logo_url, primary_color, secondary_color) VALUES
        ('CMP-001', 'CLI-001', 'DataLegos', 'https://example.com/logo.png', '#3B82F6', '#10B981');

        -- Insert phases
        INSERT INTO phases (id, name, description, color, sort_order) VALUES
        ('PHS-001', 'Planning', 'Initial planning and requirements gathering', '#6366F1', 1),
        ('PHS-002', 'Development', 'Active development phase', '#3B82F6', 2),
        ('PHS-003', 'Testing', 'Quality assurance and testing', '#F59E0B', 3),
        ('PHS-004', 'Deployment', 'Production deployment', '#10B981', 4),
        ('PHS-005', 'Maintenance', 'Post-deployment maintenance', '#6B7280', 5);

        -- Insert programs
        INSERT INTO programs (id, client_id, name, description, start_date, end_date, status) VALUES
        ('PRG-001', 'CLI-001', 'Internal Tools', 'Development of internal productivity tools', '2025-01-01', '2025-12-31', 'In Progress'),
        ('PRG-002', 'CLI-002', 'Digital Transformation', 'Enterprise-wide digital transformation initiative', '2024-06-01', '2026-06-30', 'In Progress'),
        ('PRG-003', 'CLI-003', 'Product Launch', 'New product development and launch', '2025-03-01', '2025-12-31', 'Planning');

        -- Insert projects
        INSERT INTO projects (id, program_id, name, description, start_date, end_date, status, repository_url) VALUES
        ('PRJ-001', 'PRG-001', 'Worky Platform', 'Internal project management system', '2025-01-01', '2025-06-30', 'In Progress', 'https://github.com/datalegos/worky'),
        ('PRJ-002', 'PRG-001', 'Customer Portal', 'Self-service customer portal', '2025-02-01', '2025-08-31', 'Planning', 'https://github.com/datalegos/customer-portal'),
        ('PRJ-003', 'PRG-002', 'Mobile App', 'iOS and Android mobile application', '2024-11-01', '2025-05-31', 'In Progress', 'https://github.com/acme/mobile-app'),
        ('PRJ-004', 'PRG-001', 'Analytics Dashboard', 'Real-time analytics and reporting dashboard', '2025-01-15', '2025-07-31', 'In Progress', 'https://github.com/datalegos/analytics'),
        ('PRJ-005', 'PRG-003', 'E-commerce Platform', 'Online shopping platform', '2025-03-01', '2025-11-30', 'Planning', 'https://github.com/techstart/ecommerce');

        -- Insert usecases
        INSERT INTO usecases (id, project_id, name, description, priority, status) VALUES
        ('USC-001', 'PRJ-001', 'User Authentication', 'Secure user login and session management', 'High', 'In Progress'),
        ('USC-002', 'PRJ-001', 'Project Management', 'Create and manage projects with hierarchy', 'High', 'In Progress'),
        ('USC-003', 'PRJ-001', 'Task Tracking', 'Track tasks with assignments and progress', 'High', 'In Progress'),
        ('USC-004', 'PRJ-001', 'Reporting', 'Generate reports and analytics', 'Medium', 'To Do'),
        ('USC-005', 'PRJ-002', 'Customer Registration', 'Allow customers to register and create accounts', 'High', 'Planning'),
        ('USC-006', 'PRJ-003', 'Push Notifications', 'Send push notifications to mobile users', 'Medium', 'In Progress'),
        ('USC-007', 'PRJ-004', 'Data Visualization', 'Interactive charts and graphs', 'High', 'In Progress');

        -- Insert user stories
        INSERT INTO user_stories (id, usecase_id, title, description, acceptance_criteria, story_points, priority, status, phase_id) VALUES
        ('UST-001', 'USC-001', 'User Login', 'As a user, I want to login with email and password', 'User can enter credentials and access dashboard', 5, 'High', 'Done', 'PHS-004'),
        ('UST-002', 'USC-002', 'Create Project', 'As a PM, I want to create new projects', 'PM can create project with name, dates, and description', 3, 'High', 'In Progress', 'PHS-002'),
        ('UST-003', 'USC-003', 'Assign Tasks', 'As a PM, I want to assign tasks to team members', 'PM can select user and assign task', 2, 'Medium', 'To Do', 'PHS-001'),
        ('UST-004', 'USC-001', 'Password Reset', 'As a user, I want to reset my password if I forget it', 'User receives email with reset link', 3, 'High', 'In Progress', 'PHS-002'),
        ('UST-005', 'USC-003', 'Task Comments', 'As a user, I want to comment on tasks', 'Users can add and view comments on tasks', 2, 'Medium', 'Done', 'PHS-004'),
        ('UST-006', 'USC-004', 'Export Reports', 'As a manager, I want to export reports to PDF', 'Reports can be downloaded as PDF files', 5, 'Medium', 'To Do', 'PHS-001'),
        ('UST-007', 'USC-005', 'Email Verification', 'As a customer, I want to verify my email address', 'Verification email sent and link works', 3, 'High', 'Planning', 'PHS-001'),
        ('UST-008', 'USC-006', 'Notification Settings', 'As a user, I want to configure notification preferences', 'Users can enable/disable notification types', 2, 'Low', 'To Do', 'PHS-001'),
        ('UST-009', 'USC-007', 'Real-time Charts', 'As a user, I want to see real-time data updates', 'Charts update automatically without refresh', 8, 'High', 'In Progress', 'PHS-002'),
        ('UST-010', 'USC-003', 'Task Dependencies', 'As a PM, I want to set task dependencies', 'Tasks can be linked with dependency relationships', 5, 'Medium', 'Planning', 'PHS-001');

        -- Insert tasks
        INSERT INTO tasks (id, user_story_id, title, description, status, priority, assigned_to, estimated_hours, actual_hours, start_date, due_date, phase_id) VALUES
        ('TSK-001', 'UST-001', 'Design database schema', 'Create PostgreSQL schema for all entities', 'Done', 'High', 'USR-002', 16, 14, '2025-01-01', '2025-01-05', 'PHS-004'),
        ('TSK-002', 'UST-001', 'Implement authentication', 'JWT-based auth with role-based access control', 'Done', 'High', 'USR-002', 24, 22, '2025-01-06', '2025-01-15', 'PHS-004'),
        ('TSK-003', 'UST-002', 'Create UI mockups', 'Design mockups for all main pages', 'In Progress', 'Medium', 'USR-004', 16, 8, '2025-01-10', '2025-01-20', 'PHS-002'),
        ('TSK-004', 'UST-002', 'Setup CI/CD pipeline', 'Configure GitHub Actions for automated deployment', 'In Progress', 'Medium', 'USR-005', 12, 8, '2025-01-08', '2025-01-18', 'PHS-002'),
        ('TSK-005', 'UST-003', 'Design task assignment UI', 'Create interface for assigning tasks', 'To Do', 'Medium', 'USR-004', 8, 0, '2025-01-15', '2025-01-22', 'PHS-001'),
        ('TSK-006', 'UST-004', 'Implement password reset API', 'Create API endpoints for password reset', 'In Progress', 'High', 'USR-002', 12, 6, '2025-01-12', '2025-01-19', 'PHS-002'),
        ('TSK-007', 'UST-004', 'Design password reset email template', 'Create HTML email template', 'Done', 'Medium', 'USR-004', 4, 3, '2025-01-10', '2025-01-12', 'PHS-004'),
        ('TSK-008', 'UST-005', 'Add comment functionality', 'Implement comment CRUD operations', 'Done', 'Medium', 'USR-002', 8, 7, '2025-01-05', '2025-01-10', 'PHS-004'),
        ('TSK-009', 'UST-009', 'Setup WebSocket connection', 'Implement real-time data streaming', 'In Progress', 'High', 'USR-002', 16, 10, '2025-01-20', '2025-02-05', 'PHS-002'),
        ('TSK-010', 'UST-009', 'Create chart components', 'Build reusable chart components', 'In Progress', 'High', 'USR-004', 20, 12, '2025-01-22', '2025-02-08', 'PHS-002'),
        ('TSK-011', 'UST-006', 'Research PDF libraries', 'Evaluate PDF generation libraries', 'To Do', 'Low', 'USR-002', 4, 0, '2025-02-01', '2025-02-05', 'PHS-001'),
        ('TSK-012', 'UST-001', 'Write authentication tests', 'Unit and integration tests for auth', 'Done', 'High', 'USR-006', 12, 11, '2025-01-08', '2025-01-14', 'PHS-003');

        -- Insert subtasks
        INSERT INTO subtasks (id, task_id, title, description, status, assigned_to, estimated_hours, actual_hours) VALUES
        ('SUB-001', 'TSK-001', 'Create users table', 'Design and create users table schema', 'Done', 'USR-002', 4, 3),
        ('SUB-002', 'TSK-001', 'Create projects table', 'Design and create projects table schema', 'Done', 'USR-002', 4, 4),
        ('SUB-003', 'TSK-001', 'Create tasks table', 'Design and create tasks table schema', 'Done', 'USR-002', 4, 3),
        ('SUB-004', 'TSK-002', 'Setup JWT library', 'Install and configure JWT library', 'Done', 'USR-002', 2, 2),
        ('SUB-005', 'TSK-002', 'Create login endpoint', 'Implement login API endpoint', 'Done', 'USR-002', 8, 7),
        ('SUB-006', 'TSK-002', 'Add role-based middleware', 'Implement RBAC middleware', 'Done', 'USR-002', 6, 5),
        ('SUB-007', 'TSK-003', 'Design dashboard mockup', 'Create dashboard UI mockup', 'In Progress', 'USR-004', 4, 2),
        ('SUB-008', 'TSK-003', 'Design project list mockup', 'Create project list UI mockup', 'In Progress', 'USR-004', 4, 2),
        ('SUB-009', 'TSK-009', 'Setup Socket.IO', 'Install and configure Socket.IO', 'Done', 'USR-002', 4, 3),
        ('SUB-010', 'TSK-009', 'Implement event handlers', 'Create WebSocket event handlers', 'In Progress', 'USR-002', 8, 5);

        -- Insert bugs
        INSERT INTO bugs (id, task_id, title, description, severity, priority, status, assigned_to, reported_by, environment) VALUES
        ('BUG-001', 'TSK-002', 'Login page not responsive on mobile', 'The login form breaks on screens smaller than 768px', 'High', 'High', 'Resolved', 'USR-004', 'USR-006', 'Mobile Safari iOS 17'),
        ('BUG-002', 'TSK-003', 'Task filter not working', 'Filtering tasks by status returns incorrect results', 'Medium', 'Medium', 'In Progress', 'USR-002', 'USR-003', 'Chrome 120'),
        ('BUG-003', 'TSK-008', 'Comments not saving', 'Comment submission fails silently', 'High', 'High', 'Resolved', 'USR-002', 'USR-006', 'Firefox 121'),
        ('BUG-004', 'TSK-009', 'WebSocket connection drops', 'Connection drops after 5 minutes of inactivity', 'Medium', 'High', 'Open', 'USR-002', 'USR-005', 'Production'),
        ('BUG-005', 'TSK-010', 'Chart rendering issue', 'Charts not rendering on Safari', 'Low', 'Medium', 'Open', 'USR-004', 'USR-006', 'Safari 17');

        -- Insert sprints
        INSERT INTO sprints (id, project_id, name, goal, start_date, end_date, status) VALUES
        ('SPR-001', 'PRJ-001', 'Sprint 1', 'Setup infrastructure and authentication', '2025-01-01', '2025-01-14', 'Completed'),
        ('SPR-002', 'PRJ-001', 'Sprint 2', 'Core features and UI development', '2025-01-15', '2025-01-28', 'Active'),
        ('SPR-003', 'PRJ-001', 'Sprint 3', 'Testing and bug fixes', '2025-01-29', '2025-02-11', 'Planning'),
        ('SPR-004', 'PRJ-003', 'Mobile Sprint 1', 'Basic app structure and navigation', '2024-11-01', '2024-11-14', 'Completed'),
        ('SPR-005', 'PRJ-004', 'Analytics Sprint 1', 'Dashboard foundation', '2025-01-15', '2025-01-28', 'Active');

        -- Link tasks to sprint
        INSERT INTO sprint_tasks (sprint_id, task_id) VALUES
        ('SPR-001', 'TSK-001'),
        ('SPR-001', 'TSK-002'),
        ('SPR-001', 'TSK-007'),
        ('SPR-001', 'TSK-008'),
        ('SPR-002', 'TSK-003'),
        ('SPR-002', 'TSK-004'),
        ('SPR-002', 'TSK-006'),
        ('SPR-005', 'TSK-009'),
        ('SPR-005', 'TSK-010');

        -- Insert commits
        INSERT INTO commits (task_id, repository, commit_hash, author, author_email, message, committed_at, branch) VALUES
        ('TSK-001', 'worky', 'abc123def456', 'John Doe', 'john@datalegos.com', 'feat: Add database schema #TSK-001', '2025-01-05 10:30:00+00', 'main'),
        ('TSK-002', 'worky', 'def456ghi789', 'John Doe', 'john@datalegos.com', 'feat: Implement JWT authentication #TSK-002', '2025-01-12 14:20:00+00', 'feature/auth'),
        ('TSK-002', 'worky', 'ghi789jkl012', 'John Doe', 'john@datalegos.com', 'fix: Add password validation #TSK-002', '2025-01-13 09:15:00+00', 'feature/auth'),
        ('TSK-004', 'worky', 'jkl012mno345', 'Alice Williams', 'alice@datalegos.com', 'ci: Setup GitHub Actions workflow #TSK-004', '2025-01-10 16:45:00+00', 'main'),
        ('TSK-006', 'worky', 'mno345pqr678', 'John Doe', 'john@datalegos.com', 'feat: Add password reset endpoint #TSK-006', '2025-01-15 11:20:00+00', 'feature/password-reset'),
        ('TSK-008', 'worky', 'pqr678stu901', 'John Doe', 'john@datalegos.com', 'feat: Implement comment system #TSK-008', '2025-01-09 14:30:00+00', 'feature/comments'),
        ('TSK-009', 'analytics', 'stu901vwx234', 'John Doe', 'john@datalegos.com', 'feat: Setup WebSocket server #TSK-009', '2025-01-22 10:00:00+00', 'feature/realtime');

        -- Insert pull requests
        INSERT INTO pull_requests (task_id, repository, pr_number, title, status, author, created_at, merged_at, url) VALUES
        ('TSK-002', 'worky', 1, 'Implement JWT Authentication', 'merged', 'John Doe', '2025-01-12 15:00:00+00', '2025-01-14 10:30:00+00', 'https://github.com/datalegos/worky/pull/1'),
        ('TSK-004', 'worky', 2, 'Setup CI/CD Pipeline', 'open', 'Alice Williams', '2025-01-16 09:00:00+00', NULL, 'https://github.com/datalegos/worky/pull/2'),
        ('TSK-006', 'worky', 3, 'Add Password Reset Feature', 'open', 'John Doe', '2025-01-17 14:00:00+00', NULL, 'https://github.com/datalegos/worky/pull/3');

        -- Insert documentation
        INSERT INTO documentation (entity_type, entity_id, title, content, format, author_id) VALUES
        ('Project', 'PRJ-001', 'Worky Architecture', '# Worky Architecture\n\nThis document describes the system architecture...\n\n## Components\n- API Server\n- Database\n- UI Application', 'markdown', 'USR-001'),
        ('Project', 'PRJ-001', 'API Documentation', '# API Documentation\n\n## Authentication\nAll API requests require JWT token...', 'markdown', 'USR-002'),
        ('Task', 'TSK-001', 'Database Schema Design', '# Database Schema\n\nThe schema follows a hierarchical structure:\n- Clients\n- Programs\n- Projects\n- Use Cases\n- User Stories\n- Tasks', 'markdown', 'USR-002'),
        ('Task', 'TSK-002', 'Authentication Implementation', '# Authentication\n\nUsing JWT with bcrypt for password hashing...', 'markdown', 'USR-002'),
        ('UseCase', 'USC-001', 'Security Requirements', '# Security Requirements\n\n- Password must be at least 8 characters\n- Must include special characters\n- Session timeout after 30 minutes', 'markdown', 'USR-001');

        -- Insert entity notes
        INSERT INTO entity_notes (entity_type, entity_id, note, author_id) VALUES
        ('Task', 'TSK-002', 'Remember to update the API documentation after merging', 'USR-003'),
        ('Task', 'TSK-004', 'Need to configure secrets in GitHub repository settings', 'USR-005'),
        ('Bug', 'BUG-002', 'This might be related to the database query optimization', 'USR-002'),
        ('UserStory', 'UST-009', 'Consider using Chart.js or D3.js for visualization', 'USR-004'),
        ('Project', 'PRJ-001', 'Target launch date is June 30, 2025', 'USR-001');

        -- Insert TODO items
        INSERT INTO todo_items (user_id, title, description, due_date, priority, status, category) VALUES
        ('USR-001', 'Review Q1 roadmap', 'Review and approve Q1 product roadmap', '2025-01-20', 'High', 'pending', 'work'),
        ('USR-002', 'Code review for PR #2', 'Review Alice''s CI/CD pipeline PR', '2025-01-18', 'High', 'pending', 'work'),
        ('USR-002', 'Update dependencies', 'Update npm packages to latest versions', '2025-01-25', 'Medium', 'pending', 'work'),
        ('USR-003', 'Sprint planning meeting', 'Prepare agenda for Sprint 3 planning', '2025-01-28', 'High', 'pending', 'work'),
        ('USR-004', 'Design system documentation', 'Document UI component library', '2025-02-01', 'Medium', 'in_progress', 'work'),
        ('USR-005', 'Server maintenance', 'Schedule server maintenance window', '2025-01-22', 'High', 'pending', 'work'),
        ('USR-006', 'Write test cases', 'Create test cases for new features', '2025-01-19', 'High', 'in_progress', 'work');

        -- Insert adhoc notes
        INSERT INTO adhoc_notes (user_id, title, content, category) VALUES
        ('USR-001', 'Meeting Notes - Jan 15', 'Discussed project priorities and resource allocation', 'meeting'),
        ('USR-002', 'Code Snippet - JWT Middleware', 'const verifyToken = (req, res, next) => { ... }', 'code'),
        ('USR-003', 'Sprint Retrospective', 'What went well: Good collaboration\nWhat to improve: Better estimation', 'meeting'),
        ('USR-004', 'Design Ideas', 'Consider using a card-based layout for the dashboard', 'idea'),
        ('USR-005', 'Server Configuration', 'Production server: 4 CPU, 16GB RAM, Ubuntu 22.04', 'technical');

        -- Insert dependencies
        INSERT INTO dependencies (entity_type, entity_id, depends_on_type, depends_on_id, dependency_type) VALUES
        ('Task', 'TSK-003', 'Task', 'TSK-001', 'blocks'),
        ('Task', 'TSK-006', 'Task', 'TSK-002', 'blocks'),
        ('Task', 'TSK-010', 'Task', 'TSK-009', 'blocks'),
        ('UserStory', 'UST-004', 'UserStory', 'UST-001', 'related'),
        ('UserStory', 'UST-010', 'UserStory', 'UST-003', 'blocks');

        RAISE NOTICE 'Development seed data loaded successfully!';
    ELSE
        RAISE NOTICE 'Users already exist - skipping seed data';
    END IF;
END $$;

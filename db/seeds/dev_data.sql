-- Development seed data for Worky
-- This file populates the database with sample data for development

-- Insert clients
INSERT INTO clients (id, name, description, is_active) VALUES
('11111111-1111-1111-1111-111111111111', 'DataLegos', 'Internal projects and tools', true),
('22222222-2222-2222-2222-222222222222', 'Acme Corp', 'Enterprise client - Manufacturing', true),
('33333333-3333-3333-3333-333333333333', 'TechStart Inc', 'Startup client - SaaS platform', true);

-- Insert users (password is 'password' hashed with bcrypt)
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK
INSERT INTO users (id, email, hashed_password, full_name, role, client_id, language, theme) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'admin@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'Admin User', 'Admin', '11111111-1111-1111-1111-111111111111', 'en', 'snow'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'john@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'John Doe', 'Developer', '11111111-1111-1111-1111-111111111111', 'en', 'dark'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'jane@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'Jane Smith', 'Project Manager', '11111111-1111-1111-1111-111111111111', 'en', 'water'),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'bob@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'Bob Johnson', 'Developer', '11111111-1111-1111-1111-111111111111', 'en', 'greenery'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'alice@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'Alice Williams', 'DevOps', '11111111-1111-1111-1111-111111111111', 'en', 'dracula'),
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'charlie@datalegos.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK', 'Charlie Brown', 'Tester', '11111111-1111-1111-1111-111111111111', 'te', 'blackwhite');

-- Insert programs
INSERT INTO programs (id, client_id, name, description, start_date, end_date, status) VALUES
('10000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Internal Tools', 'Development of internal productivity tools', '2025-01-01', '2025-12-31', 'In Progress'),
('10000000-0000-0000-0000-000000000002', '22222222-2222-2222-2222-222222222222', 'Digital Transformation', 'Enterprise-wide digital transformation initiative', '2024-06-01', '2026-06-30', 'In Progress');

-- Insert projects
INSERT INTO projects (id, program_id, name, description, start_date, end_date, status, repository_url) VALUES
('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'Worky Platform', 'Internal project management system', '2025-01-01', '2025-06-30', 'In Progress', 'https://github.com/datalegos/worky'),
('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'Customer Portal', 'Self-service customer portal', '2025-02-01', '2025-08-31', 'Planning', 'https://github.com/datalegos/customer-portal'),
('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'Mobile App', 'iOS and Android mobile application', '2024-11-01', '2025-05-31', 'In Progress', 'https://github.com/acme/mobile-app');

-- Insert usecases
INSERT INTO usecases (id, project_id, name, description, priority, status) VALUES
('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'User Authentication', 'Secure user login and session management', 'High', 'In Progress'),
('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 'Project Management', 'Create and manage projects with hierarchy', 'High', 'In Progress'),
('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001', 'Task Tracking', 'Track tasks with assignments and progress', 'High', 'In Progress');

-- Insert user stories
INSERT INTO user_stories (id, usecase_id, title, description, acceptance_criteria, story_points, priority, status) VALUES
('40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'User Login', 'As a user, I want to login with email and password', 'User can enter credentials and access dashboard', 5, 'High', 'Done'),
('40000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000002', 'Create Project', 'As a PM, I want to create new projects', 'PM can create project with name, dates, and description', 3, 'High', 'In Progress'),
('40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 'Assign Tasks', 'As a PM, I want to assign tasks to team members', 'PM can select user and assign task', 2, 'Medium', 'To Do');

-- Insert tasks
INSERT INTO tasks (id, user_story_id, title, description, status, priority, assigned_to, estimated_hours, actual_hours, start_date, due_date) VALUES
('50000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'Design database schema', 'Create PostgreSQL schema for all entities', 'Done', 'High', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 16, 14, '2025-01-01', '2025-01-05'),
('50000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000001', 'Implement authentication', 'JWT-based auth with role-based access control', 'In Progress', 'High', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 24, 18, '2025-01-06', '2025-01-15'),
('50000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000002', 'Create UI mockups', 'Design mockups for all main pages', 'To Do', 'Medium', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 16, 0, '2025-01-10', '2025-01-20'),
('50000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000002', 'Setup CI/CD pipeline', 'Configure GitHub Actions for automated deployment', 'In Progress', 'Medium', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 12, 8, '2025-01-08', '2025-01-18');

-- Insert bugs
INSERT INTO bugs (id, task_id, title, description, severity, priority, status, assigned_to, reported_by, environment) VALUES
('60000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', 'Login page not responsive on mobile', 'The login form breaks on screens smaller than 768px', 'High', 'High', 'Open', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'Mobile Safari iOS 17'),
('60000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000002', 'Task filter not working', 'Filtering tasks by status returns incorrect results', 'Medium', 'Medium', 'In Progress', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'Chrome 120');

-- Insert sprints
INSERT INTO sprints (id, project_id, name, goal, start_date, end_date, status) VALUES
('70000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'Sprint 1', 'Setup infrastructure and authentication', '2025-01-01', '2025-01-14', 'Active');

-- Link tasks to sprint
INSERT INTO sprint_tasks (sprint_id, task_id) VALUES
('70000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002'),
('70000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000004');

-- Insert some commits
INSERT INTO commits (task_id, repository, commit_hash, author, author_email, message, committed_at, branch) VALUES
('50000000-0000-0000-0000-000000000001', 'worky', 'abc123def456', 'John Doe', 'john@datalegos.com', 'feat: Add database schema #TASK-1', '2025-01-05 10:30:00+00', 'main'),
('50000000-0000-0000-0000-000000000002', 'worky', 'def456ghi789', 'John Doe', 'john@datalegos.com', 'feat: Implement JWT authentication #TASK-2', '2025-01-12 14:20:00+00', 'feature/auth');

-- Insert documentation
INSERT INTO documentation (entity_type, entity_id, title, content, format, author_id) VALUES
('Project', '20000000-0000-0000-0000-000000000001', 'Worky Architecture', '# Worky Architecture\n\nThis document describes the system architecture...', 'markdown', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
('Task', '50000000-0000-0000-0000-000000000001', 'Database Schema Design', '# Database Schema\n\nThe schema follows a hierarchical structure...', 'markdown', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

-- Simple seed data for testing
INSERT INTO clients (id, name, description) VALUES
('CLI-001', 'DataLegos', 'Internal projects and tools'),
('CLI-002', 'Acme Corp', 'Enterprise client - Manufacturing'),
('CLI-003', 'TechStart Inc', 'Startup client - SaaS platform');

INSERT INTO users (id, email, hashed_password, full_name, role, client_id, language, theme) VALUES
('USR-001', 'admin@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Admin User', 'Admin', 'CLI-001', 'en', 'snow'),
('USR-002', 'john@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'John Doe', 'Developer', 'CLI-001', 'en', 'dark'),
('USR-003', 'jane@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Jane Smith', 'Project Manager', 'CLI-001', 'en', 'water'),
('USR-004', 'bob@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Bob Johnson', 'Developer', 'CLI-001', 'en', 'greenery'),
('USR-005', 'alice@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Alice Williams', 'DevOps', 'CLI-001', 'en', 'dracula'),
('USR-006', 'charlie@datalegos.com', '$2b$12$9OAMueEnVYFWy7shFaKgqujLD8MJWcByjxw2uOzb30Vc3PgG.aHEy', 'Charlie Brown', 'Tester', 'CLI-001', 'en', 'blackwhite');

INSERT INTO programs (id, client_id, name, description, start_date, end_date, status) VALUES
('PRG-001', 'CLI-001', 'Internal Tools', 'Development of internal productivity tools', '2025-01-01', '2025-12-31', 'In Progress'),
('PRG-002', 'CLI-002', 'Digital Transformation', 'Enterprise-wide digital transformation initiative', '2024-06-01', '2026-06-30', 'In Progress');

INSERT INTO projects (id, program_id, name, description, start_date, end_date, status, repository_url) VALUES
('PRJ-001', 'PRG-001', 'Worky Platform', 'Internal project management system', '2025-01-01', '2025-06-30', 'In Progress', 'https://github.com/datalegos/worky'),
('PRJ-002', 'PRG-001', 'Customer Portal', 'Self-service customer portal', '2025-02-01', '2025-08-31', 'Planning', 'https://github.com/datalegos/customer-portal'),
('PRJ-003', 'PRG-002', 'Mobile App', 'iOS and Android mobile application', '2024-11-01', '2025-05-31', 'In Progress', 'https://github.com/acme/mobile-app');
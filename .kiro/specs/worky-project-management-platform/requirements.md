# Requirements Document

## Introduction

Worky is an internal Project Management, Monitoring, and Alerting Platform for DataLegos consulting company. The system unifies project planning, tracking, documentation, bug management, Git traceability, utilization reporting, and alerting under one secure, self-hosted platform. The system supports a hierarchical data model (Client → Program → Project → Usecase → User Story → Task → Subtask) with role-based access control, Git integration, real-time monitoring, and comprehensive reporting capabilities.

## Glossary

- **Worky System**: The complete internal project management platform including UI, API, database, and monitoring components deployed as separate containerized services
- **UI Service**: React-based frontend application served as a separate Docker container
- **API Service**: FastAPI backend application served as a separate Docker container
- **DB Service**: PostgreSQL database served as a separate Docker container
- **Ansible Inventory**: Configuration files (.ini format) containing all deployment parameters and environment-specific settings
- **Volume Mount**: Persistent storage mechanism for sharing data between host system and Docker containers
- **Sprint Board**: Kanban-style board organized by sprint cycles for Agile daily standup meetings
- **Dependency**: A relationship between two entities where one must be completed before another can start or progress
- **Agile**: An iterative development methodology using sprints, standups, and incremental delivery
- **User**: An authenticated individual with assigned role and client association
- **Client**: Top-level organizational entity representing a customer or business unit
- **Program**: A collection of related projects under a client
- **Project**: A specific initiative with defined scope, team, and deliverables
- **Usecase**: A functional requirement or scenario within a project
- **User Story**: A user-centric description of desired functionality within a usecase
- **Task**: A discrete unit of work assigned to team members within a user story
- **Subtask**: A granular work item that is part of a task
- **Git Traceability**: The ability to link commits, pull requests, and branches to tasks
- **Utilization Report**: Analysis of resource allocation versus actual usage
- **Engagement Report**: Measurement of developer activity levels
- **Occupancy Forecast**: Prediction of time allocation for upcoming periods
- **RBAC**: Role-Based Access Control system
- **Audit Trail**: Immutable log of all system changes and user actions
- **Alert**: Automated notification triggered by system events or thresholds

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a system administrator, I want to manage user authentication and role-based access control, so that only authorized users can access appropriate system resources.

#### Acceptance Criteria

1. THE Worky System SHALL implement OAuth2 or JWT-based authentication for all API endpoints
2. WHEN a user attempts to access a protected resource, THE Worky System SHALL validate the authentication token and verify role permissions
3. THE Worky System SHALL support at least six distinct roles: Admin, Project Manager, Product Owner, Developer, DevOps, Tester, and Business Analyst
4. THE Worky System SHALL enforce that each user belongs to exactly one client
5. THE Worky System SHALL apply access control at the project level, restricting data visibility based on user role and client association

### Requirement 2: Hierarchical Data Management

**User Story:** As a project manager, I want to organize work in a hierarchical structure from clients down to subtasks, so that I can manage complex projects with clear relationships and dependencies.

#### Acceptance Criteria

1. THE Worky System SHALL support a seven-level hierarchy: Client, Program, Project, Usecase, User Story, Task, and Subtask
2. WHEN a parent entity is deleted, THE Worky System SHALL cascade the deletion to all child entities while preserving records in audit logs
3. THE Worky System SHALL enforce that each user is associated with exactly one client through a foreign key constraint
4. THE Worky System SHALL allow administrators to create, read, update, and delete entities at any hierarchy level
5. THE Worky System SHALL maintain referential integrity across all hierarchy levels using database foreign key constraints

### Requirement 3: Project Planning and Visualization

**User Story:** As a project manager, I want to visualize project timelines and dependencies using Gantt charts and Kanban boards, so that I can track progress and identify bottlenecks.

#### Acceptance Criteria

1. THE Worky System SHALL provide a Gantt chart view displaying tasks with start dates, end dates, and dependency relationships
2. THE Worky System SHALL provide a Kanban board view with customizable columns representing task states
3. THE Worky System SHALL provide a Sprint Board view organized by sprint cycles for Agile daily standup meetings
4. THE Worky System SHALL allow users to define dependencies at each hierarchy level: Program, Project, Usecase, User Story, Task, and Subtask
5. WHEN a dependency is defined at any hierarchy level, THE Worky System SHALL prevent scheduling conflicts that violate dependency constraints
6. THE Worky System SHALL allow users to assign team members, roles, and deadlines to tasks
7. THE Worky System SHALL calculate and display progress metrics for each task and project based on completed work

### Requirement 4: Git Integration and Traceability

**User Story:** As a developer, I want to link my commits and pull requests to specific tasks, so that code changes are traceable to project requirements.

#### Acceptance Criteria

1. THE Worky System SHALL integrate with GitHub, GitLab, and Bitbucket APIs to retrieve commit and pull request data
2. WHEN a commit message contains a task identifier tag, THE Worky System SHALL automatically link the commit to the corresponding task
3. WHEN a pull request is merged, THE Worky System SHALL update the linked task status according to configured rules
4. THE Worky System SHALL generate changelog and release notes based on linked commits and tasks
5. THE Worky System SHALL display commit history and pull request information within the task detail view

### Requirement 5: Documentation Management

**User Story:** As a business analyst, I want to create and maintain versioned documentation for each project entity, so that knowledge is preserved and accessible to the team.

#### Acceptance Criteria

1. THE Worky System SHALL provide a Markdown and rich-text editor for creating documentation
2. THE Worky System SHALL support versioned documentation linked to each hierarchy level (Client through Subtask)
3. THE Worky System SHALL allow users to export documentation to PDF format
4. WHERE Git synchronization is enabled, THE Worky System SHALL sync documentation with markdown files in connected repositories
5. THE Worky System SHALL maintain a version history for each documentation artifact with timestamps and author information

### Requirement 6: Bug Tracking and Lifecycle Management

**User Story:** As a tester, I want to create, track, and manage bugs with severity and priority levels, so that issues are resolved systematically.

#### Acceptance Criteria

1. THE Worky System SHALL allow users to create bug reports with severity, priority, status, and description fields
2. THE Worky System SHALL support linking bugs to user stories, commits, or builds
3. WHEN a commit message contains a bug closure tag, THE Worky System SHALL automatically update the bug status to closed
4. THE Worky System SHALL allow assignment of bugs to specific team members
5. THE Worky System SHALL track bug lifecycle states including New, Assigned, In Progress, Fixed, Verified, and Closed

### Requirement 7: Utilization and Engagement Reporting

**User Story:** As an administrator, I want to generate utilization and engagement reports, so that I can analyze resource allocation and team productivity.

#### Acceptance Criteria

1. THE Worky System SHALL generate utilization reports showing resource allocation versus actual usage
2. THE Worky System SHALL generate engagement reports measuring developer activity levels based on commits, tasks, and time logged
3. THE Worky System SHALL generate occupancy forecasts showing percentage of time booked for upcoming periods
4. THE Worky System SHALL allow export of reports to PDF and CSV formats
5. THE Worky System SHALL store report snapshots in the database with generation timestamp and parameters

### Requirement 8: Monitoring and Alerting

**User Story:** As a DevOps engineer, I want to monitor system health and receive alerts for critical events, so that I can respond quickly to issues.

#### Acceptance Criteria

1. THE Worky System SHALL integrate with Prometheus to collect API metrics and system health data
2. THE Worky System SHALL provide Grafana dashboards displaying task completion trends, bug density, developer activity, and CI/CD pipeline success rates
3. WHEN a critical event occurs (failed transaction, exception, or unresponsive module), THE Worky System SHALL send an alert to Discord via webhook
4. THE Worky System SHALL integrate with Loki for centralized log aggregation
5. THE Worky System SHALL implement OpenTelemetry for distributed tracing across system components

### Requirement 9: Security and Audit Logging

**User Story:** As an administrator, I want comprehensive security controls and audit trails, so that the system is secure and all actions are traceable.

#### Acceptance Criteria

1. THE Worky System SHALL encrypt all communication using TLS
2. THE Worky System SHALL encrypt sensitive database columns containing personally identifiable information
3. THE Worky System SHALL record all CRUD operations and system changes in an immutable audit log with correlation IDs
4. THE Worky System SHALL store structured JSON logs with timestamp, service name, environment, log level, request ID, user ID, client ID, project ID, action, message, duration, and context
5. THE Worky System SHALL manage secrets using Ansible Vault or an external secret manager

### Requirement 10: Containerization and Deployment

**User Story:** As a DevOps engineer, I want the system deployed as containerized services with automated provisioning, so that deployment is consistent and repeatable.

#### Acceptance Criteria

1. THE Worky System SHALL organize code into three separate directories: ui/, api/, and db/ for frontend, backend, and database artifacts respectively
2. THE Worky System SHALL provide Docker containers for UI, API, database, Prometheus, and Grafana services as isolated containers
3. THE Worky System SHALL store all configuration parameters in Ansible inventory .ini files without hardcoding values in application code
4. THE Worky System SHALL mount logs, outputs, and database files as volumes outside Docker containers on the host filesystem
5. THE Worky System SHALL include a docker-compose.yml file for local development setup
6. THE Worky System SHALL provide Ansible playbooks for provisioning Docker runtime, database, Prometheus, and Grafana
7. THE Worky System SHALL implement CI/CD pipelines that build, lint, test, security scan, and deploy services
8. THE Worky System SHALL scan container images using Trivy before deployment

### Requirement 11: Performance and Scalability

**User Story:** As a system administrator, I want the system to handle concurrent users and projects efficiently, so that performance remains acceptable under load.

#### Acceptance Criteria

1. THE Worky System SHALL support at least 100 concurrent projects
2. THE Worky System SHALL support at least 300 active users
3. WHEN API response time exceeds 2 seconds for 95% of requests, THE Worky System SHALL trigger a performance alert
4. THE Worky System SHALL implement database connection pooling to optimize resource usage
5. THE Worky System SHALL use database indexes on frequently queried columns to maintain query performance

### Requirement 12: Data Backup and Recovery

**User Story:** As an administrator, I want automated database backups with retention policies, so that data can be recovered in case of failure.

#### Acceptance Criteria

1. THE Worky System SHALL perform automated nightly database backups with encryption
2. THE Worky System SHALL retain hot backups for 30 days
3. THE Worky System SHALL retain cold storage backups for 180 days
4. THE Worky System SHALL verify backup integrity through automated restore tests
5. WHEN a backup operation fails, THE Worky System SHALL send an alert to administrators via Discord

### Requirement 13: Multi-tenancy and Client Isolation

**User Story:** As an administrator, I want strict client data isolation, so that users can only access data belonging to their assigned client.

#### Acceptance Criteria

1. THE Worky System SHALL enforce that each user has exactly one client_id foreign key
2. WHEN a user queries data, THE Worky System SHALL filter results to include only records associated with the user's client
3. WHERE a user has Admin role, THE Worky System SHALL allow access to all client data for system administration purposes
4. THE Worky System SHALL prevent cross-client data leakage through API endpoints
5. THE Worky System SHALL validate client association on all create, update, and delete operations

### Requirement 14: Internationalization and Theming

**User Story:** As a user, I want to use the system in my preferred language and visual theme, so that the interface is comfortable and accessible.

#### Acceptance Criteria

1. THE Worky System SHALL support internationalization (i18n) with English and Telugu language options
2. THE Worky System SHALL provide six visual themes: Snow (light), Greenery (green-based), Water (blue-based), Dracula (red and black), Dark, and Black & White
3. WHEN a user selects a theme, THE Worky System SHALL update all widgets, fonts, and cursor styles to match the theme aesthetic
4. THE Worky System SHALL persist user language and theme preferences in the database
5. WHEN a user changes language or theme, THE Worky System SHALL apply the change immediately without requiring page reload

### Requirement 15: Role-Based Feature Access

**User Story:** As an administrator, I want to configure which features each role can access, so that users see only relevant functionality.

#### Acceptance Criteria

1. WHERE a user has Admin role, THE Worky System SHALL grant full control including user management, role assignment, and system configuration
2. WHERE a user has Project Manager role, THE Worky System SHALL grant access to planning, dependencies, Gantt charts, and reporting features
3. WHERE a user has Developer role, THE Worky System SHALL grant access to assigned tasks and Git integration features
4. WHERE a user has Tester role, THE Worky System SHALL grant access to bug tracking and verification features
5. THE Worky System SHALL hide UI elements and disable API endpoints for features not accessible to the user's role

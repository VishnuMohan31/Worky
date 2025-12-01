# Worky - Knowledge Transfer Document

**Version:** 1.0  
**Date:** December 1, 2025  
**Document Owner:** Development Team

---

## 1. Business Case

### 1.1 Overview
Worky is a comprehensive project management platform designed to manage complex software development projects through a hierarchical structure. It provides end-to-end visibility from client engagement to individual task execution, with integrated QA testing, bug tracking, and team collaboration features.

### 1.2 Key Business Objectives
- **Unified Project Tracking**: Single platform for managing clients, programs, projects, use cases, user stories, tasks, and subtasks
- **Quality Assurance**: Integrated test management and bug lifecycle tracking following industry standards
- **Team Productivity**: Personal TODO management, chat assistant, and real-time collaboration
- **Data-Driven Insights**: Comprehensive reporting and analytics for project health and team performance
- **Flexible Data Import**: Excel-based data loading for easy migration and bulk updates

### 1.3 Target Users
- **Admin**: System configuration and user management
- **Project Manager**: Project planning, resource allocation, and progress tracking
- **Product Owner**: Requirements definition and backlog prioritization
- **Developer**: Task execution and code integration
- **DevOps**: Infrastructure and deployment management
- **Tester/QA**: Test execution and bug management
- **Business Analyst**: Requirements gathering and documentation

---

## 2. System Architecture

### 2.1 Technology Stack

**Frontend (UI)**
- React 18 with TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Zustand (state management)
- i18next (internationalization)
- Axios (API communication)

**Backend (API)**
- FastAPI (Python async web framework)
- SQLAlchemy 2.0 (async ORM)
- Pydantic (data validation)
- JWT (authentication)
- Alembic (database migrations)
- Prometheus (metrics)

**Database**
- PostgreSQL 15
- UUID-based primary keys
- Soft delete support
- Audit trail tracking

**Infrastructure**
- Docker & Docker Compose
- Nginx (reverse proxy - production)
- Structured JSON logging

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (React)                      │
│  - Pages, Components, Services, Contexts                 │
│  - Themes: Snow, Greenery, Water, Dracula, Dark, B&W   │
│  - Languages: English, Telugu                            │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                  API Layer (FastAPI)                     │
│  - Endpoints, Services, CRUD, Middleware                 │
│  - JWT Auth, RBAC, Rate Limiting                        │
│  - Chat Assistant, Report Generation                     │
└─────────────────────────────────────────────────────────┘
                          ↓ SQL
┌─────────────────────────────────────────────────────────┐
│              Database Layer (PostgreSQL)                 │
│  - Core Hierarchy Tables                                 │
│  - QA & Testing Tables                                   │
│  - TODO & Chat Tables                                    │
│  - Audit & History Tables                                │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Project Hierarchy

### 3.1 Hierarchy Structure

Worky follows a strict 7-level hierarchy:

```
Client (Organization)
  └── Program (Portfolio of projects)
        └── Project (Individual project)
              └── Use Case (Feature group)
                    └── User Story (User requirement)
                          └── Task (Development work item)
                                └── Subtask (Granular work unit)
```

### 3.2 Hierarchy Details

**Client**
- Top-level organizational entity
- Users belong to exactly one client
- Data isolation boundary (users only see their client's data)
- Fields: name, description, is_active

**Program**
- Collection of related projects under a client
- Strategic initiative or product line
- Fields: name, description, start_date, end_date, status

**Project**
- Individual software project or application
- Contains repository URL for code integration
- Fields: name, description, start_date, end_date, status, repository_url

**Use Case**
- Functional area or feature group within a project
- Groups related user stories
- Fields: name, description, priority, status

**User Story**
- User-centric requirement following Agile format
- Contains acceptance criteria and story points
- Can be assigned to sprints
- Fields: title, description, acceptance_criteria, story_points, priority, status, phase_id

**Task**
- Specific development work item
- Assigned to individual developers
- Time-tracked with estimates and actuals
- Fields: title, description, status, priority, assigned_to, estimated_hours, actual_hours, start_date, due_date

**Subtask**
- Granular breakdown of tasks
- Enables detailed progress tracking
- Fields: title, description, status, priority, assigned_to, estimated_hours, actual_hours, due_date

### 3.3 Supporting Entities

**Phases**
- Work phases: Development, Testing, Deployment, Maintenance, etc.
- Can be assigned to user stories for workflow tracking
- Ordered sequence for project lifecycle

**Sprints**
- Agile sprint management
- Links to projects with configurable duration
- Contains sprint tasks and user stories
- Fields: name, start_date, end_date, status, project_id

**Dependencies**
- Cross-entity dependencies
- Tracks blocking relationships
- Fields: source_entity_type, source_entity_id, target_entity_type, target_entity_id, dependency_type

---

## 4. Functional Components

### 4.1 Core Features

**Dashboard**
- Overview statistics (projects, tasks, bugs)
- Recent activity feed
- Quick access to assigned tasks
- Project health indicators

**Client Management**
- CRUD operations for clients
- Client activation/deactivation
- User assignment to clients

**Program & Project Management**
- Hierarchical navigation
- Project timeline visualization
- Status tracking and updates
- Repository integration

**Task Management**
- Task creation and assignment
- Status workflow (To Do → In Progress → Done)
- Time tracking (estimated vs actual hours)
- Priority and due date management
- Subtask breakdown

**User Story Management**
- Backlog management
- Story point estimation
- Acceptance criteria definition
- Sprint assignment

### 4.2 QA & Testing Features

**Test Run Management**
- Create test runs at any hierarchy level (Project → Subtask)
- Test run types: Misc, One-Timer
- Status: In Progress, Completed, Aborted
- Metrics: total cases, passed, failed, blocked

**Test Case Management**
- Test cases belong to test runs
- Structured test steps with expected results
- Execution tracking (actual result, inference)
- Priority levels: P0, P1, P2, P3
- Status: Not Executed, Passed, Failed, Blocked, Skipped

**Bug Lifecycle Management**
- Create bugs from failed test cases or directly
- Bug statuses: New → Open → In Progress → Fixed → In Review → Ready for QA → Verified → Closed
- Bug categories: UI, Backend, Database, Integration, Performance, Security, Environment
- Severity: Critical, High, Medium, Low
- Priority: P1, P2, P3, P4
- Assignment: reporter, assignee, QA owner
- Comments and attachments
- Status history and audit trail

**Hierarchical Bug Viewing**
- View bugs at any hierarchy level
- Automatically includes bugs from all descendant levels
- Example: Selecting a Project shows bugs from Project + all Use Cases + User Stories + Tasks + Subtasks

### 4.3 Productivity Features

**TODO Management**
- Personal TODO list per user
- Time-based panes: Yesterday, Today, Tomorrow, Day After Tomorrow
- Public/Private visibility control
- Optional linking to tasks/subtasks (read-only)
- ADHOC notes pane for quick sticky notes
- Drag-and-drop between panes

**Chat Assistant**
- Natural language queries about projects and tasks
- Context-aware responses with RAG (Retrieval-Augmented Generation)
- Safe actions: view items, set reminders, update status, create comments
- RBAC enforcement (users only see their client's data)
- Rate limiting: 60 requests/minute per user
- Session-based conversation context (10 messages)
- Rich responses: deep links, cards, tables, charts
- Audit logging for compliance

**Entity Notes**
- Add notes to any entity (Project, Task, Bug, etc.)
- Timestamped and user-attributed
- Supports rich text formatting

**Comments System**
- Threaded comments on bugs and tasks
- @mentions for notifications
- Edit within 15 minutes
- File attachments support

### 4.4 Reporting & Analytics

**Project Reports**
- Project tree structure visualization
- Task distribution by status
- Resource utilization
- Timeline and milestone tracking

**QA Metrics Dashboard**
- Bug trend analysis (creation vs resolution)
- Bug distribution (category, severity, priority)
- Mean time to resolution (MTTR)
- Bug aging reports
- Test run completion metrics
- Pass/fail trends

**Sprint Reports**
- Sprint velocity
- Burndown charts
- Sprint completion rates

**Export Capabilities**
- PDF, Excel, CSV formats
- Customizable date ranges
- Filtered views

### 4.5 Administration

**User Management**
- CRUD operations for users
- Role assignment (7 roles)
- Client assignment
- User activation/deactivation

**Organization Management**
- Multi-tenant support
- Organization-level settings
- User preferences (theme, language, view mode)

**Sprint Configuration**
- Project-level sprint settings
- Sprint duration configuration
- Sprint status management

---

## 5. Technical Components

### 5.1 API Structure

```
api/
├── app/
│   ├── api/v1/endpoints/      # REST endpoints
│   │   ├── auth.py            # Authentication
│   │   ├── clients.py         # Client management
│   │   ├── projects.py        # Project CRUD
│   │   ├── tasks.py           # Task management
│   │   ├── bugs.py            # Bug tracking
│   │   ├── test_cases.py      # Test case management
│   │   ├── test_runs.py       # Test run management
│   │   ├── todos.py           # TODO management
│   │   ├── chat.py            # Chat assistant
│   │   ├── reports.py         # Report generation
│   │   └── ...
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── security.py        # JWT, password hashing
│   │   └── logging.py         # Structured logging
│   ├── crud/                  # Database operations
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── chat_service.py    # Chat assistant logic
│   │   ├── report_service.py  # Report generation
│   │   ├── sprint_service.py  # Sprint management
│   │   └── ...
│   └── middleware/            # Custom middleware
├── alembic/                   # Database migrations
├── tests/                     # Unit & integration tests
└── requirements.txt           # Python dependencies
```

### 5.2 UI Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── auth/              # Login, protected routes
│   │   ├── layout/            # Sidebar, Header, Layout
│   │   ├── hierarchy/         # Entity lists and details
│   │   ├── tasks/             # Task components
│   │   ├── qa/                # QA & testing components
│   │   ├── todo/              # TODO feature components
│   │   ├── chat/              # Chat assistant widget
│   │   ├── reports/           # Report viewers
│   │   ├── forms/             # Reusable forms
│   │   └── common/            # Shared components
│   ├── pages/                 # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── ProjectsPage.tsx
│   │   ├── TasksPage.tsx
│   │   ├── TestCasesPage.tsx
│   │   ├── BugLifecyclePage.tsx
│   │   ├── TodoPage.tsx
│   │   └── ...
│   ├── services/
│   │   ├── api.ts             # API client
│   │   ├── chatApi.ts         # Chat API
│   │   └── todoApi.ts         # TODO API
│   ├── contexts/              # React contexts
│   │   ├── AuthContext.tsx
│   │   └── ChatContext.tsx
│   ├── types/                 # TypeScript types
│   └── i18n.ts                # Internationalization
├── public/themes/             # CSS theme files
└── package.json               # Node dependencies
```

### 5.3 Database Schema

**Core Tables**
- `clients` - Organizations
- `users` - User accounts
- `programs` - Program portfolio
- `projects` - Projects
- `usecases` - Use cases
- `user_stories` - User stories
- `tasks` - Tasks
- `subtasks` - Subtasks
- `phases` - Work phases
- `sprints` - Sprint management

**QA Tables**
- `test_runs` - Test run containers
- `test_cases` - Individual test cases
- `test_executions` - Test execution records
- `bugs` - Bug tracking
- `bug_comments` - Bug comments
- `bug_attachments` - Bug file attachments
- `bug_status_history` - Bug audit trail

**Productivity Tables**
- `todo_items` - User TODO items
- `adhoc_notes` - Quick notes
- `chat_messages` - Chat conversations
- `chat_audit_logs` - Chat audit trail
- `reminders` - User reminders

**Supporting Tables**
- `entity_notes` - Notes on any entity
- `dependencies` - Cross-entity dependencies
- `organizations` - Organization settings
- `company_settings` - Company-wide config
- `audit_logs` - System audit trail

### 5.4 Authentication & Authorization

**JWT-Based Authentication**
- Login endpoint: `POST /api/v1/auth/login`
- Returns access token with 30-minute expiry
- Token includes user ID, email, role, client ID

**Role-Based Access Control (RBAC)**
- 7 roles: Admin, Project Manager, Product Owner, Developer, DevOps, Tester, Business Analyst
- Client-level data isolation (users only see their client's data)
- Endpoint-level permission checks

**Security Features**
- Password hashing with bcrypt
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)
- Rate limiting (60 req/min per user for chat)
- CORS configuration

### 5.5 Data Import System

**Excel Data Loader**
- Located in `Data_upload/scripts/excel_loader/`
- Parses Excel files with project hierarchy
- Maps Excel data to database schema
- Builds hierarchical relationships
- Validates data integrity
- Provides detailed logging
- Rollback on errors

**Components**
- `excel_parser.py` - Reads Excel files
- `data_mapper.py` - Maps Excel to database schema
- `hierarchy_builder.py` - Builds entity relationships
- `database_writer.py` - Writes to PostgreSQL
- `import_orchestrator.py` - Coordinates import process
- `excel_loader_app.py` - Flask API for imports

**Usage**
```bash
cd Data_upload/scripts
./start_loader.sh
# Upload Excel file via API or UI
```

---

## 6. How to Run the Application

### 6.1 Prerequisites

**Required Software**
- Docker & Docker Compose
- Node.js 18+ (for local UI development)
- Python 3.11+ (for local API development)
- PostgreSQL 15 (if running without Docker)

**System Requirements**
- 4GB RAM minimum
- 10GB disk space
- macOS, Linux, or Windows with WSL2

### 6.2 Quick Start (Docker - Recommended)

**1. Clone Repository**
```bash
cd /Users/ravikiranponduri/Desktop/WIP/worky
```

**2. Start All Services**
```bash
cd App_Development_scripts
./worky.sh all start
```

This starts:
- Database (PostgreSQL) on port 5437
- API (FastAPI) on port 8007
- UI (React) on port 3007

**3. Access Application**
- UI: http://localhost:3007
- API Docs: http://localhost:8007/docs
- API ReDoc: http://localhost:8007/redoc

**4. Default Login**
- Email: `admin@datalegos.com`
- Password: `password`

### 6.3 Service Management

**Using Master Script**
```bash
cd App_Development_scripts

# Start services
./worky.sh all start      # All services
./worky.sh ui start       # UI only
./worky.sh api start      # API only
./worky.sh db start       # Database only

# Stop services
./worky.sh all stop       # All services
./worky.sh ui stop        # UI only

# Restart services
./worky.sh all restart    # All services
./worky.sh ui restart     # UI only
```

**Using Individual Scripts**
```bash
# UI
./start_ui.sh
./stop_ui.sh
./restart_ui.sh

# API
./start_api.sh
./stop_api.sh
./restart_api.sh

# Database
./start_db.sh
./stop_db.sh
./restart_db.sh

# All
./start_all.sh
./stop_all.sh
./restart_all.sh
```

### 6.4 Local Development Setup

**Database Setup**
```bash
# Start database
cd App_Development_scripts
./start_db.sh

# Verify migrations
cd ../db
./verify_migrations.sh

# Load seed data (optional)
cd ../dummy_data_setup
python create_sample_data.py
```

**API Setup**
```bash
cd api

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000
```

**UI Setup**
```bash
cd ui

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with API URL

# Start development server
npm run dev
```

### 6.5 Database Management

**Access Database Shell**
```bash
cd App_Development_scripts
./db_shell.sh
```

**Run Migrations**
```bash
cd db
./apply_migrations.sh
```

**Reset Database**
```bash
# Stop and remove database container
docker-compose down -v

# Start fresh (migrations run automatically)
docker-compose up -d db
```

**Load Dummy Data**
```bash
cd dummy_data_setup

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env

# Load sample data
python create_sample_data.py

# Load QA test data
python create_qa_data.py
```

### 6.6 Ports & URLs

**Development Ports**
- UI: 3007 → http://localhost:3007
- API: 8007 → http://localhost:8007
- Database: 5437 (PostgreSQL)

**API Endpoints**
- Swagger UI: http://localhost:8007/docs
- ReDoc: http://localhost:8007/redoc
- Health Check: http://localhost:8007/health
- Metrics: http://localhost:8007/metrics

### 6.7 Troubleshooting

**Services Won't Start**
```bash
# Check if ports are in use
lsof -i :3007  # UI
lsof -i :8007  # API
lsof -i :5437  # Database

# Check Docker status
docker ps
docker-compose logs db
docker-compose logs api

# Restart Docker
docker-compose down
docker-compose up -d
```

**Database Connection Issues**
```bash
# Check database is running
docker ps | grep worky-postgres

# Check database logs
docker logs worky-postgres

# Test connection
psql -h localhost -p 5437 -U postgres -d worky
```

**API Not Responding**
```bash
# Check API logs
cd App_Development_scripts
tail -f ../logs/api.log

# Check API container
docker logs worky-api

# Restart API
./worky.sh api restart
```

**UI Build Errors**
```bash
cd ui

# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run build
```

### 6.8 Testing

**API Tests**
```bash
cd api
pytest
pytest tests/integration/
```

**UI Tests**
```bash
cd ui
npm test
```

**Integration Tests**
```bash
cd api
./test_api_integration.sh
```

---

## 7. Key Configuration Files

**Environment Files**
- `api/.env` - API configuration (database, secrets, external services)
- `ui/.env` - UI configuration (API URL, feature flags)
- `dummy_data_setup/.env` - Data loading configuration
- `Data_upload/scripts/excel_loader/.env` - Excel loader configuration

**Docker Configuration**
- `docker-compose.yml` - Service orchestration
- `api/Dockerfile` - API container definition

**Database Configuration**
- `db/migrations/*.sql` - Database schema migrations
- `db/seeds/dev_data.sql` - Development seed data

---

## 8. Additional Resources

**Documentation Locations**
- API Documentation: `api/README.md`
- UI Documentation: `ui/README.md`
- Database Documentation: `db/README.md`
- QA Feature Spec: `.kiro/specs/qa-testing-bug-management/`
- Chat Assistant Spec: `.kiro/specs/chat-assistant/`
- TODO Feature Spec: `.kiro/specs/todo-feature/`
- Excel Loader: `Data_upload/scripts/excel_loader/README.md`

**Key Implementation Guides**
- Chat Assistant: `api/CHAT_ENDPOINTS_IMPLEMENTATION.md`
- Bug Management: `api/ENHANCED_BUG_ENDPOINTS_GUIDE.md`
- Reminder System: `api/REMINDER_SYSTEM.md`
- Session Service: `api/SESSION_SERVICE_IMPLEMENTATION.md`

---

## 9. Support & Maintenance

**Log Locations**
- API Logs: `logs/api.log`
- UI Logs: `logs/ui.log`
- Database Logs: `docker logs worky-postgres`
- Excel Loader Logs: `Data_upload/scripts/excel_loader/logs/`

**Monitoring**
- Prometheus metrics: http://localhost:8007/metrics
- Health check: http://localhost:8007/health

**Backup & Recovery**
- Database backups: `volumes/postgres-data/`
- Export data via API endpoints
- Excel export functionality in UI

---

**Document End**

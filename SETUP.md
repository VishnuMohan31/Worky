# Worky Setup Guide

This guide will help you set up the Worky application from scratch on any platform.

> 📋 **Deployment Ready**: The application is ready for production deployment after completing security configuration. See [DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md) for details.

## Prerequisites

- **Docker Desktop** (includes Docker and Docker Compose)
- **Node.js 18+** (for UI development)
- **Git** (for cloning the repository)

## Quick Start (Fresh Installation)

> ⚠️ **IMPORTANT**: For a fresh clone on a new device, always reset the database to ensure clean initialization.

### 1. Clone the Repository

```bash
git clone https://github.com/datalegos/worky.git
cd worky
```

### 2. Initialize Database (REQUIRED for new devices)

**Windows (PowerShell):**
```powershell
.\db\init_database.ps1 -Reset
```

**macOS/Linux (Bash):**
```bash
./db/init_database.sh --reset
```

### 3. Start All Services

**Windows (PowerShell):**
```powershell
.\App_Development_scripts\start_all.ps1
```

**macOS/Linux (Bash):**
```bash
./App_Development_scripts/start_all.sh
```

**Alternative - Docker Compose Only (All Platforms):**
```bash
# Start database and API via Docker
docker-compose up -d --build

# Start UI separately (in a new terminal)
cd ui
npm install
npm run dev
```

> 📝 **Note**: Database migrations only run when the PostgreSQL container is created for the first time. If you have issues, run `docker-compose down -v` and try again.

This will:
- Start PostgreSQL database on port 5437
- Apply all database migrations automatically
- Load development seed data (on first run)
- Start API server on port 8007
- Start UI development server on port 3007

### 3. Access the Application

- **UI**: http://localhost:3007
- **API**: http://localhost:8007
- **API Docs**: http://localhost:8007/docs

### 4. Verify Setup (Optional but Recommended)

Before logging in, verify everything is set up correctly:

```bash
# Run the verification script
python verify_setup.py
```

This will check:
- Database connectivity
- Database tables exist
- Users are loaded
- API is running

### 5. Login

Use the default admin credentials:
- **Email**: `admin@datalegos.com`
- **Password**: `password`

> ⚠️ **If login fails with 500 error**: See troubleshooting section below for database initialization steps.

## Detailed Setup & Operations Guide

This section provides comprehensive instructions for running and managing the Worky application.

---

## 🚀 How to Start the Application

### Method 1: Automated Script (Recommended for First-Time Setup)

**Windows (PowerShell):**
```powershell
.\App_Development_scripts\start_all.ps1
```

**macOS/Linux (Bash):**
```bash
cd App_Development_scripts
chmod +x start_all.sh
./start_all.sh
```

**What this does:**
1. Starts Docker services (Database + API)
2. Waits for database to be healthy
3. Applies database migrations automatically
4. Loads seed data (if database is empty)
5. Starts UI development server
6. Provides connection details

### Method 2: Docker Compose Only

```bash
# Start database and API
docker-compose up -d --build

# Start UI separately (in a new terminal)
cd ui
npm install
npm run dev
```

### Method 3: Individual Services

Start each service separately:

```bash
# 1. Start Database
./App_Development_scripts/start_db.sh
# OR
docker-compose up -d db

# 2. Wait for database (30-60 seconds)
# Check with: docker exec worky-postgres pg_isready -U postgres

# 3. Start API
./App_Development_scripts/start_api.sh
# OR
docker-compose up -d api

# 4. Start UI
./App_Development_scripts/start_ui.sh
# OR
cd ui && npm run dev
```

---

## 🗄️ Database Setup & Migrations

### Automatic Database Initialization

The database is **automatically initialized** on first run with:
- **33 Migration Files**: Numbered 000-031 (schema) + 999 (seed data)
- **Complete Schema**: All tables, indexes, sequences, functions
- **Seed Data**: Development users and sample data (if database is empty)

### Migration Process

#### How Migrations Work

1. **First Run (Empty Database):**
   - PostgreSQL container runs all `.sql` files from `db/migrations/` in alphabetical order
   - `000_baseline_schema.sql` creates the complete schema
   - Migrations 001-031 apply incremental changes
   - `999_seed_dev_data.sql` loads development data (only if no users exist)

2. **Subsequent Runs:**
   - Only new migrations (if any) are applied
   - Existing tables/objects are skipped (using `IF NOT EXISTS`)
   - Seed data is skipped if users already exist

#### Migration Files Overview

| File | Description |
|------|-------------|
| `000_baseline_schema.sql` | Complete database schema (all tables) |
| `001_initial_schema.sql` | Initial schema additions |
| `002_supporting_tables.sql` | Supporting tables (dependencies, etc.) |
| `003_add_audit_and_soft_delete.sql` | Audit logging and soft delete |
| `004_add_phases.sql` | Phase management |
| `005_add_bugs_and_audit.sql` | Bug tracking system |
| `006_update_user_roles.sql` | User role updates |
| `007_change_to_string_ids.sql` | ID system migration |
| `008_add_entity_notes.sql` | Notes system |
| `009_add_short_long_descriptions.sql` | Description fields |
| `010_add_field_categories.sql` | Field categorization |
| `010a_add_user_view_preferences.sql` | User preferences |
| `011_add_company_settings.sql` | Company settings |
| `012_add_sprint_configuration.sql` | Sprint configuration |
| `013_fix_sprints_table_schema.sql` | Sprint schema fixes |
| `014_add_project_sprint_config.sql` | Project sprint config |
| `015_create_organizations_table.sql` | Organizations |
| `016_create_todo_tables.sql` | Todo system |
| `017_create_chat_assistant_tables.sql` | Chat assistant |
| `018_add_phase_to_user_stories.sql` | User story phases |
| `020_convert_sprints_to_string_ids.sql` | Sprint ID conversion |
| `021_create_team_management_schema.sql` | Team management |
| `022_fix_subtasks_audit_fields.sql` | Subtask fixes |
| `023_make_subtasks_phase_id_nullable.sql` | Subtask phase nullable |
| `024_add_sample_audit_logs.sql` | Sample audit logs |
| `025_add_contact_info_to_clients.sql` | Client contact info |
| `026_extend_users_for_team_management.sql` | User extensions |
| `027_create_notification_system.sql` | Notifications |
| `028_add_decision_tracking.sql` | Decision tracking |
| `029_fix_team_assignment_schema.sql` | Team assignment fixes |
| `030_add_test_management_tables.sql` | Test management |
| `031_add_subtasks_duration_scrum.sql` | Subtask duration |
| `999_seed_dev_data.sql` | Development seed data |

### Manual Database Operations

#### Initialize or Reset Database

```bash
# Initialize database (check status)
./db/init_database.sh

# Reset database (WARNING: destroys all data)
./db/init_database.sh --reset

# Force reset (no confirmation)
./db/init_database.sh --force-reset
```

**What happens:**
- Stops and removes database container
- Deletes all database volumes
- Creates fresh database container
- Runs all migrations automatically
- Loads seed data if database is empty

#### Verify Migrations

```bash
# Check migration status
./db/verify_migrations.sh

# Check tables in database
docker exec worky-postgres psql -U postgres -d worky -c "\dt"

# Count tables
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';"
```

#### Apply Specific Migration Manually

```bash
# Apply a specific migration file
docker exec -i worky-postgres psql -U postgres -d worky < db/migrations/017_create_chat_assistant_tables.sql

# Or use the apply script
./db/apply_migrations.sh db/migrations/017_create_chat_assistant_tables.sql
```

### Database Connection Details

**Connection Information:**
```
Host: localhost
Port: 5437
Database: worky
User: postgres
Password: postgres
```

**Connect via psql:**
```bash
# Interactive shell
docker exec -it worky-postgres psql -U postgres -d worky

# Run a query
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM users;"

# List all tables
docker exec worky-postgres psql -U postgres -d worky -c "\dt"

# Describe a table
docker exec worky-postgres psql -U postgres -d worky -c "\d users"
```

**Using External Tools:**
- **pgAdmin**: Connect to `localhost:5437` with credentials above
- **DBeaver**: Use PostgreSQL connection with same details
- **VS Code**: Use PostgreSQL extension with connection string

---

## 🌱 Seeding Data (Development Data)

### Automatic Seed Data Loading

Seed data is **automatically loaded** when:
- Database is first initialized (empty database)
- No users exist in the database
- Migration `999_seed_dev_data.sql` runs automatically

### Manual Seed Data Operations

#### Load Seed Data

```bash
# Load seed data (only if no users exist)
./db/load_seed_data.sh

# Force reload seed data (even if users exist)
./db/load_seed_data.sh --force
```

**What gets loaded:**
- 9 Users (all with password: `password`)
- 3 Clients
- 2 Programs
- 3 Projects
- 3 Use Cases
- 3 User Stories
- 4 Tasks
- 2 Bugs
- 1 Sprint
- Sample notes, assignments, and relationships

#### Verify Seed Data

```bash
# Check user count
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM users;"

# List all users
docker exec worky-postgres psql -U postgres -d worky -c "SELECT email, role, full_name FROM users;"

# Check other data
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM clients;"
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM projects;"
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM tasks;"
```

### Seed Data Contents

#### Users (All passwords: `password`)

| Email | Role | Full Name |
|-------|------|-----------|
| admin@datalegos.com | Admin | Admin User |
| john@datalegos.com | Developer | John Doe |
| jane@datalegos.com | Project Manager | Jane Smith |
| bob@datalegos.com | Developer | Bob Johnson |
| alice@datalegos.com | DevOps | Alice Williams |
| charlie@datalegos.com | Tester | Charlie Brown |
| david@datalegos.com | Developer | David Lee |
| emily@datalegos.com | Designer | Emily Chen |
| frank@datalegos.com | QA Engineer | Frank Miller |

#### Sample Data Summary

- **Clients**: 3 (DataLegos, Acme Corp, TechStart Inc)
- **Programs**: 2 (Internal Tools, Digital Transformation)
- **Projects**: 3 (Worky Platform, Customer Portal, Mobile App)
- **Use Cases**: 3 (User Authentication, Project Management, Task Tracking)
- **User Stories**: 3 (User Login, Create Project, Assign Tasks)
- **Tasks**: 4 (Database schema, authentication, UI mockups, CI/CD)
- **Bugs**: 2 (Login responsiveness, task filter)
- **Sprints**: 1 (Sprint 1 with linked tasks)
- **Notes**: Multiple entity notes
- **Assignments**: Task and bug assignments

**Note**: Organizations are NOT seeded (only admins can create them)

---

## 🔧 Running Individual Servers

### Database Server

#### Start Database

```bash
# Method 1: Using script
./App_Development_scripts/start_db.sh

# Method 2: Docker Compose
docker-compose up -d db

# Method 3: Docker directly
docker run -d \
  --name worky-postgres \
  -e POSTGRES_DB=worky \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5437:5432 \
  -v ./volumes/postgres-data:/var/lib/postgresql/data \
  -v ./db/migrations:/docker-entrypoint-initdb.d \
  postgres:15
```

#### Stop Database

```bash
# Method 1: Using script
./App_Development_scripts/stop_db.sh

# Method 2: Docker Compose
docker-compose stop db
# OR
docker-compose down  # Stops all services

# Method 3: Docker directly
docker stop worky-postgres
docker rm worky-postgres
```

#### Restart Database

```bash
./App_Development_scripts/restart_db.sh
# OR
docker-compose restart db
```

#### View Database Logs

```bash
docker logs worky-postgres -f
# OR
docker-compose logs db -f
```

#### Check Database Health

```bash
# Check if database is ready
docker exec worky-postgres pg_isready -U postgres

# Check database version
docker exec worky-postgres psql -U postgres -d worky -c "SELECT version();"

# Check database size
docker exec worky-postgres psql -U postgres -d worky -c "SELECT pg_size_pretty(pg_database_size('worky'));"
```

### API Server

#### Start API

```bash
# Method 1: Using script
./App_Development_scripts/start_api.sh

# Method 2: Docker Compose
docker-compose up -d api

# Method 3: Local development (without Docker)
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8007
```

#### Stop API

```bash
# Method 1: Using script
./App_Development_scripts/stop_api.sh

# Method 2: Docker Compose
docker-compose stop api

# Method 3: Docker directly
docker stop worky-api
```

#### Restart API

```bash
./App_Development_scripts/restart_api.sh
# OR
docker-compose restart api
```

#### View API Logs

```bash
docker logs worky-api -f
# OR
docker-compose logs api -f

# Local development logs
tail -f volumes/api-logs/worky-api.log
```

#### Check API Health

```bash
# Health check endpoint
curl http://localhost:8007/health

# API documentation
open http://localhost:8007/docs

# Check API version
curl http://localhost:8007/api/v1/version
```

#### API Configuration

Environment variables (set in `docker-compose.yml`):
- `DATABASE_HOST`: Database host (default: `db`)
- `DATABASE_PORT`: Database port (default: `5432`)
- `DATABASE_NAME`: Database name (default: `worky`)
- `DATABASE_USER`: Database user (default: `postgres`)
- `DATABASE_PASSWORD`: Database password (default: `postgres`)
- `SECRET_KEY`: JWT secret key (default: `your-secret-key-change-in-production`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: `30`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `http://localhost:3007,...`)
- `ENVIRONMENT`: Environment mode (default: `development`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### UI Server

#### Start UI

```bash
# Method 1: Using script
./App_Development_scripts/start_ui.sh

# Method 2: Manual
cd ui
npm install  # First time only
npm run dev
```

#### Stop UI

```bash
# Method 1: Using script
./App_Development_scripts/stop_ui.sh

# Method 2: Find and kill process
# Linux/macOS
lsof -ti:3007 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3007).OwningProcess | Stop-Process
```

#### Restart UI

```bash
./App_Development_scripts/restart_ui.sh
```

#### View UI Logs

```bash
# If started with script
tail -f logs/ui.log

# If started manually, logs appear in terminal
```

#### Check UI Status

```bash
# Check if UI is running
curl http://localhost:3007

# Check UI process
# Linux/macOS
lsof -ti:3007

# Windows
netstat -ano | findstr :3007
```

#### UI Configuration

Configuration in `ui/vite.config.ts`:
```typescript
server: {
  port: 3007,
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: 'http://localhost:8007',
      changeOrigin: true
    }
  }
}
```

**Environment Variables:**
- `VITE_API_BASE_URL`: API base URL (optional, defaults to proxy)
- `VITE_API_TIMEOUT`: API timeout (optional)

---

## 🔄 Service Management

### Start All Services

```bash
# Automated script (recommended)
./App_Development_scripts/start_all.sh

# Docker Compose only (DB + API)
docker-compose up -d --build

# Then start UI separately
cd ui && npm run dev
```

### Stop All Services

```bash
# Automated script
./App_Development_scripts/stop_all.sh

# Docker Compose
docker-compose down

# Stop UI separately (if started manually)
# Find process on port 3007 and kill it
```

### Restart All Services

```bash
# Automated script
./App_Development_scripts/restart_all.sh

# Docker Compose
docker-compose restart

# Restart UI separately
./App_Development_scripts/restart_ui.sh
```

### Check Service Status

```bash
# Check Docker containers
docker ps

# Check all services
docker-compose ps

# Check specific service
docker ps | grep worky-postgres
docker ps | grep worky-api

# Check UI process
lsof -ti:3007  # Linux/macOS
netstat -ano | findstr :3007  # Windows
```

### View All Logs

```bash
# All Docker services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db

# UI logs (if started with script)
tail -f logs/ui.log
```

### API Setup

The API is a FastAPI application running in Docker.

#### Development Mode

```bash
# Start API only
./App_Development_scripts/start_api.sh

# Restart API
./App_Development_scripts/restart_api.sh

# Stop API
./App_Development_scripts/stop_api.sh

# View API logs
docker logs worky-api -f
```

#### API Configuration

Environment variables are set in `docker-compose.yml`:
- `DATABASE_HOST`: Database host (default: db)
- `DATABASE_PORT`: Database port (default: 5432)
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)

### UI Setup

The UI is a React + TypeScript application using Vite.

#### Development Mode

```bash
# Start UI only
./App_Development_scripts/start_ui.sh

# Restart UI
./App_Development_scripts/restart_ui.sh

# Stop UI
./App_Development_scripts/stop_ui.sh
```

#### UI Configuration

The UI proxies API requests through Vite. Configuration in `ui/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8007',
    changeOrigin: true
  }
}
```

## Development Seed Data

The application comes with pre-loaded development data. Seed data is automatically loaded via the migration file `db/migrations/999_seed_dev_data.sql`, which runs automatically after all schema migrations when the database is first initialized.

**Note**: The seed data migration (`999_seed_dev_data.sql`) will only insert data if no users exist in the database, making it safe to run on fresh installations.

### Seed Data Contents

The application comes with pre-loaded development data:

### Users (all with password: `password`)

| Email | Role | Full Name |
|-------|------|-----------|
| admin@datalegos.com | Admin | Admin User |
| john@datalegos.com | Developer | John Doe |
| jane@datalegos.com | Project Manager | Jane Smith |
| bob@datalegos.com | Developer | Bob Johnson |
| alice@datalegos.com | DevOps | Alice Williams |
| charlie@datalegos.com | Tester | Charlie Brown |

### Sample Data

- **3 Clients**: DataLegos, Acme Corp, TechStart Inc
- **2 Programs**: Internal Tools, Digital Transformation
- **3 Projects**: Worky Platform, Customer Portal, Mobile App
- **3 Use Cases**: User Authentication, Project Management, Task Tracking
- **3 User Stories**: User Login, Create Project, Assign Tasks
- **4 Tasks**: Database schema, authentication, UI mockups, CI/CD
- **2 Bugs**: Login responsiveness, task filter
- **1 Sprint**: Sprint 1 with linked tasks

## Troubleshooting

### Fresh Clone Issues

**Problem**: Database schema errors after cloning to a new device
```bash
# The database is initialized from SQL files in db/migrations/
# If you see errors, make sure to delete old volumes first:
docker-compose down -v
docker-compose up -d --build
```

**Problem**: Migration 029 not applied (for existing databases)
```bash
# Apply the fix migration manually:
docker exec -i worky-postgres psql -U postgres -d worky < db/migrations/029_fix_team_assignment_schema.sql
```

### Database Issues

**Problem**: Database container won't start
```bash
# Check logs
docker logs worky-postgres

# Remove volumes and recreate (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d db
```

**Problem**: Migrations not applied
```bash
# Check if migrations directory is mounted
docker exec worky-postgres ls /docker-entrypoint-initdb.d

# Manually apply all migrations
docker exec worky-postgres psql -U postgres -d worky -c "\i /docker-entrypoint-initdb.d/021_create_team_management_schema.sql"
```

**Problem**: Seed data not loaded
```bash
# Check if users exist
docker exec worky-postgres psql -U postgres -d worky -c "SELECT COUNT(*) FROM users;"

# Load seed data manually (all platforms)
docker exec -i worky-postgres psql -U postgres -d worky < db/migrations/999_seed_dev_data.sql
```

### API Issues

**Problem**: API returns 500 errors
```bash
# Check API logs
docker logs worky-api -f

# Restart API
./App_Development_scripts/restart_api.sh
```

**Problem**: Database connection errors
```bash
# Verify database is running
docker ps | grep postgres

# Check database connectivity
docker exec worky-api ping db
```

### UI Issues

**Problem**: Login fails with 500 error
```bash
# First, verify your setup
python verify_setup.py

# Check API logs for detailed error messages
docker logs worky-api -f

# Common causes and solutions:

# 1. Database not initialized
docker-compose down -v
docker-compose up -d --build

# 2. Database tables missing (migrations not applied)
docker exec worky-postgres psql -U postgres -d worky -c "\dt" | grep users
# If users table doesn't exist, reset database:
docker-compose down -v
docker-compose up -d db
# Wait for migrations to complete, then start API

# 3. No users in database (seed data not loaded)
docker exec -i worky-postgres psql -U postgres -d worky < db/migrations/999_seed_dev_data.sql

# 4. Database connection issues
# Check if database is accessible from API container:
docker exec worky-api ping -c 2 db
# Check database health:
curl http://localhost:8007/health
```

**Problem**: Getting "Database connection failed" or "Database tables not initialized" errors
- This means the database isn't ready or migrations haven't run
- Run the verification script: `python verify_setup.py`
- Reset database: `docker-compose down -v && docker-compose up -d --build`
- Wait 30-60 seconds for migrations to complete before trying to login

**Problem**: UI won't start
```bash
# Install dependencies
cd ui
npm install

# Start UI
npm run dev
```

**Problem**: UI shows error screen on first load (especially on new devices)
- **This has been fixed!** The `queryClient.ts` file now safely handles environment variable initialization
- If you still see this issue:
  1. Clear browser cache and hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
  2. Verify you have the latest code with the fix
  3. Restart the UI server:
     ```bash
     ./App_Development_scripts/stop_ui.sh
     ./App_Development_scripts/start_ui.sh
     ```
- The fix ensures `import.meta.env.MODE` is safely accessed with fallbacks, preventing initialization errors

### Windows-Specific Issues

**Problem**: Shell scripts (.sh) don't work on Windows
```powershell
# Use the PowerShell versions instead:
.\App_Development_scripts\start_all.ps1
.\App_Development_scripts\stop_all.ps1

# Or run docker-compose directly:
docker-compose up -d --build
cd ui; npm run dev
```

**Problem**: Line ending issues with shell scripts (if using Git Bash/WSL)
```bash
# Convert line endings
sed -i 's/\r$//' App_Development_scripts/*.sh
```

**Problem**: PowerShell execution policy blocks scripts
```powershell
# Run this as Administrator (one-time setup):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Authentication Issues

**Problem**: Password doesn't work
- Default password is: `password`
- If still failing, reload seed data:
```bash
./db/load_seed_data.sh --force
```

## Service Management Scripts

All scripts are located in `App_Development_scripts/`:

### Windows (PowerShell)
- `start_all.ps1` - Start all services (DB, API, UI)
- `stop_all.ps1` - Stop all services

### macOS/Linux (Bash)
- `start_all.sh` - Start all services (DB, API, UI)
- `start_db.sh` - Start database only
- `start_api.sh` - Start API only
- `start_ui.sh` - Start UI only
- `stop_all.sh` - Stop all services
- `stop_db.sh` - Stop database only
- `stop_api.sh` - Stop API only
- `stop_ui.sh` - Stop UI only
- `restart_all.sh` - Restart all services

### Cross-Platform (Docker)
```bash
# Start all Docker services
docker-compose up -d --build

# Stop all Docker services
docker-compose down

# View logs
docker-compose logs -f
```

## Next Steps

After setup:
1. Explore the API documentation at http://localhost:8007/docs
2. Login to the UI at http://localhost:3007
3. Review the database schema in `db/migrations/`
4. Check out the API code in `api/app/`
5. Explore the UI code in `ui/src/`

## Additional Resources

- [Deployment Readiness](DEPLOYMENT_READINESS.md) - Production deployment status and checklist
- [Deployment Guide](DEPLOYMENT.md) - Step-by-step production deployment instructions
- [Database README](db/README.md) - Database migrations and schema
- [API README](api/README.md) - API documentation
- [UI README](ui/README.md) - UI development guide
- [Knowledge Transfer](Knowledge_transfer/WORKY_KT_DOCUMENT.md) - System architecture

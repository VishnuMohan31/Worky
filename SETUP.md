# Worky Setup Guide

This guide will help you set up the Worky application from scratch on any platform.

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

### 4. Login

Use the default admin credentials:
- **Email**: `admin@datalegos.com`
- **Password**: `password`

## Detailed Setup

### Database Setup

The database is automatically initialized on first run with:
- All schema migrations (18 migration files)
- Development seed data (users, projects, tasks, etc.)

#### Manual Database Operations

```bash
# Initialize or reset database
./db/init_database.sh

# Reset database (WARNING: destroys all data)
./db/init_database.sh --reset

# Load seed data manually
./db/load_seed_data.sh

# Force reload seed data
./db/load_seed_data.sh --force

# Apply specific migration
./db/apply_migrations.sh migrations/017_create_chat_assistant_tables.sql

# Verify migrations
./db/verify_migrations.sh
```

#### Database Connection

```
Host: localhost
Port: 5437
Database: worky
User: postgres
Password: postgres
```

Connect via psql:
```bash
docker exec -it worky-postgres psql -U postgres -d worky
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
docker exec -i worky-postgres psql -U postgres -d worky < db/seeds/dev_seed.sql
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
- Check that API is running on port 8007
- Verify proxy configuration in `ui/vite.config.ts`
- Check browser console for errors

**Problem**: UI won't start
```bash
# Install dependencies
cd ui
npm install

# Start UI
npm run dev
```

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

- [Database README](db/README.md) - Database migrations and schema
- [API README](api/README.md) - API documentation
- [UI README](ui/README.md) - UI development guide
- [Knowledge Transfer](Knowledge_transfer/WORKY_KT_DOCUMENT.md) - System architecture

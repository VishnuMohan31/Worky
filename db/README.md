# Worky Database Migrations

This directory contains all database schema migrations for the Worky application.

## Directory Structure

```
db/
├── migrations/          # SQL migration files (executed in alphabetical order)
├── seeds/              # Seed data for development
├── db_loader/          # Scripts for loading data from Google Sheets
├── apply_migrations.sh # Script to apply migrations to running container
├── verify_migrations.sh # Script to verify migration files
└── README.md           # This file
```

## Migration Files

All migration files are located in `db/migrations/` and follow the naming convention:
```
NNN_description.sql
```

Where:
- `NNN` is a zero-padded sequential number (001, 002, etc.)
- `description` is a brief description of the migration

### Current Migrations

1. **001_initial_schema.sql** - Core tables (users, clients, programs, projects, etc.)
2. **002_supporting_tables.sql** - Supporting tables and relationships
3. **003_add_audit_and_soft_delete.sql** - Audit trail and soft delete functionality
4. **004_add_phases.sql** - Work phases (Development, Testing, etc.)
5. **005_add_bugs_and_audit.sql** - Bug tracking and audit logs
6. **006_update_user_roles.sql** - User role updates
7. **007_change_to_string_ids.sql** - Convert IDs to string format
8. **008_add_entity_notes.sql** - Notes functionality for entities
9. **009_add_short_long_descriptions.sql** - Description fields
10. **010_add_field_categories.sql** - UI field categorization metadata
11. **010a_add_user_view_preferences.sql** - User view preferences (tile/list)
12. **011_add_company_settings.sql** - Company-wide settings
13. **012_add_sprint_configuration.sql** - Sprint configuration
14. **013_fix_sprints_table_schema.sql** - Sprint table fixes
15. **014_add_project_sprint_config.sql** - Project-level sprint config
16. **015_create_organizations_table.sql** - Organizations table
17. **016_create_todo_tables.sql** - TODO items and adhoc notes
18. **017_create_chat_assistant_tables.sql** - Chat assistant tables (messages, audit, reminders)

## Automatic Initialization

When you start the database container for the first time using `docker-compose up`, PostgreSQL will automatically execute all SQL files in the `db/migrations/` directory in **alphabetical order**.

This is configured in `docker-compose.yml`:
```yaml
volumes:
  - ./db/migrations:/docker-entrypoint-initdb.d
```

### Important Notes

1. **First-time setup only**: Migrations are only executed when the database is first created
2. **Alphabetical order**: Files are executed in alphabetical order (001, 002, 010, 010a, 011, etc.)
3. **Idempotent**: All migrations use `CREATE TABLE IF NOT EXISTS` to be idempotent
4. **No rollback**: Once executed, migrations cannot be automatically rolled back

## Manual Migration Application

If you need to apply migrations to an existing database:

### Apply all migrations
```bash
./db/apply_migrations.sh
```

### Apply a specific migration
```bash
./db/apply_migrations.sh migrations/017_create_chat_assistant_tables.sql
```

## Verification

To verify all migration files are present and properly ordered:

```bash
./db/verify_migrations.sh
```

This will:
- Count migration files
- List them in execution order
- Check for duplicate migration numbers
- Verify required tables are defined

## Database Reset

To completely reset the database and reapply all migrations:

```bash
# Stop and remove the database container
docker-compose down -v

# Start fresh (migrations will run automatically)
docker-compose up -d db
```

## Creating New Migrations

When creating a new migration:

1. **Number sequentially**: Use the next available number (e.g., 018)
2. **Descriptive name**: Use a clear, descriptive name
3. **Idempotent**: Use `IF NOT EXISTS` clauses
4. **Comments**: Add comments explaining the purpose
5. **Test**: Test the migration on a fresh database

Example:
```sql
-- Migration: Add feature X
-- Description: Creates tables for feature X
-- Date: YYYY-MM-DD

CREATE TABLE IF NOT EXISTS my_table (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_my_table_name ON my_table(name);

-- Add comments
COMMENT ON TABLE my_table IS 'Description of the table';
```

## Required Tables

The following tables are required for the application to function:

### Core Hierarchy
- `users` - User accounts
- `clients` - Top-level clients
- `programs` - Client programs
- `projects` - Program projects
- `usecases` - Project use cases
- `user_stories` - Use case user stories
- `tasks` - User story tasks
- `subtasks` - Task subtasks

### Supporting Tables
- `phases` - Work phases (Development, Testing, etc.)
- `bugs` - Bug tracking
- `entity_notes` - Notes for any entity
- `organizations` - Organization management
- `company_settings` - Company-wide settings

### TODO & Productivity
- `todo_items` - User TODO items
- `adhoc_notes` - Quick notes

### Chat Assistant
- `chat_messages` - Chat conversation messages
- `chat_audit_logs` - Audit trail for chat interactions
- `reminders` - User reminders

### Sprint Management
- `sprints` - Sprint definitions
- `sprint_tasks` - Tasks in sprints
- `project_sprint_config` - Project-level sprint configuration

## Troubleshooting

### Migrations not running
- Ensure the database container is being created fresh
- Check `docker-compose logs db` for errors
- Verify the volume mount in `docker-compose.yml`

### Duplicate migration numbers
- Rename files to ensure unique sequential numbers
- Use suffixes like `010a` if needed for ordering

### Migration errors
- Check SQL syntax
- Ensure foreign key references exist
- Verify data types match

## Database Connection

Default connection details (development):
```
Host: localhost
Port: 5437
Database: worky
User: postgres
Password: postgres
```

## Seed Data

Development seed data is available in `db/seeds/dev_data.sql`. To load:

```bash
docker exec -i worky-postgres psql -U postgres -d worky < db/seeds/dev_data.sql
```

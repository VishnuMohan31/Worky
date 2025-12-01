# Database Quick Start Guide

## First Time Setup

### 1. Start the Database

```bash
docker-compose up -d db
```

This will:
- Create a PostgreSQL container named `worky-postgres`
- Automatically execute all migrations in `db/migrations/` (in alphabetical order)
- Create all required tables and indexes
- Set up the database schema

### 2. Verify Setup

```bash
./db/verify_migrations.sh
```

This checks:
- All migration files are present
- No duplicate migration numbers
- All required tables are defined

### 3. Initialize/Verify Database

```bash
./db/init_database.sh
```

This will:
- Check if the database container is running
- Verify all required tables exist
- Display connection information

## Reset Database (Clean Start)

If you need to completely reset the database:

```bash
./db/init_database.sh --reset
```

⚠️ **Warning**: This will destroy all existing data!

## Manual Migration Application

If migrations didn't run automatically or you need to apply them manually:

```bash
# Apply all migrations
./db/apply_migrations.sh

# Apply a specific migration
./db/apply_migrations.sh migrations/017_create_chat_assistant_tables.sql
```

## Database Connection

### From Host Machine

```
Host: localhost
Port: 5437
Database: worky
User: postgres
Password: postgres
```

### From Docker Container

```
Host: db
Port: 5432
Database: worky
User: postgres
Password: postgres
```

## Common Commands

### Connect to Database

```bash
docker exec -it worky-postgres psql -U postgres -d worky
```

### List All Tables

```bash
docker exec -it worky-postgres psql -U postgres -d worky -c '\dt'
```

### View Table Schema

```bash
docker exec -it worky-postgres psql -U postgres -d worky -c '\d table_name'
```

### Check Database Logs

```bash
docker-compose logs db
```

### Stop Database

```bash
docker-compose stop db
```

### Remove Database (with data)

```bash
docker-compose down -v
```

## Load Seed Data (Development)

```bash
docker exec -i worky-postgres psql -U postgres -d worky < db/seeds/dev_data.sql
```

## Troubleshooting

### Migrations Not Running

**Problem**: Tables are not created after starting the container

**Solution**:
1. Check if this is a fresh database (migrations only run on first creation)
2. If database already exists, apply migrations manually:
   ```bash
   ./db/apply_migrations.sh
   ```
3. Or reset the database:
   ```bash
   ./db/init_database.sh --reset
   ```

### Container Won't Start

**Problem**: Database container fails to start

**Solution**:
1. Check logs: `docker-compose logs db`
2. Ensure port 5437 is not in use: `lsof -i :5437`
3. Remove old volumes: `docker-compose down -v`
4. Start fresh: `docker-compose up -d db`

### Connection Refused

**Problem**: Cannot connect to database

**Solution**:
1. Verify container is running: `docker ps | grep worky-postgres`
2. Check health status: `docker inspect worky-postgres | grep Health`
3. Wait for database to be ready (can take 10-30 seconds)
4. Check port mapping: `docker port worky-postgres`

### Missing Tables

**Problem**: Some tables are missing

**Solution**:
1. Run verification: `./db/verify_migrations.sh`
2. Check which migrations failed: `docker-compose logs db | grep ERROR`
3. Apply migrations manually: `./db/apply_migrations.sh`

## Migration Files

All migrations are in `db/migrations/` and are executed in alphabetical order:

1. `001_initial_schema.sql` - Core tables
2. `002_supporting_tables.sql` - Supporting tables
3. `003_add_audit_and_soft_delete.sql` - Audit functionality
4. `004_add_phases.sql` - Work phases
5. `005_add_bugs_and_audit.sql` - Bug tracking
6. `006_update_user_roles.sql` - User roles
7. `007_change_to_string_ids.sql` - String IDs
8. `008_add_entity_notes.sql` - Notes
9. `009_add_short_long_descriptions.sql` - Descriptions
10. `010_add_field_categories.sql` - Field categories
11. `010a_add_user_view_preferences.sql` - View preferences
12. `011_add_company_settings.sql` - Company settings
13. `012_add_sprint_configuration.sql` - Sprint config
14. `013_fix_sprints_table_schema.sql` - Sprint fixes
15. `014_add_project_sprint_config.sql` - Project sprint config
16. `015_create_organizations_table.sql` - Organizations
17. `016_create_todo_tables.sql` - TODO items
18. `017_create_chat_assistant_tables.sql` - **Chat assistant** (NEW)

## Required Tables for Chat Feature

The chat assistant requires these tables (created by migration 017):

- **chat_messages** - Stores conversation messages
- **chat_audit_logs** - Audit trail for chat interactions
- **reminders** - User reminders created via chat

## Next Steps

After database setup:

1. Start the API server: `docker-compose up -d api`
2. Start the UI: `cd ui && npm run dev`
3. Access the application: `http://localhost:5173`

## Additional Resources

- Full documentation: `db/README.md`
- Migration verification: `./db/verify_migrations.sh`
- Database initialization: `./db/init_database.sh`
- Apply migrations: `./db/apply_migrations.sh`

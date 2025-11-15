# Alembic Setup Complete ✓

Alembic has been successfully configured to keep your database schema and SQLAlchemy models in sync.

## What Was Done

1. **Initialized Alembic** in the `api/` directory
2. **Configured async database support** for PostgreSQL with asyncpg
3. **Imported all models** so Alembic can detect changes
4. **Created baseline migration** from the existing database schema
5. **Stamped database** to mark current state as the baseline

## Current Status

- **Database Version**: 41ee2f43d014 (head)
- **Migration**: "Sync models with existing database schema"
- **Status**: ✓ Models and database are in sync

## How to Use

### When You Change a Model

1. Edit your model in `app/models/`
2. Create a migration:
   ```bash
   cd api
   ./migrate.sh create "Description of your change"
   ```
3. Review the generated migration in `alembic/versions/`
4. Apply the migration:
   ```bash
   ./migrate.sh upgrade
   ```

### Example Workflow

```bash
# 1. Add a new column to User model
# Edit app/models/user.py

# 2. Generate migration
./migrate.sh create "Add phone_number to users"

# 3. Review the migration file
# Check alembic/versions/xxxxx_add_phone_number_to_users.py

# 4. Apply migration
./migrate.sh upgrade

# 5. Verify
./migrate.sh current
```

## Helper Script Commands

```bash
./migrate.sh create "message"  # Create new migration
./migrate.sh upgrade           # Apply migrations
./migrate.sh downgrade         # Rollback last migration
./migrate.sh history           # Show all migrations
./migrate.sh current           # Show current version
./migrate.sh check             # Check for pending migrations
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic is smart but not perfect
2. **Test migrations on development first** before production
3. **Commit migrations with model changes** to version control
4. **Never edit applied migrations** - create a new one instead
5. **Backup database before migrations** in production

## Configuration Files

- `alembic.ini` - Main configuration
- `alembic/env.py` - Environment setup (imports models)
- `alembic/versions/` - Migration scripts
- `.env` - Database connection settings

## Troubleshooting

### "Target database is not up to date"
```bash
./migrate.sh upgrade
```

### "Multiple heads detected"
```bash
cd api
alembic merge heads -m "Merge migrations"
```

### Check what changes Alembic would generate
```bash
cd api
alembic revision --autogenerate -m "test" --sql
# This shows SQL without creating a migration
```

## Integration with Development

The migration system is now part of your development workflow:

1. **Models are the source of truth** - Define your schema in SQLAlchemy models
2. **Alembic generates migrations** - Automatically detects model changes
3. **Migrations update database** - Apply changes to PostgreSQL
4. **Version control tracks everything** - Migrations are committed with code

## Next Steps

- When you modify any model, use `./migrate.sh create "description"`
- Before deploying, run `./migrate.sh upgrade` on target environment
- Keep migrations in version control alongside your code

For more details, see `MIGRATIONS.md`

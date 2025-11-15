# Database Migrations with Alembic

This project uses Alembic to manage database schema migrations and keep models in sync with the database.

## Quick Reference

### Create a new migration after model changes
```bash
cd api
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations to database
```bash
cd api
alembic upgrade head
```

### Rollback last migration
```bash
cd api
alembic downgrade -1
```

### View migration history
```bash
cd api
alembic history
```

### View current database version
```bash
cd api
alembic current
```

## Workflow

1. **Make changes to your SQLAlchemy models** in `api/app/models/`

2. **Generate a migration**:
   ```bash
   cd api
   alembic revision --autogenerate -m "Add new column to users table"
   ```

3. **Review the generated migration** in `api/alembic/versions/`
   - Alembic auto-generates migrations but always review them
   - Add any custom data migrations if needed

4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

5. **Commit both the model changes and migration file** to version control

## Important Notes

- **Always review auto-generated migrations** before applying them
- **Never edit applied migrations** - create a new migration instead
- **Keep models and database in sync** - don't make manual database changes
- **Test migrations** on a development database before production
- **Backup your database** before running migrations in production

## Configuration

- **alembic.ini**: Main configuration file
- **alembic/env.py**: Environment configuration (imports all models)
- **alembic/versions/**: Migration scripts directory

The database connection is configured from environment variables:
- DATABASE_HOST
- DATABASE_PORT
- DATABASE_NAME
- DATABASE_USER
- DATABASE_PASSWORD

## Troubleshooting

### Migration conflicts
If you have multiple developers creating migrations:
```bash
alembic merge heads -m "Merge migrations"
```

### Reset to a specific version
```bash
alembic downgrade <revision_id>
```

### Start fresh (DANGER - drops all data)
```bash
alembic downgrade base
alembic upgrade head
```

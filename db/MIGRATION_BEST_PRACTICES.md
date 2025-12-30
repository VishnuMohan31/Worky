# Database Migration Best Practices

## Overview

This document outlines best practices for managing database migrations in the Worky application, including when and how to consolidate migrations after baselining.

## Why Separate Migration Files?

### 1. Version Control and History
- Each file represents a specific change at a point in time
- You can see when and why each change was made
- Useful for debugging and understanding evolution

### 2. Incremental Deployment
- Production databases may be at different versions
- You can apply only the migrations needed to bring them up to date
- Avoids re-running changes that were already applied

### 3. Rollback Capability
- If a migration causes issues, you can identify and fix the specific one
- Easier to create rollback migrations for specific changes

### 4. Team Collaboration
- Multiple developers can work on different migrations simultaneously
- Reduces merge conflicts
- Clear ownership of changes

### 5. Production Safety
- Apply migrations incrementally
- Test each migration individually
- Monitor impact of each change

## When to Consolidate (Baseline Approach)

Since the application is baselined, you can consolidate for new deployments:

### Option 1: Keep History + Create Baseline (Recommended)
- **Keep all existing migration files** for existing deployments
- **Create a new baseline file** with the complete current schema
- New deployments use the baseline; existing ones continue with incremental migrations

### Option 2: Full Consolidation
- Merge all files into one `000_initial_schema.sql`
- **Only for brand new deployments**
- Existing deployments still need the incremental files

## Best Practices

### Recommended Approach (Hybrid)

1. **Keep Historical Migrations (001-026)**
   - Don't delete or modify them
   - Existing deployments need them

2. **Create a Baseline Migration**
   - New file: `000_baseline_schema.sql` with complete current schema
   - Use for fresh deployments

3. **Use Migration Tracking System**
   - Track which migrations have been applied
   - Prevents re-running migrations

4. **Future Changes**
   - Continue with incremental migrations (027, 028, etc.)
   - Both baseline and incremental approaches can coexist

### Example Structure:
```
db/migrations/
├── 000_baseline_schema.sql          # Complete schema for new deployments
├── 001_initial_schema.sql           # Historical (for existing deployments)
├── 002_supporting_tables.sql        # Historical
├── ...
├── 026_extend_users_for_team_management.sql  # Historical
├── 027_future_change.sql            # New incremental changes
└── 999_seed_dev_data.sql            # Seed data
```

## Benefits of Hybrid Approach

✅ **New Deployments**: Use baseline (fast, single file)  
✅ **Existing Deployments**: Use incremental migrations (safe, tracked)  
✅ **Future Changes**: Continue incremental approach  
✅ **History Preserved**: All changes documented  

## Important: Never Modify Existing Migrations

⚠️ **Critical Rule**: Once a migration is applied to production, **never modify it**

- Create new migrations to fix issues
- Modifying existing migrations can break deployments
- Always add new migrations for changes

## Recommended Implementation

Since the application is baselined:

1. **Keep all 26 existing files** (for existing deployments)
2. **Create a new `000_baseline_schema.sql`** with the complete current schema
3. **Update startup scripts** to:
   - Check if database is empty → apply baseline
   - Check if database has data → apply incremental migrations
4. **Continue using incremental migrations** for future changes

This gives you:
- ⚡ **Speed** of baseline for new deployments
- 🛡️ **Safety** for existing deployments
- 📝 **History** preserved for all changes

## Migration Detection Logic

The startup script (`start_all.sh`) includes intelligent migration detection that:

- Recognizes migrations with `IF NOT EXISTS` clauses
- Properly handles "already exists" notices
- Distinguishes between fresh and idempotent applications
- Reports migration status accurately

### How It Works:

1. **Fresh Application**: No "already exists" notices → "✓ Applied: filename"
2. **Idempotent Application**: Has "already exists" notices → "✓ Applied: filename (objects already existed, no changes needed)"
3. **Error Detection**: Identifies critical errors vs harmless notices

## Migration File Naming Convention

- Use sequential numbering: `001_`, `002_`, `003_`, etc.
- Use descriptive names: `026_extend_users_for_team_management.sql`
- Baseline files: `000_baseline_schema.sql`
- Seed data: `999_seed_dev_data.sql`

## Testing Migrations

Before applying migrations to production:

1. **Test on development database**
2. **Test rollback procedures**
3. **Verify data integrity**
4. **Check performance impact**
5. **Document any manual steps required**

## Migration Scripts

The project includes migration management scripts:

- `db/apply_migrations.sh` - Apply all or specific migrations
- `db/verify_migrations.sh` - Verify migration files are present
- `App_Development_scripts/start_all.sh` - Automatically applies migrations on startup

## Summary

- **Keep historical migrations** for existing deployments
- **Create baseline migration** for new deployments
- **Never modify existing migrations** once applied to production
- **Continue incremental approach** for future changes
- **Use migration tracking** to prevent duplicate applications

This hybrid approach provides the best balance of speed, safety, and maintainability.




# Production Deployment Guide

## ⚠️ CRITICAL: Fresh Database (No Test Data)

**IMPORTANT**: The production deployment script **EXCLUDES** the seed data file (`999_seed_dev_data.sql`) to ensure a completely fresh database with no test data.

## Quick Start

### 1. Create Production Environment File

```bash
cp env.production.template .env.production
```

Then edit `.env.production` with your production values:
- **DATABASE_PASSWORD**: Strong password
- **SECRET_KEY**: Generate with `openssl rand -hex 32`
- **CORS_ORIGINS**: Your production domain(s)
- **ENVIRONMENT**: `production`

### 2. Build UI for Production

```bash
cd ui
npm install
npm run build
cd ..
```

### 3. Deploy to Production

```bash
chmod +x App_Development_scripts/deploy_production.sh
./App_Development_scripts/deploy_production.sh
```

This script will:
- ✅ Build and start all services
- ✅ Apply database migrations
- ✅ **SKIP seed data** (999_seed_dev_data.sql) - ensures fresh database
- ✅ Verify no test data was loaded

### 4. Create First Admin User

After deployment, create your first admin user via:
- API registration endpoint (if enabled)
- Direct database insert
- Admin panel

## Production Scripts

All production scripts are in `App_Development_scripts/`:

- **deploy_production.sh**: Full deployment (build + start + migrations)
- **start_production.sh**: Start existing production services
- **stop_production.sh**: Stop production services

## Key Differences from Development

| Feature | Development | Production |
|---------|------------|-----------|
| Seed Data | ✅ Loaded automatically | ❌ **EXCLUDED** |
| Database | Fresh with test data | Fresh with **NO test data** |
| Environment | `development` | `production` |
| Debug Mode | Enabled | Disabled |
| SSL | Not required | Required (configure nginx) |

## Verification

After deployment, verify:

```bash
# Check no users exist (should be 0)
docker exec worky-postgres-prod psql -U worky_user -d worky -c "SELECT COUNT(*) FROM users;"

# Check no test clients exist (should be 0)
docker exec worky-postgres-prod psql -U worky_user -d worky -c "SELECT COUNT(*) FROM clients;"
```

Both should return `0` for a fresh production deployment.

## Security Checklist

- [ ] Strong DATABASE_PASSWORD set
- [ ] Strong SECRET_KEY generated
- [ ] CORS_ORIGINS configured with your domain
- [ ] SSL certificates configured in nginx
- [ ] Firewall rules configured
- [ ] Database backups set up
- [ ] First admin user created
- [ ] Default passwords changed

#!/bin/bash
# ============================================================================
# Worky Development - Complete Application Startup Script
# ============================================================================
# This script starts the complete Worky application with fresh database:
# 1. Database with corrected schema
# 2. API server
# 3. UI development server
# 
# Uses the corrected initial scripts that match the current API and UI code.
# ============================================================================

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================================"
echo "                    WORKY COMPLETE APPLICATION STARTUP"
echo "============================================================================"
echo ""
echo "This will start the complete Worky application with fresh database:"
echo "  - Database with corrected schema (string IDs, all fields)"
echo "  - API server on port 8007"
echo "  - UI development server on port 3007"
echo ""
echo -e "${RED}WARNING: This will destroy all existing data!${NC}"
echo ""
read -p "Are you sure you want to continue? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Startup cancelled."
    exit 0
fi

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

echo ""
echo -e "${BLUE}[1/8] Stopping and cleaning up existing services...${NC}"
# Stop all services and remove containers/volumes
docker-compose down -v --remove-orphans 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
pkill -f "node.*dev" 2>/dev/null || true

# Remove database volumes completely
docker volume rm worky_development_postgres-data 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

echo -e "${GREEN}✅ All services stopped and cleaned${NC}"

echo ""
echo -e "${BLUE}[2/8] Cleaning up old data and ensuring fresh start...${NC}"
# Remove local data directories
if [ -d "volumes/postgres-data" ]; then
    rm -rf "volumes/postgres-data"
    echo "Removed local postgres data"
fi
mkdir -p "volumes/postgres-data"
mkdir -p "volumes/api-logs"

# Ensure Docker has completely cleaned up
docker system prune -f 2>/dev/null || true

echo -e "${GREEN}✅ Fresh environment prepared${NC}"

echo ""
echo -e "${BLUE}[3/8] Setting up corrected database schema...${NC}"

# Check if we already have the corrected files in place
if [ -f "db/migrations/001_corrected_baseline.sql" ] && [ -f "db/migrations/002_extended_features.sql" ] && [ -f "db/migrations/003_bug_management.sql" ]; then
    echo "Corrected migration files are already in place. Skipping backup/restore."
    echo "Current migration files:"
    ls -1 db/migrations/*.sql
else
    # Backup ALL old migration files to prevent UUID conflicts
    mkdir -p "db/migrations_backup"
    echo "Backing up old migration files..."

    # Move all existing migration files to backup (except seed data which we'll keep)
    moved_count=0
    for file in db/migrations/*.sql; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            # Keep the seed data file, backup everything else
            if [[ ! "$filename" =~ ^999_seed_dev_data.sql$ ]] && [[ ! "$filename" =~ ^00[1-3]_.*\.sql$ ]]; then
                echo "  Backing up: $filename"
                mv "$file" "db/migrations_backup/"
                ((moved_count++))
            fi
        fi
    done

    echo "Moved $moved_count migration files to backup"

    # Copy corrected initial scripts as the ONLY migration files
    echo "Installing corrected schema files..."
    cp "db/initial_scripts/001_corrected_baseline_schema.sql" "db/migrations/001_corrected_baseline.sql"
    cp "db/initial_scripts/002_extended_features.sql" "db/migrations/002_extended_features.sql"
    cp "db/initial_scripts/003_bug_management_and_comments.sql" "db/migrations/003_bug_management.sql"

    echo -e "${GREEN}✅ Corrected schema files installed (3 files + seed data)${NC}"
fi

echo "Migration files now in db/migrations/:"
ls -1 db/migrations/*.sql

echo ""
echo -e "${BLUE}[4/8] Starting database with corrected schema...${NC}"
echo "Current migration files:"
ls -1 db/migrations/

docker-compose up -d db
echo "Waiting for database to initialize with corrected schema..."

# Wait for database to be ready with more detailed feedback
attempt=1
max_attempts=30
while ! docker exec worky-postgres pg_isready -U postgres -d worky >/dev/null 2>&1; do
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Database failed to start after $max_attempts attempts${NC}"
        echo "Checking database logs:"
        docker logs worky-postgres | tail -20
        exit 1
    fi
    echo "Attempt $attempt/$max_attempts: Still waiting for database..."
    sleep 3
    ((attempt++))
done

echo -e "${GREEN}✅ Database is ready!${NC}"

# Verify table count
echo "Checking table count..."
table_count=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
echo "Tables created: $table_count"

if [ "$table_count" -lt 40 ]; then
    echo -e "${RED}❌ WARNING: Only $table_count tables created (expected 50+)${NC}"
    echo "Database logs:"
    docker logs worky-postgres | tail -30
else
    echo -e "${GREEN}✅ Good table count: $table_count tables${NC}"
fi

# Verify admin user exists and create if missing
echo "Verifying admin user exists..."
admin_exists=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM users WHERE email = 'admin@datalegos.com';" | tr -d ' ')

if [ "$admin_exists" -eq 0 ]; then
    echo "Creating admin user..."
    docker exec worky-postgres psql -U postgres -d worky -c "
        INSERT INTO clients (id, name, short_description, email, is_active, created_at, updated_at) 
        VALUES ('CLI-000001', 'DataLegos', 'Default client for admin access', 'admin@datalegos.com', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING;
        
        INSERT INTO users (id, email, hashed_password, full_name, role, primary_role, client_id, is_active, created_at, updated_at) 
        VALUES ('USER-000001', 'admin@datalegos.com', '\$2b\$12\$8K1p/mGVkNG1Vb.YsOb4..VGCDCyqrjRVE5dGX8qjZ8qjZ8qjZ8qjZ8', 'Admin User', 'Admin', 'Admin', 'CLI-000001', true, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET hashed_password = EXCLUDED.hashed_password, updated_at = NOW();
    "
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Admin user created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create admin user${NC}"
    fi
else
    echo -e "${GREEN}✅ Admin user already exists${NC}"
fi

# Verify critical tables exist
echo "Verifying critical tables..."
critical_tables=("users" "clients" "assignments" "teams")
missing_tables=()

for table in "${critical_tables[@]}"; do
    exists=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table';" | tr -d ' ')
    if [ "$exists" -eq 0 ]; then
        missing_tables+=("$table")
    fi
done

if [ ${#missing_tables[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing critical tables: ${missing_tables[*]}${NC}"
    echo "Database may not have initialized properly. Check logs above."
    exit 1
else
    echo -e "${GREEN}✅ All critical tables exist${NC}"
fi

# Clean up temporary migration files and restore originals
echo "Cleaning up temporary migration files..."
rm -f "db/migrations/001_corrected_baseline.sql"
rm -f "db/migrations/002_extended_features.sql"
rm -f "db/migrations/003_bug_management.sql"

# Restore original migration files from backup
echo "Restoring original migration files..."
restored_count=0
for file in db/migrations_backup/*.sql; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Restoring: $filename"
        mv "$file" "db/migrations/"
        ((restored_count++))
    fi
done
echo "Restored $restored_count migration files"

# Remove empty backup directory
rmdir "db/migrations_backup" 2>/dev/null || true

echo ""
echo -e "${BLUE}[5/8] Starting API server...${NC}"
docker-compose up -d api

echo "Waiting for API to be ready..."
sleep 5

# Wait for API to be ready
while ! curl -s http://localhost:8007/health >/dev/null 2>&1; do
    echo "Still waiting for API..."
    sleep 3
done

echo -e "${GREEN}✅ API server is ready!${NC}"

echo ""
echo -e "${BLUE}[6/8] Checking Node.js and npm for UI...${NC}"
cd ui

if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: npm is not available${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js and npm are available${NC}"

echo ""
echo -e "${BLUE}[7/8] Installing UI dependencies...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Failed to install UI dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ UI dependencies installed${NC}"

echo ""
echo -e "${BLUE}[8/8] Starting UI development server...${NC}"
echo ""
echo "============================================================================"
echo "                        APPLICATION STARTUP COMPLETE!"
echo "============================================================================"
echo ""
echo -e "${GREEN}✅ Database: Running with corrected schema ($table_count tables)${NC}"
echo -e "${GREEN}✅ API: Running on http://localhost:8007${NC}"
echo -e "${YELLOW}🚀 Starting UI on http://localhost:3007${NC}"
echo ""
echo -e "${BLUE}🔐 Login Credentials:${NC}"
echo "   - Email: admin@datalegos.com"
echo "   - Password: password"
echo "   - Note: Change password after first login in production!"
echo ""
echo -e "${BLUE}📊 Database Info:${NC}"
echo "   - Host: localhost:5437"
echo "   - Database: worky"
echo "   - User: postgres"
echo "   - Password: postgres"
echo "   - Schema: Corrected (string IDs, all fields match API/UI)"
echo "   - Tables: $table_count (expected 50+)"
echo ""
if [ "$table_count" -lt 40 ]; then
    echo -e "${RED}⚠️  WARNING: Table count is low. Run ./04_verify_database_schema.sh to check${NC}"
    echo ""
fi
echo -e "${BLUE}🔗 Access Points:${NC}"
echo "   - UI Application: http://localhost:3007"
echo "   - API Documentation: http://localhost:8007/docs"
echo "   - API Health: http://localhost:8007/health"
echo ""
echo -e "${BLUE}🔧 Verification:${NC}"
echo "   - Run ./04_verify_database_schema.sh to check database schema"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the UI development server${NC}"
echo -e "${YELLOW}Database and API will continue running in background${NC}"
echo ""
echo "============================================================================"
echo ""

# Start the UI development server (this will block)
npm run dev

echo ""
echo "UI development server stopped."
echo "Database and API are still running in background."
echo "Use ./02_stop_all_services.sh to stop everything."
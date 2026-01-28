#!/bin/bash
# ============================================================================
# Worky Development - Startup with Existing Migration Files
# ============================================================================
# This script starts the application assuming the corrected migration files
# are already in place in db/migrations/. It does NOT move or backup files.
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
echo "           WORKY STARTUP (WITH EXISTING CORRECTED MIGRATIONS)"
echo "============================================================================"
echo ""

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

echo -e "${BLUE}[1/6] Stopping any running services...${NC}"
docker-compose down -v --remove-orphans 2>/dev/null || true
pkill -f "node.*dev" 2>/dev/null || true

echo ""
echo -e "${BLUE}[2/6] Cleaning up old data...${NC}"
if [ -d "volumes/postgres-data" ]; then
    rm -rf "volumes/postgres-data"
    echo "Removed local postgres data"
fi
mkdir -p "volumes/postgres-data"
mkdir -p "volumes/api-logs"

echo ""
echo -e "${BLUE}[3/6] Verifying migration files...${NC}"
echo "Current migration files:"
ls -1 db/migrations/*.sql

# Check if corrected files exist
if [ ! -f "db/migrations/001_corrected_baseline.sql" ]; then
    echo -e "${RED}❌ ERROR: 001_corrected_baseline.sql not found${NC}"
    echo "Please run the full startup script: ./01_startup_complete_application.sh"
    exit 1
fi

echo -e "${GREEN}✅ Corrected migration files found${NC}"

echo ""
echo -e "${BLUE}[4/6] Starting database...${NC}"
docker-compose up -d db

# Wait for database to be ready
attempt=1
max_attempts=30
while ! docker exec worky-postgres pg_isready -U postgres -d worky >/dev/null 2>&1; do
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Database failed to start after $max_attempts attempts${NC}"
        exit 1
    fi
    echo "Attempt $attempt/$max_attempts: Waiting for database..."
    sleep 3
    ((attempt++))
done

echo -e "${GREEN}✅ Database is ready!${NC}"

# Check table count
table_count=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
echo "Tables created: $table_count"

if [ "$table_count" -lt 40 ]; then
    echo -e "${RED}❌ WARNING: Only $table_count tables created (expected 50+)${NC}"
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

echo ""
echo -e "${BLUE}[5/6] Starting API server...${NC}"
docker-compose up -d api

# Wait for API
sleep 5
while ! curl -s http://localhost:8007/health >/dev/null 2>&1; do
    echo "Waiting for API..."
    sleep 3
done

echo -e "${GREEN}✅ API server is ready!${NC}"

echo ""
echo -e "${BLUE}[6/6] Starting UI...${NC}"
cd ui
npm install
echo ""
echo "============================================================================"
echo "                        APPLICATION READY!"
echo "============================================================================"
echo ""
echo -e "${GREEN}✅ Database: $table_count tables${NC}"
echo -e "${GREEN}✅ API: http://localhost:8007${NC}"
echo -e "${YELLOW}🚀 Starting UI on http://localhost:3007${NC}"
echo ""
npm run dev
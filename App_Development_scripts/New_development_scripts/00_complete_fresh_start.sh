#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================================"
echo "                    WORKY COMPLETE FRESH START"
echo "============================================================================"
echo ""
echo "This will:"
echo "- Stop all services and clean everything"
echo "- Rebuild database with corrected schema"
echo "- Create admin user automatically"
echo "- Start all services (DB, API, UI)"
echo "- Verify login works"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo -e "${BLUE}[1/10] Stopping all services and cleaning up...${NC}"

# Stop everything
docker-compose down -v 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
pkill -f "node.*dev" 2>/dev/null || true

# Remove volumes
docker volume rm worky_development_postgres-data 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

# Remove local data
if [ -d "volumes/postgres-data" ]; then
    rm -rf "volumes/postgres-data"
fi
mkdir -p "volumes/postgres-data"
mkdir -p "volumes/api-logs"

docker system prune -f 2>/dev/null || true

echo -e "${GREEN}✅ Cleanup complete${NC}"

echo ""
echo -e "${BLUE}[2/10] Preparing database scripts...${NC}"

# Ensure we're in the right directory
cd /d/WORKY/Worky_Development

# Backup and prepare migration files
mkdir -p "db/migrations_backup"
for file in db/migrations/*.sql; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [[ ! "$filename" =~ ^999_seed_dev_data.sql$ ]]; then
            mv "$file" "db/migrations_backup/" 2>/dev/null || true
        fi
    fi
done

# Copy corrected scripts as migrations
cp "db/initial_scripts/001_corrected_baseline_schema.sql" "db/migrations/001_corrected_baseline.sql"
cp "db/initial_scripts/002_extended_features.sql" "db/migrations/002_extended_features.sql"
cp "db/initial_scripts/003_bug_management_and_comments.sql" "db/migrations/003_bug_management.sql"

echo -e "${GREEN}✅ Database scripts prepared${NC}"

echo ""
echo -e "${BLUE}[3/10] Starting database...${NC}"

docker-compose up -d db

# Wait for database with detailed feedback
attempt=1
max_attempts=30
while ! docker exec worky-postgres pg_isready -U postgres -d worky >/dev/null 2>&1; do
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Database failed to start${NC}"
        docker logs worky-postgres | tail -20
        exit 1
    fi
    echo "Attempt $attempt/$max_attempts: Waiting for database..."
    sleep 3
    ((attempt++))
done

echo -e "${GREEN}✅ Database started${NC}"

echo ""
echo -e "${BLUE}[4/10] Verifying database schema...${NC}"

# Check table count
table_count=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
echo "Tables created: $table_count"

if [ "$table_count" -lt 40 ]; then
    echo -e "${RED}❌ Not enough tables created${NC}"
    docker logs worky-postgres | tail -30
    exit 1
fi

echo -e "${GREEN}✅ Database schema verified ($table_count tables)${NC}"

echo ""
echo -e "${BLUE}[5/10] Verifying admin user...${NC}"

# Check if admin user exists
admin_count=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM users WHERE email = 'admin@datalegos.com';" | tr -d ' ')

if [ "$admin_count" -eq 0 ]; then
    echo -e "${RED}❌ Admin user not found in database${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Admin user verified${NC}"

echo ""
echo -e "${BLUE}[6/10] Cleaning up temporary migration files...${NC}"

# Remove temporary migration files
rm -f "db/migrations/001_corrected_baseline.sql"
rm -f "db/migrations/002_extended_features.sql"
rm -f "db/migrations/003_bug_management.sql"

# Restore original migration files
for file in db/migrations_backup/*.sql; do
    if [ -f "$file" ]; then
        mv "$file" "db/migrations/"
    fi
done
rmdir "db/migrations_backup" 2>/dev/null || true

echo -e "${GREEN}✅ Migration files cleaned up${NC}"

echo ""
echo -e "${BLUE}[7/10] Starting API server...${NC}"

docker-compose up -d api

# Wait for API with retries
sleep 5
api_attempts=1
max_api_attempts=20
while ! curl -s http://localhost:8007/health >/dev/null 2>&1; do
    if [ $api_attempts -eq $max_api_attempts ]; then
        echo -e "${RED}❌ API failed to start${NC}"
        docker logs worky-api | tail -20
        exit 1
    fi
    echo "Attempt $api_attempts/$max_api_attempts: Waiting for API..."
    sleep 3
    ((api_attempts++))
done

echo -e "${GREEN}✅ API server started${NC}"

echo ""
echo -e "${BLUE}[8/10] Testing login functionality...${NC}"

# Test login API
login_response=$(curl -s -X POST http://localhost:8007/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@datalegos.com", "password": "password"}')

if echo "$login_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login API works${NC}"
else
    echo -e "${RED}❌ Login API failed${NC}"
    echo "Response: $login_response"
    echo ""
    echo "API Logs:"
    docker logs worky-api | tail -10
    exit 1
fi

echo ""
echo -e "${BLUE}[9/10] Preparing UI...${NC}"

cd ui

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi

# Install dependencies
npm install >/dev/null 2>&1

echo -e "${GREEN}✅ UI prepared${NC}"

echo ""
echo -e "${BLUE}[10/10] Starting UI server...${NC}"

echo ""
echo "============================================================================"
echo "                        STARTUP COMPLETE!"
echo "============================================================================"
echo ""
echo -e "${GREEN}✅ Database: Running ($table_count tables)${NC}"
echo -e "${GREEN}✅ API: Running on http://localhost:8007${NC}"
echo -e "${GREEN}✅ Login: Verified working${NC}"
echo -e "${YELLOW}🚀 Starting UI on http://localhost:3007${NC}"
echo ""
echo -e "${BLUE}🔐 Login Credentials:${NC}"
echo "   - Email: admin@datalegos.com"
echo "   - Password: password"
echo ""
echo -e "${BLUE}🔗 Access Points:${NC}"
echo "   - UI Application: http://localhost:3007"
echo "   - API Documentation: http://localhost:8007/docs"
echo "   - API Health: http://localhost:8007/health"
echo ""
echo -e "${GREEN}Everything is ready! You can now login to the application.${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the UI development server${NC}"
echo -e "${YELLOW}Database and API will continue running in background${NC}"
echo ""
echo "============================================================================"
echo ""

# Start UI (this will block)
npm run dev
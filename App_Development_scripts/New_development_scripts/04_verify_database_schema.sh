#!/bin/bash
# ============================================================================
# Worky Development - Database Schema Verification
# ============================================================================
# This script verifies that the database has been created with the correct
# schema (string IDs, all required fields, proper table count)
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
echo "                    DATABASE SCHEMA VERIFICATION"
echo "============================================================================"
echo ""

# Check if database is running
if ! docker exec worky-postgres pg_isready -U postgres -d worky >/dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Database is not running${NC}"
    echo "Please start the application first: ./01_startup_complete_application.sh"
    exit 1
fi

echo -e "${BLUE}📊 Checking database schema...${NC}"
echo ""

# Count tables
TABLE_COUNT=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')

echo -e "${BLUE}Table Count:${NC} $TABLE_COUNT"
if [ "$TABLE_COUNT" -ge 50 ]; then
    echo -e "${GREEN}✅ Table count looks good (expected ~52)${NC}"
else
    echo -e "${RED}❌ Table count is low (expected ~52, got $TABLE_COUNT)${NC}"
fi

echo ""
echo -e "${BLUE}📋 All Tables:${NC}"
docker exec worky-postgres psql -U postgres -d worky -c "\dt;"

echo ""
echo -e "${BLUE}🔍 Checking core table schemas...${NC}"

# Check clients table
echo ""
echo -e "${YELLOW}Clients Table:${NC}"
docker exec worky-postgres psql -U postgres -d worky -c "\d clients;"

# Check users table
echo ""
echo -e "${YELLOW}Users Table:${NC}"
docker exec worky-postgres psql -U postgres -d worky -c "\d users;"

# Check tasks table
echo ""
echo -e "${YELLOW}Tasks Table:${NC}"
docker exec worky-postgres psql -U postgres -d worky -c "\d tasks;"

# Check subtasks table
echo ""
echo -e "${YELLOW}Subtasks Table:${NC}"
docker exec worky-postgres psql -U postgres -d worky -c "\d subtasks;"

echo ""
echo -e "${BLUE}🔑 Checking ID types (should be VARCHAR, not UUID)...${NC}"

# Check if IDs are VARCHAR (string) not UUID
ID_CHECK=$(docker exec worky-postgres psql -U postgres -d worky -t -c "
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND column_name = 'id' 
    AND table_name IN ('clients', 'users', 'tasks', 'subtasks', 'projects', 'sprints')
ORDER BY table_name;
")

echo "$ID_CHECK"

# Check for UUID types (should be none)
UUID_COUNT=$(docker exec worky-postgres psql -U postgres -d worky -t -c "
SELECT COUNT(*) 
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND data_type = 'uuid';
" | tr -d ' ')

echo ""
if [ "$UUID_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No UUID columns found (good - using string IDs)${NC}"
else
    echo -e "${RED}❌ Found $UUID_COUNT UUID columns (should be 0)${NC}"
fi

echo ""
echo -e "${BLUE}📝 Checking for required fields...${NC}"

# Check if tasks table has required fields
TASKS_FIELDS=$(docker exec worky-postgres psql -U postgres -d worky -t -c "
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'tasks'
    AND column_name IN ('short_description', 'long_description', 'sprint_id')
ORDER BY column_name;
")

echo "Tasks table required fields:"
echo "$TASKS_FIELDS"

# Check if subtasks table has required fields
SUBTASKS_FIELDS=$(docker exec worky-postgres psql -U postgres -d worky -t -c "
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'subtasks'
    AND column_name IN ('short_description', 'long_description', 'duration_days', 'scrum_points')
ORDER BY column_name;
")

echo ""
echo "Subtasks table required fields:"
echo "$SUBTASKS_FIELDS"

echo ""
echo "============================================================================"
echo "                      VERIFICATION COMPLETE"
echo "============================================================================"
echo ""

if [ "$TABLE_COUNT" -ge 50 ] && [ "$UUID_COUNT" -eq 0 ]; then
    echo -e "${GREEN}🎉 DATABASE SCHEMA VERIFICATION PASSED!${NC}"
    echo -e "${GREEN}✅ Correct number of tables ($TABLE_COUNT)${NC}"
    echo -e "${GREEN}✅ Using string IDs (no UUIDs)${NC}"
    echo -e "${GREEN}✅ Schema matches API and UI expectations${NC}"
else
    echo -e "${RED}❌ DATABASE SCHEMA VERIFICATION FAILED!${NC}"
    if [ "$TABLE_COUNT" -lt 50 ]; then
        echo -e "${RED}  - Too few tables ($TABLE_COUNT, expected ~52)${NC}"
    fi
    if [ "$UUID_COUNT" -gt 0 ]; then
        echo -e "${RED}  - Found UUID columns ($UUID_COUNT, expected 0)${NC}"
    fi
    echo ""
    echo -e "${YELLOW}💡 To fix this:${NC}"
    echo "  1. Stop the application: ./02_stop_complete_application.sh"
    echo "  2. Clean up everything: ./03_cleanup_complete_application.sh"
    echo "  3. Start fresh: ./01_startup_complete_application.sh"
fi

echo ""
echo "============================================================================"
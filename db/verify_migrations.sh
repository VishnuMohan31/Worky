#!/bin/bash

# Verify Database Migrations Script
# This script verifies that all migration files are present and properly ordered
# Usage: ./verify_migrations.sh

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Worky Database Migration Verification ===${NC}\n"

# Count migration files
MIGRATION_COUNT=$(ls -1 db/migrations/*.sql 2>/dev/null | wc -l | tr -d ' ')

if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo -e "${RED}Error: No migration files found in db/migrations/${NC}"
    exit 1
fi

echo -e "${GREEN}Found $MIGRATION_COUNT migration files${NC}\n"

# List all migrations in order
echo -e "${YELLOW}Migration files (in execution order):${NC}"
ls -1 db/migrations/*.sql | sort | nl -w2 -s'. '

echo -e "\n${YELLOW}Checking for duplicate migration numbers...${NC}"
DUPLICATES=$(ls -1 db/migrations/*.sql | sed 's/.*\/\([0-9]*\).*/\1/' | sort | uniq -d)

if [ -n "$DUPLICATES" ]; then
    echo -e "${RED}Warning: Found duplicate migration numbers:${NC}"
    echo "$DUPLICATES"
    echo -e "${YELLOW}This may cause issues with migration order${NC}"
else
    echo -e "${GREEN}✓ No duplicate migration numbers found${NC}"
fi

# Check for required tables in migrations
echo -e "\n${YELLOW}Checking for required table definitions...${NC}"

REQUIRED_TABLES=(
    "users"
    "clients"
    "programs"
    "projects"
    "usecases"
    "user_stories"
    "tasks"
    "subtasks"
    "phases"
    "bugs"
    "chat_messages"
    "chat_audit_logs"
    "reminders"
    "todo_items"
    "organizations"
)

for table in "${REQUIRED_TABLES[@]}"; do
    if grep -rq "CREATE TABLE.*$table" db/migrations/*.sql; then
        echo -e "${GREEN}✓ $table${NC}"
    else
        echo -e "${RED}✗ $table (not found)${NC}"
    fi
done

# Summary
echo -e "\n${BLUE}=== Summary ===${NC}"
echo -e "Total migrations: ${GREEN}$MIGRATION_COUNT${NC}"
echo -e "Migration directory: ${BLUE}db/migrations/${NC}"
echo -e "Docker mount point: ${BLUE}/docker-entrypoint-initdb.d${NC}"

echo -e "\n${YELLOW}Note:${NC} All SQL files in db/migrations/ will be executed automatically"
echo -e "when the PostgreSQL container is first created (via docker-compose.yml)"

echo -e "\n${GREEN}Verification complete!${NC}"

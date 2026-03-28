#!/bin/bash

# Database Initialization Script
# This script initializes or resets the Worky database with all migrations
# Usage: ./init_database.sh [--reset]
# 
# IMPORTANT: For a fresh clone on a new device, always use --reset flag
# to ensure clean database initialization with all migrations.

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database connection details
DB_CONTAINER="worky-postgres"
DB_NAME="worky"
DB_USER="postgres"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}=== Worky Database Initialization ===${NC}\n"

# Check if reset flag is provided
RESET_DB=false
FORCE_RESET=false
if [ "$1" == "--reset" ]; then
    RESET_DB=true
    echo -e "${YELLOW}⚠️  Reset mode enabled - This will destroy all existing data!${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${RED}Aborted${NC}"
        exit 0
    fi
elif [ "$1" == "--force-reset" ]; then
    RESET_DB=true
    FORCE_RESET=true
    echo -e "${YELLOW}⚠️  Force reset mode - destroying all data without confirmation${NC}"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Navigate to project root for docker-compose
cd "$PROJECT_ROOT"

# Reset database if requested
if [ "$RESET_DB" = true ]; then
    echo -e "\n${YELLOW}Stopping and removing database container and volumes...${NC}"
    docker-compose down -v 2>/dev/null || true
    
    # Also remove any orphan volumes
    docker volume rm worky_postgres-data 2>/dev/null || true
    
    echo -e "${GREEN}✓ Database container and volumes removed${NC}"
    echo -e "${YELLOW}Starting fresh database container...${NC}"
    docker-compose up -d db
    
    # Wait for database to be ready
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    sleep 5
    
    # Wait for health check
    for i in {1..60}; do
        if docker exec $DB_CONTAINER pg_isready -U $DB_USER > /dev/null 2>&1; then
            echo -e "\n${GREEN}✓ Database is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    
    # Wait for migrations to complete (PostgreSQL runs them from /docker-entrypoint-initdb.d)
    echo -e "${YELLOW}Waiting for migrations to complete...${NC}"
    sleep 10
    
    # Check if migrations completed by looking for key tables
    for i in {1..30}; do
        TABLE_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | tr -d ' ')
        if [ "$TABLE_COUNT" -gt 20 ]; then
            echo -e "${GREEN}✓ Migrations completed (${TABLE_COUNT} tables created)${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    
    echo -e "${GREEN}✓ Fresh database created with all migrations${NC}\n"
else
    # Check if container is running
    if ! docker ps | grep -q $DB_CONTAINER; then
        echo -e "${YELLOW}Database container is not running. Starting...${NC}"
        docker-compose up -d db
        
        # Wait for database to be ready
        echo -e "${YELLOW}Waiting for database to be ready...${NC}"
        for i in {1..60}; do
            if docker exec $DB_CONTAINER pg_isready -U $DB_USER > /dev/null 2>&1; then
                echo -e "\n${GREEN}✓ Database is ready${NC}"
                break
            fi
            echo -n "."
            sleep 1
        done
        echo ""
    else
        echo -e "${GREEN}✓ Database container is running${NC}"
    fi
fi

# Verify migrations
echo -e "\n${YELLOW}Verifying migration files...${NC}"
MIGRATION_COUNT=$(ls -1 "$SCRIPT_DIR/migrations"/*.sql 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}Found $MIGRATION_COUNT migration files${NC}"

# List all tables in the database
echo -e "\n${YELLOW}Checking database tables...${NC}"
TABLES=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | tr -d ' ')

if [ "$TABLES" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $TABLES tables in database${NC}"
    
    # List key tables
    echo -e "\n${BLUE}Key tables:${NC}"
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT '  ✓ ' || tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'users', 'clients', 'programs', 'projects', 'usecases', 
            'user_stories', 'tasks', 'subtasks', 'phases', 'bugs',
            'teams', 'team_members', 'assignments', 'entity_notes',
            'chat_messages', 'chat_audit_logs', 'reminders',
            'todo_items', 'organizations', 'notifications'
        )
        ORDER BY tablename;
    " 2>/dev/null
else
    echo -e "${RED}✗ No tables found in database${NC}"
    echo -e "${YELLOW}This might indicate migrations haven't run yet${NC}"
    echo -e "${YELLOW}Try running: ./db/init_database.sh --reset${NC}"
fi

# Check for required tables
echo -e "\n${YELLOW}Verifying required tables...${NC}"
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
    "teams"
    "team_members"
    "assignments"
    "entity_notes"
    "todo_items"
    "organizations"
)

MISSING_TABLES=()
for table in "${REQUIRED_TABLES[@]}"; do
    if docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT 1 FROM pg_tables WHERE tablename = '$table';" 2>/dev/null | grep -q 1; then
        echo -e "${GREEN}✓ $table${NC}"
    else
        echo -e "${RED}✗ $table (missing)${NC}"
        MISSING_TABLES+=("$table")
    fi
done

# Check for seed data
echo -e "\n${YELLOW}Checking for seed data...${NC}"
USER_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
if [ "$USER_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $USER_COUNT users (seed data present)${NC}"
else
    echo -e "${YELLOW}⚠ No users found - seed data may not have loaded${NC}"
fi

# Summary
echo -e "\n${BLUE}=== Summary ===${NC}"
echo -e "Database: ${GREEN}$DB_NAME${NC}"
echo -e "Container: ${GREEN}$DB_CONTAINER${NC}"
echo -e "Total tables: ${GREEN}$TABLES${NC}"
echo -e "Migration files: ${GREEN}$MIGRATION_COUNT${NC}"
echo -e "Users: ${GREEN}$USER_COUNT${NC}"

if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
    echo -e "\n${GREEN}✓ All required tables are present${NC}"
    echo -e "${GREEN}✓ Database initialization complete!${NC}"
else
    echo -e "\n${RED}✗ Missing ${#MISSING_TABLES[@]} required tables${NC}"
    echo -e "${YELLOW}Try running: ./db/init_database.sh --reset${NC}"
fi

# Connection info
echo -e "\n${BLUE}Connection Details:${NC}"
echo -e "  Host: ${GREEN}localhost${NC}"
echo -e "  Port: ${GREEN}5437${NC}"
echo -e "  Database: ${GREEN}$DB_NAME${NC}"
echo -e "  User: ${GREEN}$DB_USER${NC}"
echo -e "  Password: ${GREEN}postgres${NC}"

echo -e "\n${BLUE}Useful Commands:${NC}"
echo -e "  View logs:        ${YELLOW}docker-compose logs db${NC}"
echo -e "  Connect to DB:    ${YELLOW}docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME${NC}"
echo -e "  List tables:      ${YELLOW}docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c '\\dt'${NC}"
echo -e "  Reset database:   ${YELLOW}./db/init_database.sh --reset${NC}"

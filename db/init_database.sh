#!/bin/bash

# Database Initialization Script
# This script initializes or resets the Worky database with all migrations
# Usage: ./init_database.sh [--reset]

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

echo -e "${BLUE}=== Worky Database Initialization ===${NC}\n"

# Check if reset flag is provided
RESET_DB=false
if [ "$1" == "--reset" ]; then
    RESET_DB=true
    echo -e "${YELLOW}⚠️  Reset mode enabled - This will destroy all existing data!${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${RED}Aborted${NC}"
        exit 0
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Reset database if requested
if [ "$RESET_DB" = true ]; then
    echo -e "\n${YELLOW}Stopping and removing database container...${NC}"
    docker-compose down -v
    
    echo -e "${GREEN}✓ Database container removed${NC}"
    echo -e "${YELLOW}Starting fresh database container...${NC}"
    docker-compose up -d db
    
    # Wait for database to be ready
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    sleep 5
    
    # Wait for health check
    for i in {1..30}; do
        if docker exec $DB_CONTAINER pg_isready -U $DB_USER > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Database is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    
    echo -e "${GREEN}✓ Fresh database created${NC}"
    echo -e "${BLUE}Migrations will be applied automatically by PostgreSQL${NC}\n"
    
    # Wait a bit more for migrations to complete
    sleep 3
else
    # Check if container is running
    if ! docker ps | grep -q $DB_CONTAINER; then
        echo -e "${YELLOW}Database container is not running. Starting...${NC}"
        docker-compose up -d db
        
        # Wait for database to be ready
        echo -e "${YELLOW}Waiting for database to be ready...${NC}"
        for i in {1..30}; do
            if docker exec $DB_CONTAINER pg_isready -U $DB_USER > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Database is ready${NC}"
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
MIGRATION_COUNT=$(ls -1 db/migrations/*.sql 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}Found $MIGRATION_COUNT migration files${NC}"

# List all tables in the database
echo -e "\n${YELLOW}Checking database tables...${NC}"
TABLES=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" 2>/dev/null | grep -v '^$' | wc -l | tr -d ' ')

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
            'chat_messages', 'chat_audit_logs', 'reminders',
            'todo_items', 'organizations'
        )
        ORDER BY tablename;
    " 2>/dev/null
else
    echo -e "${RED}✗ No tables found in database${NC}"
    echo -e "${YELLOW}This might indicate migrations haven't run yet${NC}"
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
    "chat_messages"
    "chat_audit_logs"
    "reminders"
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

# Summary
echo -e "\n${BLUE}=== Summary ===${NC}"
echo -e "Database: ${GREEN}$DB_NAME${NC}"
echo -e "Container: ${GREEN}$DB_CONTAINER${NC}"
echo -e "Total tables: ${GREEN}$TABLES${NC}"
echo -e "Migration files: ${GREEN}$MIGRATION_COUNT${NC}"

if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
    echo -e "\n${GREEN}✓ All required tables are present${NC}"
    echo -e "${GREEN}✓ Database initialization complete!${NC}"
else
    echo -e "\n${RED}✗ Missing ${#MISSING_TABLES[@]} required tables${NC}"
    echo -e "${YELLOW}You may need to apply migrations manually:${NC}"
    echo -e "  ./db/apply_migrations.sh"
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

#!/bin/bash

# Load Seed Data Script
# This script loads development seed data into the database
# Usage: ./load_seed_data.sh [--force]

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

echo -e "${BLUE}=== Load Seed Data ===${NC}\n"

# Check if force flag is provided
FORCE=false
if [ "$1" == "--force" ]; then
    FORCE=true
    echo -e "${YELLOW}⚠️  Force mode enabled - This will reload seed data even if users exist${NC}"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if container is running
if ! docker ps | grep -q $DB_CONTAINER; then
    echo -e "${RED}Error: Database container is not running${NC}"
    echo -e "${YELLOW}Start it with: docker-compose up -d db${NC}"
    exit 1
fi

# Check if users already exist
USER_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')

if [ "$USER_COUNT" -gt 0 ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}⚠️  Database already contains $USER_COUNT users${NC}"
    echo -e "${YELLOW}Seed data is typically only loaded on fresh installations${NC}"
    echo -e "\nOptions:"
    echo -e "  1. Use ${GREEN}--force${NC} flag to reload seed data anyway"
    echo -e "  2. Reset the database with ${GREEN}./db/init_database.sh --reset${NC}"
    exit 0
fi

# Load seed data (now integrated into migrations as 999_seed_dev_data.sql)
echo -e "${YELLOW}Loading seed data from db/migrations/999_seed_dev_data.sql...${NC}"

if docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < db/migrations/999_seed_dev_data.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Seed data loaded successfully!${NC}"
    
    # Count loaded data
    echo -e "\n${BLUE}Loaded data summary:${NC}"
    
    CLIENTS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM clients;" 2>/dev/null | tr -d ' ')
    echo -e "  Clients: ${GREEN}$CLIENTS${NC}"
    
    USERS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
    echo -e "  Users: ${GREEN}$USERS${NC}"
    
    PROGRAMS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM programs;" 2>/dev/null | tr -d ' ')
    echo -e "  Programs: ${GREEN}$PROGRAMS${NC}"
    
    PROJECTS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM projects;" 2>/dev/null | tr -d ' ')
    echo -e "  Projects: ${GREEN}$PROJECTS${NC}"
    
    USECASES=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM usecases;" 2>/dev/null | tr -d ' ')
    echo -e "  Use Cases: ${GREEN}$USECASES${NC}"
    
    STORIES=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM user_stories;" 2>/dev/null | tr -d ' ')
    echo -e "  User Stories: ${GREEN}$STORIES${NC}"
    
    TASKS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM tasks;" 2>/dev/null | tr -d ' ')
    echo -e "  Tasks: ${GREEN}$TASKS${NC}"
    
    BUGS=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM bugs;" 2>/dev/null | tr -d ' ')
    echo -e "  Bugs: ${GREEN}$BUGS${NC}"
    
    echo -e "\n${BLUE}Test Credentials:${NC}"
    echo -e "  Email: ${GREEN}admin@datalegos.com${NC}"
    echo -e "  Password: ${GREEN}password${NC}"
    
else
    echo -e "${RED}✗ Failed to load seed data${NC}"
    echo -e "${YELLOW}Check the error messages above for details${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Seed data loading complete!${NC}"

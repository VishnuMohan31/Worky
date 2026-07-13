#!/bin/bash

# Apply database migrations to running Worky PostgreSQL container
# Usage: ./apply_migrations.sh [migration_number]

set -e

# Database connection details
DB_CONTAINER="worky-postgres"
DB_NAME="worky"
DB_USER="postgres"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Worky Database Migration Tool ===${NC}\n"

# Check if container is running
if ! docker ps | grep -q $DB_CONTAINER; then
    echo -e "${RED}Error: Database container '$DB_CONTAINER' is not running${NC}"
    echo "Start it with: docker-compose up -d db"
    exit 1
fi

# If migration number is provided, apply only that migration
if [ ! -z "$1" ]; then
    MIGRATION_FILE="migrations/$1"
    if [ ! -f "db/$MIGRATION_FILE" ]; then
        echo -e "${RED}Error: Migration file 'db/$MIGRATION_FILE' not found${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Applying migration: $MIGRATION_FILE${NC}"
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "db/$MIGRATION_FILE"
    echo -e "${GREEN}✓ Migration applied successfully${NC}\n"
    exit 0
fi

# Apply all migrations in order
echo -e "${YELLOW}Applying all new migrations...${NC}\n"

for migration in db/migrations/*.sql; do
    filename=$(basename "$migration")
    echo -e "${YELLOW}Checking migration: $filename${NC}"
    
    # Try to apply migration (will fail if already applied, which is fine)
    if docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$migration" 2>&1 | grep -q "ERROR"; then
        echo -e "${YELLOW}  ⊘ Already applied or error (skipping)${NC}"
    else
        echo -e "${GREEN}  ✓ Applied successfully${NC}"
    fi
done

echo -e "\n${GREEN}=== Migration process complete ===${NC}"
echo -e "\nTo verify, run: docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c '\\dt'"

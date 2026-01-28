#!/bin/bash
# ============================================================================
# Worky Development - Stop Complete Application
# ============================================================================
# This script stops all Worky application services:
# - UI development server
# - API server
# - Database
# ============================================================================

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================================"
echo "                    STOPPING WORKY COMPLETE APPLICATION"
echo "============================================================================"
echo ""

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

echo -e "${BLUE}[1/4] Stopping UI development server...${NC}"
if pgrep -f "node.*dev" >/dev/null 2>&1; then
    echo "Found UI development server processes. Stopping..."
    pkill -f "node.*dev" 2>/dev/null || true
    echo -e "${GREEN}✅ UI development server stopped${NC}"
else
    echo -e "${GREEN}✅ No UI development server running${NC}"
fi

echo ""
echo -e "${BLUE}[2/4] Stopping Docker services (API and Database)...${NC}"
if docker-compose down; then
    echo -e "${GREEN}✅ API and Database stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Some services may not have stopped cleanly${NC}"
fi

echo ""
echo -e "${BLUE}[3/4] Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}[4/4] Final cleanup and restoration...${NC}"
# Restore migration files if they were backed up during startup
if [ -d "db/migrations_backup" ] && [ "$(ls -A db/migrations_backup)" ]; then
    echo "Restoring original migration files..."
    for file in db/migrations_backup/*.sql; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            echo "  Restoring: $filename"
            mv "$file" "db/migrations/"
        fi
    done
    rmdir "db/migrations_backup" 2>/dev/null || true
    echo -e "${GREEN}✅ Migration files restored${NC}"
fi

# Stop any remaining Node.js processes
if pgrep -f "node" >/dev/null 2>&1; then
    pkill -f "node" 2>/dev/null || true
    echo -e "${GREEN}✅ All Node.js processes stopped${NC}"
else
    echo -e "${GREEN}✅ No Node.js processes to stop${NC}"
fi

echo ""
echo "============================================================================"
echo "                      ALL SERVICES STOPPED"
echo "============================================================================"
echo ""
echo -e "${GREEN}✅ UI Development Server: Stopped${NC}"
echo -e "${GREEN}✅ API Server: Stopped${NC}"
echo -e "${GREEN}✅ Database: Stopped${NC}"
echo ""
echo -e "${YELLOW}🚀 To restart the complete application:${NC}"
echo "   ./01_startup_complete_application.sh"
echo ""
echo -e "${YELLOW}🧹 To completely clean up everything:${NC}"
echo "   ./03_cleanup_complete.sh"
echo ""
echo "============================================================================"
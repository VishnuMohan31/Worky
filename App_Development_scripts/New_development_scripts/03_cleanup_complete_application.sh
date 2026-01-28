#!/bin/bash
# ============================================================================
# Worky Development - Complete Application Cleanup
# ============================================================================
# This script performs complete cleanup of the entire Worky application:
# - Stops all services (UI, API, Database)
# - Removes all Docker containers and images
# - Cleans up all data and build artifacts
# - Removes node_modules and temporary files
# 
# WARNING: This will destroy ALL data and require fresh setup!
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
echo "                    WORKY COMPLETE APPLICATION CLEANUP"
echo "============================================================================"
echo ""
echo -e "${RED}⚠️  WARNING: This will completely clean up your entire development environment!${NC}"
echo ""
echo "This will destroy:"
echo "  - All running services (UI, API, Database)"
echo "  - All Docker containers and images"
echo "  - All database data"
echo "  - All build artifacts and node_modules"
echo "  - All logs and temporary files"
echo ""
echo -e "${RED}🔥 ALL DATA AND DEPENDENCIES WILL BE LOST! 🔥${NC}"
echo ""
read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm
if [ "$confirm" != "DELETE" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting complete application cleanup..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

echo ""
echo -e "${BLUE}[1/10] Stopping UI development server...${NC}"
if pgrep -f "node.*dev" >/dev/null 2>&1; then
    pkill -f "node.*dev" 2>/dev/null || true
    echo -e "${GREEN}✅ UI development server stopped${NC}"
else
    echo -e "${GREEN}✅ No UI development server running${NC}"
fi

echo ""
echo -e "${BLUE}[2/10] Stopping Docker services...${NC}"
docker-compose down -v --remove-orphans 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
echo -e "${GREEN}✅ All Docker services stopped${NC}"

echo ""
echo -e "${BLUE}[3/10] Removing Docker containers...${NC}"
docker rm $(docker ps -aq) 2>/dev/null || true
echo -e "${GREEN}✅ Docker containers removed${NC}"

echo ""
echo -e "${BLUE}[4/10] Removing Docker images...${NC}"
docker rmi $(docker images -q) -f 2>/dev/null || true
echo -e "${GREEN}✅ Docker images removed${NC}"

echo ""
echo -e "${BLUE}[5/10] Cleaning Docker system...${NC}"
docker system prune -a --volumes -f
echo -e "${GREEN}✅ Docker system cleaned${NC}"

echo ""
echo -e "${BLUE}[6/10] Removing database data and logs...${NC}"
if [ -d "volumes" ]; then
    rm -rf "volumes"
    echo -e "${GREEN}✅ Database data and API logs removed${NC}"
else
    echo -e "${GREEN}✅ No volumes to remove${NC}"
fi

echo ""
echo -e "${BLUE}[7/10] Cleaning UI dependencies and build files...${NC}"
cd ui
if [ -d "node_modules" ]; then
    rm -rf "node_modules"
    echo -e "${GREEN}✅ node_modules removed${NC}"
else
    echo -e "${GREEN}✅ No node_modules to remove${NC}"
fi

if [ -d "dist" ]; then
    rm -rf "dist"
    echo -e "${GREEN}✅ dist folder removed${NC}"
fi

if [ -d ".next" ]; then
    rm -rf ".next"
    echo -e "${GREEN}✅ .next folder removed${NC}"
fi

if [ -d "build" ]; then
    rm -rf "build"
    echo -e "${GREEN}✅ build folder removed${NC}"
fi

if [ -f "package-lock.json" ]; then
    rm -f "package-lock.json"
    echo -e "${GREEN}✅ package-lock.json removed${NC}"
fi

cd ..

echo ""
echo -e "${BLUE}[8/10] Restoring migration files and cleaning logs...${NC}"
# Restore migration files if they were backed up
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

if [ -d "logs" ]; then
    rm -rf "logs"
    echo -e "${GREEN}✅ Logs directory removed${NC}"
fi

if ls *.log 1> /dev/null 2>&1; then
    rm -f *.log
    echo -e "${GREEN}✅ Log files removed${NC}"
fi

if [ -d ".tmp" ]; then
    rm -rf ".tmp"
    echo -e "${GREEN}✅ Temporary files removed${NC}"
fi

echo ""
echo -e "${BLUE}[9/10] Stopping all remaining processes...${NC}"
if pgrep -f "node" >/dev/null 2>&1; then
    pkill -f "node" 2>/dev/null || true
    echo -e "${GREEN}✅ All Node.js processes stopped${NC}"
else
    echo -e "${GREEN}✅ No Node.js processes to stop${NC}"
fi

echo ""
echo -e "${BLUE}[10/10] Final verification...${NC}"
echo "Docker containers: $(docker ps -aq | wc -l)"
echo "Docker images: $(docker images -q | wc -l)"
echo "Node.js processes: $(pgrep -f "node" | wc -l)"

echo ""
echo "============================================================================"
echo "                      COMPLETE CLEANUP FINISHED!"
echo "============================================================================"
echo ""
echo -e "${GREEN}🧹 Everything has been completely cleaned:${NC}"
echo -e "${GREEN}  ✅ UI development server stopped${NC}"
echo -e "${GREEN}  ✅ API server stopped${NC}"
echo -e "${GREEN}  ✅ Database stopped${NC}"
echo -e "${GREEN}  ✅ All Docker containers and images removed${NC}"
echo -e "${GREEN}  ✅ All database data deleted${NC}"
echo -e "${GREEN}  ✅ All UI dependencies removed${NC}"
echo -e "${GREEN}  ✅ All build artifacts removed${NC}"
echo -e "${GREEN}  ✅ All logs and temporary files removed${NC}"
echo -e "${GREEN}  ✅ All processes stopped${NC}"
echo ""
echo -e "${YELLOW}🚀 To start fresh:${NC}"
echo "  ./01_startup_complete_application.sh"
echo ""
echo -e "${BLUE}💡 The startup script will:${NC}"
echo "  - Use corrected database schema (string IDs, all fields)"
echo "  - Install fresh UI dependencies"
echo "  - Start complete application stack"
echo ""
echo "============================================================================"
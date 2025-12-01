#!/bin/bash

# Worky - Stop All Services
# This script stops the Database, API, and UI services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Worky - Stopping All Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to kill processes on a port
kill_port() {
    local port=$1
    local name=$2
    
    echo -e "${YELLOW}Stopping $name (port $port)...${NC}"
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            echo -e "${RED}✗ Failed to stop $name${NC}"
        else
            echo -e "${GREEN}✓ $name stopped${NC}"
        fi
    else
        echo -e "${YELLOW}$name is not running${NC}"
    fi
}

# Stop UI (port 3007)
kill_port 3007 "UI"

# Stop API (port 8007)
kill_port 8007 "API"

# Stop Database (port 5437)
kill_port 5437 "Database"

# Also kill any remaining node/uvicorn/postgres processes
echo ""
echo -e "${YELLOW}Cleaning up remaining processes...${NC}"

# Kill any remaining uvicorn processes
pkill -f "uvicorn app.main:app" 2>/dev/null && echo -e "${GREEN}✓ Stopped uvicorn processes${NC}"

# Kill any remaining vite processes
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}✓ Stopped vite processes${NC}"

# Kill any remaining postgres processes on our port
pkill -f "postgres.*5437" 2>/dev/null && echo -e "${GREEN}✓ Stopped postgres processes${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Services Stopped${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

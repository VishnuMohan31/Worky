#!/bin/bash

# Worky - Start All Services
# This script starts the Database, API, and UI services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log directory
LOG_DIR="volumes/logs"
mkdir -p "$LOG_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Worky - Starting All Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $name to be ready...${NC}"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}✗ $name failed to start${NC}"
    return 1
}

# 1. Start Database
echo -e "${BLUE}[1/3] Starting PostgreSQL Database...${NC}"
if check_port 5437; then
    echo -e "${YELLOW}Database already running on port 5437${NC}"
else
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}✗ Docker is not running!${NC}"
        echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
        echo -e "${YELLOW}Or start the database manually:${NC}"
        echo -e "  cd App_Development_scripts && ./start_db.sh"
        exit 1
    fi
    
    (cd App_Development_scripts && ./start_db.sh > "../$LOG_DIR/db_startup.log" 2>&1) &
    sleep 5
    if check_port 5437; then
        echo -e "${GREEN}✓ Database started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start database${NC}"
        echo -e "${YELLOW}Check logs: cat $LOG_DIR/db_startup.log${NC}"
        exit 1
    fi
fi
echo ""

# 2. Start API
echo -e "${BLUE}[2/3] Starting FastAPI Backend...${NC}"
if check_port 8007; then
    echo -e "${YELLOW}API already running on port 8007${NC}"
else
    cd api
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8007 > "../$LOG_DIR/api.log" 2>&1 &
    API_PID=$!
    cd ..
    
    if wait_for_service "API" "http://localhost:8007/health"; then
        echo -e "${GREEN}✓ API started successfully (PID: $API_PID)${NC}"
    else
        echo -e "${RED}✗ Failed to start API${NC}"
        exit 1
    fi
fi
echo ""

# 3. Start UI
echo -e "${BLUE}[3/3] Starting React UI...${NC}"
if check_port 3007; then
    echo -e "${YELLOW}UI already running on port 3007${NC}"
else
    cd ui
    nohup npm run dev > "../$LOG_DIR/ui.log" 2>&1 &
    UI_PID=$!
    cd ..
    
    sleep 5  # Give Vite time to start
    if check_port 3007; then
        echo -e "${GREEN}✓ UI started successfully (PID: $UI_PID)${NC}"
    else
        echo -e "${RED}✗ Failed to start UI${NC}"
        exit 1
    fi
fi
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Services Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  • Database:  ${GREEN}postgresql://localhost:5437/worky${NC}"
echo -e "  • API:       ${GREEN}http://localhost:8007${NC}"
echo -e "  • API Docs:  ${GREEN}http://localhost:8007/docs${NC}"
echo -e "  • UI:        ${GREEN}http://localhost:3007${NC}"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  • Database:  ${YELLOW}$LOG_DIR/db_startup.log${NC}"
echo -e "  • API:       ${YELLOW}$LOG_DIR/api.log${NC}"
echo -e "  • UI:        ${YELLOW}$LOG_DIR/ui.log${NC}"
echo ""
echo -e "${BLUE}Login Credentials:${NC}"
echo -e "  • Email:     ${GREEN}admin@datalegos.com${NC}"
echo -e "  • Password:  ${GREEN}password${NC}"
echo ""
echo -e "${YELLOW}To stop all services, run: ./stop_all_services.sh${NC}"
echo -e "${YELLOW}To view logs: tail -f $LOG_DIR/api.log${NC}"
echo ""

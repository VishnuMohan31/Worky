#!/bin/bash
echo "🚀 Starting Worky API..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Stop any existing API processes first
echo "Checking for existing API processes..."
pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
lsof -ti:8007 | xargs kill -9 2>/dev/null || true

cd "$PROJECT_ROOT/api"

# Check for .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Start API in background
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8007 > "$PROJECT_ROOT/logs/api.log" 2>&1 &
API_PID=$!

# Save PID to file
echo $API_PID > "$PROJECT_ROOT/logs/api.pid"

sleep 2

# Check if process is running
if ps -p $API_PID > /dev/null; then
    echo "✓ API started (PID: $API_PID)"
else
    echo "✗ API failed to start. Check logs/api.log"
    exit 1
fi

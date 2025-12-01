#!/bin/bash
echo "🛑 Stopping Worky API..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/logs/api.pid"

# Try to kill using PID file first
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill -9 $PID 2>/dev/null
        echo "✓ Killed API process (PID: $PID)"
    fi
    rm -f "$PID_FILE"
fi

# Kill all uvicorn processes (parent and children) as backup
pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true

# Also kill any processes on port 8007 as final backup
lsof -ti:8007 | xargs kill -9 2>/dev/null || true

sleep 1
echo "✅ API stopped"

#!/bin/bash
echo "🎨 Starting Worky UI..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Stop any existing UI processes first
echo "Checking for existing UI processes..."
pkill -9 -f "vite.*worky" 2>/dev/null || true
lsof -ti:3007 | xargs kill -9 2>/dev/null || true

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

cd "$PROJECT_ROOT/ui"

# Start UI in background
nohup npm run dev > "$PROJECT_ROOT/logs/ui.log" 2>&1 &
UI_PID=$!

# Save PID to file
echo $UI_PID > "$PROJECT_ROOT/logs/ui.pid"

sleep 3

# Check if process is running
if ps -p $UI_PID > /dev/null; then
    echo "✓ UI started (PID: $UI_PID)"
else
    echo "✗ UI failed to start. Check logs/ui.log"
    exit 1
fi

#!/bin/bash
# Stop UI Only (Bash)
# Usage: ./stop_ui.sh

echo "🛑 Stopping UI..."

# Find and kill process on port 3007
UI_PID=$(lsof -ti:3007 2>/dev/null)
if [ -n "$UI_PID" ]; then
    kill -9 $UI_PID 2>/dev/null
    echo "✅ UI stopped (killed PID: $UI_PID)"
else
    # Also try to find npm dev processes
    pkill -f "vite" 2>/dev/null
    echo "✅ UI stopped"
fi

#!/bin/bash
# Start UI Only (Bash)
# Usage: ./start_ui.sh

echo "🎨 Starting UI..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/ui"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Start UI
echo "🚀 Starting Vite dev server..."
nohup npm run dev > "$PROJECT_ROOT/logs/ui.log" 2>&1 &
UI_PID=$!

sleep 3

# Check if UI started
if curl -s http://localhost:3007 > /dev/null 2>&1; then
    echo "✅ UI is ready on http://localhost:3007 (PID: $UI_PID)"
else
    echo "✅ UI started (PID: $UI_PID)"
    echo "   May take a few seconds to be ready"
fi

echo ""
echo "📝 Logs: tail -f $PROJECT_ROOT/logs/ui.log"

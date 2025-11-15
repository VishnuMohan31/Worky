#!/bin/bash
echo "🚀 Starting Worky UI + API..."
SCRIPT_DIR="$(dirname "$0")"

# Start API in background
echo "Starting API..."
cd "$SCRIPT_DIR/../api"
if [ ! -f .env ]; then
    cp .env.example .env
fi
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8007 > ../logs/api.log 2>&1 &
API_PID=$!
echo "✓ API started (PID: $API_PID)"

sleep 3

# Start UI in background
echo "Starting UI..."
cd "$SCRIPT_DIR/../ui"
nohup npm run dev > ../logs/ui.log 2>&1 &
UI_PID=$!
echo "✓ UI started (PID: $UI_PID)"

echo ""
echo "✅ UI + API started!"
echo "   UI:  http://localhost:3007"
echo "   API: http://localhost:8007"
echo ""
echo "📝 Logs:"
echo "   API: tail -f logs/api.log"
echo "   UI:  tail -f logs/ui.log"

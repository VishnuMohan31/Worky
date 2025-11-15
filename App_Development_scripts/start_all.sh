#!/bin/bash
echo "🚀 Starting All Worky Services..."
SCRIPT_DIR="$(dirname "$0")"

# Start Database
echo ""
echo "1️⃣ Starting Database..."
"$SCRIPT_DIR/start_db.sh"
if [ $? -ne 0 ]; then
    echo "❌ Database failed to start"
    exit 1
fi

# Start API in background
echo ""
echo "2️⃣ Starting API..."
cd "$SCRIPT_DIR/../api"
if [ ! -f .env ]; then
    cp .env.example .env
fi
mkdir -p ../logs
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8007 > ../logs/api.log 2>&1 &
API_PID=$!
echo "✓ API started (PID: $API_PID)"

sleep 3

# Start UI in background
echo ""
echo "3️⃣ Starting UI..."
cd "$SCRIPT_DIR/../ui"
nohup npm run dev > ../logs/ui.log 2>&1 &
UI_PID=$!
echo "✓ UI started (PID: $UI_PID)"

echo ""
echo "=" * 60
echo "✅ All Worky Services Started!"
echo "=" * 60
echo ""
echo "📊 Services:"
echo "   Database: localhost:5437 (Docker)"
echo "   API:      http://localhost:8007"
echo "   UI:       http://localhost:3007"
echo ""
echo "🔐 Login:"
echo "   Email:    admin@datalegos.com"
echo "   Password: password"
echo ""
echo "📝 Logs:"
echo "   API: tail -f logs/api.log"
echo "   UI:  tail -f logs/ui.log"
echo "   DB:  docker-compose logs -f db"
echo ""
echo "🛑 Stop:"
echo "   $SCRIPT_DIR/stop_all.sh"

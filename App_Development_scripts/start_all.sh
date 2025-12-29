#!/bin/bash
# Start All Worky Services (Bash)
# Usage: ./start_all.sh

echo "🚀 Starting All Worky Services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Start Database and API via Docker
echo ""
echo "1️⃣ Starting Database and API (Docker)..."
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Docker services failed to start"
    exit 1
fi

echo "✅ Database and API started"

# Wait for services to be healthy
echo ""
echo "2️⃣ Waiting for services to be healthy..."
sleep 10

# Check database
if docker exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "⚠️  Database may still be starting"
fi

# Check API
if curl -s http://localhost:8007/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "⚠️  API may still be starting"
fi

# Start UI
echo ""
echo "3️⃣ Starting UI..."
cd "$PROJECT_ROOT/ui"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing UI dependencies..."
    npm install
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Start UI in background
nohup npm run dev > "$PROJECT_ROOT/logs/ui.log" 2>&1 &
UI_PID=$!
echo "✅ UI started (PID: $UI_PID)"

# Return to project root
cd "$PROJECT_ROOT"

echo ""
echo "============================================"
echo "✅ All Worky Services Started!"
echo "============================================"
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
echo "   API: docker logs worky-api -f"
echo "   DB:  docker logs worky-postgres -f"
echo "   UI:  tail -f logs/ui.log"
echo ""
echo "🛑 Stop:"
echo "   $SCRIPT_DIR/stop_all.sh"

#!/bin/bash
# Stop All Worky Services (Bash)
# Usage: ./stop_all.sh

echo "🛑 Stopping All Worky Services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Stop UI (kill any npm/node processes for Vite on port 3007)
echo ""
echo "1️⃣ Stopping UI..."
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

# Set up Docker commands (use Windows Docker if in WSL)
if [ -f "/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe" ]; then
    DOCKER_COMPOSE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Stop Docker services
echo ""
echo "2️⃣ Stopping Docker services (API and Database)..."
"$DOCKER_COMPOSE" down

if [ $? -eq 0 ]; then
    echo "✅ Docker services stopped"
else
    echo "⚠️  Some services may not have stopped cleanly"
fi

echo ""
echo "============================================"
echo "✅ All Worky Services Stopped!"
echo "============================================"
echo ""
echo "To start again:"
echo "   $SCRIPT_DIR/start_all.sh"

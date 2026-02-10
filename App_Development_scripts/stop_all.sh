#!/bin/bash
# Stop All Worky Services (Bash)
# Usage: ./stop_all.sh

echo "🛑 Stopping All Worky Services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Set up Docker commands (use Windows Docker if in WSL)
if [ -f "/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe" ]; then
    DOCKER_COMPOSE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Stop all Docker services (DB, API, UI)
echo "🛑 Stopping all Docker services..."
"$DOCKER_COMPOSE" down

if [ $? -eq 0 ]; then
    echo "✅ All Docker services stopped"
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

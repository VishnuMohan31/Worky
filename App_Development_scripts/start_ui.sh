#!/bin/bash
# Start UI Only (Bash)
# Usage: ./start_ui.sh

echo "🎨 Starting UI via Docker..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Set up Docker commands (use Windows Docker if in WSL)
if [ -f "/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe" ]; then
    DOCKER_COMPOSE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Start UI via Docker
"$DOCKER_COMPOSE" up -d ui

if [ $? -ne 0 ]; then
    echo "❌ UI failed to start"
    exit 1
fi

# Wait for UI to be healthy
echo "⏳ Waiting for UI to be healthy..."
sleep 5

for i in {1..30}; do
    if curl -s http://localhost:3007 > /dev/null 2>&1; then
        echo ""
        echo "✅ UI is ready on http://localhost:3007"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "⚠️  UI may still be starting. Check: docker logs worky-ui"

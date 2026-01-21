#!/bin/bash
# Start Production Services
# Usage: ./App_Development_scripts/start_production.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found"
    echo "   Please create it from env.production.template"
    exit 1
fi

# Set up Docker commands
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo "🚀 Starting Production Services..."
$DOCKER_COMPOSE -f docker-compose.prod.yml --env-file .env.production up -d

echo ""
echo "✅ Production services started"
echo ""
echo "📊 Services Status:"
docker ps --filter "name=worky" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

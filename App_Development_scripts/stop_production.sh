#!/bin/bash
# Stop Production Services
# Usage: ./App_Development_scripts/stop_production.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env.production exists (optional for stop)
ENV_FILE=""
if [ -f ".env.production" ]; then
    ENV_FILE="--env-file .env.production"
fi

# Set up Docker commands
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo "🛑 Stopping Production Services..."
$DOCKER_COMPOSE -f docker-compose.prod.yml $ENV_FILE down

echo ""
echo "✅ Production services stopped"

#!/bin/bash
# Stop API Only (Bash)
# Usage: ./stop_api.sh

echo "🛑 Stopping API..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

docker-compose stop api

echo "✅ API stopped"

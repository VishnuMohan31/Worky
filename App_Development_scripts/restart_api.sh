#!/bin/bash
# Restart API Only (Bash)
# Usage: ./restart_api.sh

echo "🔄 Restarting API..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Rebuild and restart API
docker-compose up -d --build api

echo "✅ API restarted"
echo "📚 API Docs: http://localhost:8007/docs"

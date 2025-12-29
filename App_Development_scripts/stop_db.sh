#!/bin/bash
# Stop Database Only (Bash)
# Usage: ./stop_db.sh

echo "🛑 Stopping Database..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

docker-compose stop db

echo "✅ Database stopped"
echo "   Note: API may fail without database connection"

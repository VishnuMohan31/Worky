#!/bin/bash
# Restart Database Only (Bash)
# Usage: ./restart_db.sh

echo "🔄 Restarting Database..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

docker-compose restart db

# Wait for database to be healthy
echo "⏳ Waiting for database to be healthy..."
for i in {1..30}; do
    if docker exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo ""
        echo "✅ Database restarted and healthy"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "⚠️  Database may still be restarting"

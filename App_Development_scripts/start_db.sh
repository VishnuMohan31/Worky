#!/bin/bash
# Start Database Only (Bash)
# Usage: ./start_db.sh

echo "🗄️ Starting Database..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Start database via Docker
docker-compose up -d db

if [ $? -ne 0 ]; then
    echo "❌ Database failed to start"
    exit 1
fi

# Wait for database to be healthy
echo "⏳ Waiting for database to be healthy..."
for i in {1..60}; do
    if docker exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo ""
        echo "✅ Database is ready on port 5437"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "⚠️  Database may still be starting. Check: docker logs worky-postgres"

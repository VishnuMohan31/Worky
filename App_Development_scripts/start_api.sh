#!/bin/bash
# Start API Only (Bash)
# Usage: ./start_api.sh

echo "🚀 Starting API..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Start API via Docker (depends on database)
docker-compose up -d api

if [ $? -ne 0 ]; then
    echo "❌ API failed to start"
    exit 1
fi

# Wait for API to be healthy
echo "⏳ Waiting for API to be healthy..."
sleep 5

for i in {1..30}; do
    if curl -s http://localhost:8007/health > /dev/null 2>&1; then
        echo ""
        echo "✅ API is ready on http://localhost:8007"
        echo "📚 API Docs: http://localhost:8007/docs"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "⚠️  API may still be starting. Check: docker logs worky-api"

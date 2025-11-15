#!/bin/bash
echo "🐳 Starting Worky Database (Docker)..."
cd "$(dirname "$0")/.."
docker-compose up -d db
sleep 3
docker-compose exec -T db pg_isready -U postgres
if [ $? -eq 0 ]; then
    echo "✅ Database is ready on port 5437"
else
    echo "❌ Database failed to start"
    exit 1
fi

#!/bin/bash
echo "🐳 Starting Worky Database (Docker)..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Stop any existing database containers first
echo "Checking for existing database containers..."
docker-compose down db 2>/dev/null || true

# Start database
docker-compose up -d db
sleep 3

# Wait for database to be ready
docker-compose exec -T db pg_isready -U postgres
if [ $? -eq 0 ]; then
    echo "✅ Database is ready on port 5437"
else
    echo "❌ Database failed to start"
    exit 1
fi

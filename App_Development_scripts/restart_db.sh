#!/bin/bash
echo "🔄 Restarting Worky Database..."
cd "$(dirname "$0")/.."
docker-compose restart db
sleep 3
docker-compose exec -T db pg_isready -U postgres
if [ $? -eq 0 ]; then
    echo "✅ Database restarted successfully"
else
    echo "❌ Database restart failed"
    exit 1
fi

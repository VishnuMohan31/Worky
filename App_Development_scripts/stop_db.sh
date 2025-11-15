#!/bin/bash
echo "🛑 Stopping Worky Database..."
cd "$(dirname "$0")/.."
docker-compose down
echo "✅ Database stopped"

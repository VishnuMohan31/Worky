#!/bin/bash
echo "🚀 Starting Worky API..."
cd "$(dirname "$0")/../api"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8007

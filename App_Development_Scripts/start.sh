#!/bin/bash
# Start the complete Worky application
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Starting Worky..."
docker compose up -d --build

echo ""
echo "Services started:"
docker compose ps
echo ""
echo "UI:  http://localhost:3007"
echo "API: http://localhost:8007"
echo "Docs: http://localhost:8007/docs"

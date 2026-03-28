#!/bin/bash
# Restart the Worky application
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Restarting Worky..."
docker compose down
docker compose up -d --build

echo ""
echo "Services restarted:"
docker compose ps

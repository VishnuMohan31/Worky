#!/bin/bash
# Stop the Worky application (data is preserved in Worky_Shared_Data)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Stopping Worky..."
docker compose down

echo ""
echo "All services stopped. Data is preserved in Worky_Shared_Data/."

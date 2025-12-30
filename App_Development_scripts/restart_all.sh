#!/bin/bash
# Restart All Worky Services (Bash)
# Usage: ./restart_all.sh

echo "🔄 Restarting All Worky Services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop all services
"$SCRIPT_DIR/stop_all.sh"

echo ""
sleep 2

# Start all services
"$SCRIPT_DIR/start_all.sh"

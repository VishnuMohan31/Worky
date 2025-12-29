#!/bin/bash
# Restart UI Only (Bash)
# Usage: ./restart_ui.sh

echo "🔄 Restarting UI..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop UI
"$SCRIPT_DIR/stop_ui.sh"

sleep 1

# Start UI
"$SCRIPT_DIR/start_ui.sh"

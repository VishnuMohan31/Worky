#!/bin/bash
echo "🔄 Restarting All Worky Services..."
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/stop_all.sh"
sleep 3
"$SCRIPT_DIR/start_all.sh"

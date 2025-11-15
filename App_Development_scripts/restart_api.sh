#!/bin/bash
echo "🔄 Restarting Worky API..."
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/stop_api.sh"
sleep 2
"$SCRIPT_DIR/start_api.sh"

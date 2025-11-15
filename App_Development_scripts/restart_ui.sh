#!/bin/bash
echo "🔄 Restarting Worky UI..."
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/stop_ui.sh"
sleep 2
"$SCRIPT_DIR/start_ui.sh"

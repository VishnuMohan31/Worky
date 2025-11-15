#!/bin/bash
echo "🔄 Restarting Worky UI + API..."
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/stop_ui_api.sh"
sleep 2
"$SCRIPT_DIR/start_ui_api.sh"

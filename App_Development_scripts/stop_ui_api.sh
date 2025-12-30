#!/bin/bash
echo "🛑 Stopping Worky UI + API..."
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/stop_ui.sh"
"$SCRIPT_DIR/stop_api.sh"
echo "✅ UI + API stopped"

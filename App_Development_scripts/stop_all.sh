#!/bin/bash
echo "🛑 Stopping All Worky Services..."
SCRIPT_DIR="$(dirname "$0")"

echo "Stopping UI..."
"$SCRIPT_DIR/stop_ui.sh"

echo "Stopping API..."
"$SCRIPT_DIR/stop_api.sh"

echo "Stopping Database..."
"$SCRIPT_DIR/stop_db.sh"

echo ""
echo "✅ All services stopped!"

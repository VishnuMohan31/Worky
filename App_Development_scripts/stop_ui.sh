#!/bin/bash
echo "🛑 Stopping Worky UI..."
pkill -f "vite" || echo "UI was not running"
echo "✅ UI stopped"

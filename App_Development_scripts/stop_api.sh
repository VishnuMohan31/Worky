#!/bin/bash
echo "🛑 Stopping Worky API..."
pkill -f "uvicorn app.main:app" || echo "API was not running"
echo "✅ API stopped"

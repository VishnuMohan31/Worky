#!/bin/bash

# Excel Loader Service Startup Script
# This script starts the FastAPI Excel Loader service

set -e

# Configuration
PORT=${EXCEL_LOADER_PORT:-8001}
HOST=${EXCEL_LOADER_HOST:-0.0.0.0}
WORKERS=${EXCEL_LOADER_WORKERS:-1}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOADER_DIR="$SCRIPT_DIR/excel_loader"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=========================================="
echo "Starting Excel Loader Service"
echo "=========================================="
echo "Directory: $LOADER_DIR"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Warning: Virtual environment not found at $VENV_DIR"
    echo "To create one, run: python -m venv $VENV_DIR"
    echo "Then install dependencies: $VENV_DIR/bin/pip install -r $LOADER_DIR/requirements.txt"
    echo "Continuing with system Python..."
fi

# Check if .env file exists
if [ ! -f "$LOADER_DIR/.env" ]; then
    echo "Warning: .env file not found in $LOADER_DIR"
    echo "Using environment variables or defaults"
fi

# Check if requirements are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Error: Required dependencies not installed"
    echo "Please run: pip install -r $LOADER_DIR/requirements.txt"
    exit 1
fi

# Start the service
echo "Starting uvicorn server..."
cd "$LOADER_DIR"
python -m uvicorn excel_loader_app:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info \
    --reload

echo "Excel Loader Service stopped"

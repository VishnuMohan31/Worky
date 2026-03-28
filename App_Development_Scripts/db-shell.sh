#!/bin/bash
# Open an interactive PostgreSQL shell inside the running DB container
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load env vars
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-worky}"

echo "Connecting to database '$DB_NAME' as '$DB_USER'..."
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME"

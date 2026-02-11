#!/bin/bash
# Script to fix postgres password in existing database volume
# This updates the password to match docker-compose.yml without losing data

echo "Fixing postgres password in existing database..."

# Change the postgres user password to match docker-compose.yml
docker exec -it worky-postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"

if [ $? -eq 0 ]; then
    echo "✓ Password updated successfully"
    echo "Restarting API container to establish new connections..."
    docker restart worky-api
    echo "✓ Done! Try logging in now."
else
    echo "✗ Failed to update password"
    exit 1
fi

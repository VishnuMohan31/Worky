#!/bin/bash

# Script to fix PostgreSQL password authentication issue
# This script resets the postgres user password to match the API configuration
# while preserving all existing data

set -e

echo "========================================="
echo "Fixing PostgreSQL Password Authentication"
echo "========================================="
echo ""

# Container name
DB_CONTAINER="worky-postgres"
NEW_PASSWORD="postgres"

# Check if container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo "Error: Container $DB_CONTAINER is not running!"
    echo "Please start the container first:"
    echo "  docker start $DB_CONTAINER"
    exit 1
fi

echo "Container $DB_CONTAINER is running."
echo ""

# Method 1: Try to connect and reset password using psql
echo "Attempting to reset password for postgres user..."
echo ""

# Try to connect without password first (in case trust authentication is enabled)
# If that fails, we'll try with the expected password
if docker exec -it "$DB_CONTAINER" psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';" 2>/dev/null; then
    echo "✓ Password reset successful using trust authentication"
elif docker exec -e PGPASSWORD=postgres "$DB_CONTAINER" psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';" 2>/dev/null; then
    echo "✓ Password reset successful using existing password"
else
    echo "Warning: Could not reset password using standard methods."
    echo ""
    echo "Trying alternative method: Using docker exec to modify pg_hba.conf temporarily..."
    echo ""
    
    # Alternative: Temporarily modify pg_hba.conf to allow trust authentication
    # This is a more advanced method that requires stopping the container
    echo "To fix this, you may need to:"
    echo "1. Stop the container: docker stop $DB_CONTAINER"
    echo "2. Start it with trust authentication temporarily"
    echo "3. Reset the password"
    echo "4. Restore normal authentication"
    echo ""
    echo "Or, if you know the current password, you can run manually:"
    echo "  docker exec -e PGPASSWORD=<current_password> $DB_CONTAINER psql -U postgres -d postgres -c \"ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';\""
    exit 1
fi

echo ""
echo "Verifying password change..."
if docker exec -e PGPASSWORD="$NEW_PASSWORD" "$DB_CONTAINER" psql -U postgres -d worky -c "SELECT version();" > /dev/null 2>&1; then
    echo "✓ Password verification successful!"
    echo ""
    echo "========================================="
    echo "Password fix completed successfully!"
    echo "========================================="
    echo ""
    echo "The database password has been reset to: $NEW_PASSWORD"
    echo "This matches the API configuration in docker-compose.yml"
    echo ""
    echo "The API should now be able to connect. You may need to restart the API container:"
    echo "  docker restart worky-api"
else
    echo "✗ Password verification failed. Please check the error above."
    exit 1
fi

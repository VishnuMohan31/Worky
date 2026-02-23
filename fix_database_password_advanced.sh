#!/bin/bash

# Advanced script to fix PostgreSQL password when standard methods fail
# This script temporarily enables trust authentication to reset the password

set -e

echo "========================================="
echo "Advanced PostgreSQL Password Fix"
echo "========================================="
echo ""
echo "This script will:"
echo "1. Stop the PostgreSQL container"
echo "2. Temporarily enable trust authentication"
echo "3. Start the container and reset the password"
echo "4. Restore password authentication"
echo "5. Restart the container normally"
echo ""

read -p "Do you want to continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

DB_CONTAINER="worky-postgres"
NEW_PASSWORD="postgres"

# Step 1: Stop the container
echo ""
echo "Step 1: Stopping container..."
docker stop "$DB_CONTAINER" || true

# Step 2: Backup and modify pg_hba.conf
echo ""
echo "Step 2: Modifying authentication settings..."
docker run --rm -v worky_postgres-data:/data -v $(pwd):/backup postgres:15 bash -c "
    # Find the pg_hba.conf file in the volume
    PG_DATA_DIR=\$(find /data -name pg_hba.conf 2>/dev/null | head -1 | xargs dirname)
    if [ -z \"\$PG_DATA_DIR\" ]; then
        echo 'Error: Could not find pg_hba.conf'
        exit 1
    fi
    
    # Backup original
    cp \$PG_DATA_DIR/pg_hba.conf \$PG_DATA_DIR/pg_hba.conf.backup
    
    # Create temporary pg_hba.conf with trust for local connections
    cat > \$PG_DATA_DIR/pg_hba.conf << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host    all             all             0.0.0.0/0               md5
EOF
    echo 'pg_hba.conf modified temporarily'
"

# Step 3: Start container
echo ""
echo "Step 3: Starting container with temporary trust authentication..."
docker start "$DB_CONTAINER"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5
for i in {1..30}; do
    if docker exec "$DB_CONTAINER" pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Step 4: Reset password
echo ""
echo "Step 4: Resetting password..."
docker exec "$DB_CONTAINER" psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';"

# Step 5: Restore original pg_hba.conf
echo ""
echo "Step 5: Restoring original authentication settings..."
docker run --rm -v worky_postgres-data:/data postgres:15 bash -c "
    PG_DATA_DIR=\$(find /data -name pg_hba.conf 2>/dev/null | head -1 | xargs dirname)
    if [ -f \$PG_DATA_DIR/pg_hba.conf.backup ]; then
        mv \$PG_DATA_DIR/pg_hba.conf.backup \$PG_DATA_DIR/pg_hba.conf
        echo 'Original pg_hba.conf restored'
    else
        # Restore default if backup not found
        cat > \$PG_DATA_DIR/pg_hba.conf << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF
        echo 'Default pg_hba.conf created'
    fi
"

# Step 6: Restart container
echo ""
echo "Step 6: Restarting container with normal authentication..."
docker restart "$DB_CONTAINER"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5
for i in {1..30}; do
    if docker exec "$DB_CONTAINER" pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Step 7: Verify
echo ""
echo "Step 7: Verifying password..."
if docker exec -e PGPASSWORD="$NEW_PASSWORD" "$DB_CONTAINER" psql -U postgres -d worky -c "SELECT version();" > /dev/null 2>&1; then
    echo "✓ Password verification successful!"
    echo ""
    echo "========================================="
    echo "Password fix completed successfully!"
    echo "========================================="
    echo ""
    echo "The database password has been reset to: $NEW_PASSWORD"
    echo ""
    echo "Next steps:"
    echo "1. Restart the API container: docker restart worky-api"
    echo "2. Check API logs: docker logs worky-api"
else
    echo "✗ Password verification failed."
    exit 1
fi

#!/bin/bash
# One-time migration script to move from bind mount to Docker volume
# This permanently fixes the password issue

set -e

echo "🔄 Migrating to Docker-managed volume..."
echo "This will permanently fix the password authentication issue"
echo ""

# Step 1: Backup current database
echo "1️⃣ Backing up current database..."
docker exec worky-postgres pg_dump -U postgres worky > /tmp/worky_backup_$(date +%Y%m%d_%H%M%S).sql
echo "   ✅ Backup created"
echo ""

# Step 2: Stop all services
echo "2️⃣ Stopping services..."
docker compose down
echo "   ✅ Services stopped"
echo ""

# Step 3: Remove old bind mount volume
echo "3️⃣ Removing old volume directory..."
if [ -d "volumes/postgres-data" ]; then
    mv volumes/postgres-data volumes/postgres-data.backup_$(date +%Y%m%d_%H%M%S)
    echo "   ✅ Old volume backed up"
fi
echo ""

# Step 4: Start with new Docker volume
echo "4️⃣ Starting with new Docker-managed volume..."
docker compose up -d
echo "   ⏳ Waiting for postgres to initialize..."
sleep 20

# Wait for postgres to be ready
for i in {1..30}; do
    if docker exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "   ✅ Postgres is ready"
        break
    fi
    sleep 1
done
echo ""

# Step 5: Restore data
echo "5️⃣ Restoring database..."
LATEST_BACKUP=$(ls -t /tmp/worky_backup_*.sql | head -1)
docker exec -i worky-postgres psql -U postgres -d worky < "$LATEST_BACKUP"
echo "   ✅ Database restored"
echo ""

# Step 6: Restart API
echo "6️⃣ Restarting API..."
docker restart worky-api
sleep 5
echo "   ✅ API restarted"
echo ""

echo "🎉 Migration complete!"
echo ""
echo "The password issue is now permanently fixed."
echo "Your data has been migrated to a Docker-managed volume."
echo ""
echo "Backup files:"
echo "  Database: $LATEST_BACKUP"
echo "  Old volume: volumes/postgres-data.backup_*"
echo ""

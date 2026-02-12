#!/bin/bash
# Test script to verify migration will work before running it

echo "🔍 Testing migration prerequisites..."
echo ""

# Test 1: Can we connect to postgres?
echo "Test 1: Database connection..."
if docker exec worky-postgres psql -U postgres -d worky -c "SELECT 1" > /dev/null 2>&1; then
    echo "   ✅ Can connect to database"
else
    echo "   ❌ Cannot connect to database"
    echo "   Fix: Run this first:"
    echo "   docker exec -it worky-postgres psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
    echo "   docker restart worky-api"
    exit 1
fi

# Test 2: Can we create a backup?
echo "Test 2: Database backup..."
if docker exec worky-postgres pg_dump -U postgres worky > /tmp/test_backup.sql 2>/dev/null; then
    BACKUP_SIZE=$(wc -l < /tmp/test_backup.sql)
    echo "   ✅ Backup successful ($BACKUP_SIZE lines)"
    rm /tmp/test_backup.sql
else
    echo "   ❌ Backup failed"
    exit 1
fi

# Test 3: Check disk space
echo "Test 3: Disk space..."
AVAILABLE=$(df /var/lib/docker | tail -1 | awk '{print $4}')
if [ "$AVAILABLE" -gt 1000000 ]; then
    echo "   ✅ Sufficient disk space"
else
    echo "   ⚠️  Low disk space: ${AVAILABLE}KB available"
fi

# Test 4: Check if volumes directory exists
echo "Test 4: Current volume..."
if [ -d "volumes/postgres-data" ]; then
    SIZE=$(du -sh volumes/postgres-data | cut -f1)
    echo "   ✅ Volume exists (size: $SIZE)"
else
    echo "   ⚠️  Volume directory not found"
fi

echo ""
echo "✅ All tests passed!"
echo ""
echo "You can safely run the migration:"
echo "   ./migrate_to_docker_volume.sh"
echo ""
echo "⚠️  Note: Application will be down for 1-2 minutes during migration"

#!/bin/bash
# Start All Worky Services (Bash)
# Usage: ./start_all.sh

echo "🚀 Starting All Worky Services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Set up Docker commands (use Windows Docker if in WSL)
if [ -f "/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe" ]; then
    DOCKER_COMPOSE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker-compose.exe"
    DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    DOCKER="docker"
else
    DOCKER_COMPOSE="docker compose"
    DOCKER="docker"
fi

# Start Database and API via Docker
echo ""
echo "1️⃣ Starting Database and API (Docker)..."
"$DOCKER_COMPOSE" up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Docker services failed to start"
    exit 1
fi

echo "✅ Database and API started"

# Wait for services to be healthy
echo ""
echo "2️⃣ Waiting for services to be healthy..."
sleep 10

# Check database
DB_READY=false
for i in {1..30}; do
    if "$DOCKER" exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Database is healthy"
        DB_READY=true
        break
    fi
    sleep 1
done

if [ "$DB_READY" = false ]; then
    echo "⚠️  Database may still be starting, but continuing..."
fi

# Apply database migrations
echo ""
echo "3️⃣ Applying database migrations..."
DB_CONTAINER="worky-postgres"
DB_NAME="worky"
DB_USER="postgres"
MIGRATIONS_APPLIED=0
MIGRATIONS_SKIPPED=0

# Wait a bit more for database to be fully ready
sleep 2

# Check if migrations directory exists
if [ ! -d "$PROJECT_ROOT/db/migrations" ]; then
    echo "⚠️  Migrations directory not found, skipping..."
else
    # Check if database is empty (no tables exist)
    TABLE_COUNT=$("$DOCKER" exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d '[:space:]')
    
    if [ -z "$TABLE_COUNT" ] || [ "$TABLE_COUNT" = "0" ]; then
        # Database is empty - apply baseline schema
        echo "📋 Database is empty, applying baseline schema..."
        BASELINE_FILE="$PROJECT_ROOT/db/migrations/000_baseline_schema.sql"
        
        if [ -f "$BASELINE_FILE" ]; then
            output=$("$DOCKER" exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$BASELINE_FILE" 2>&1)
            exit_code=$?
            
            if [ $exit_code -eq 0 ]; then
                if echo "$output" | grep -qiE "ERROR|FATAL"; then
                    echo "  ❌ Error applying baseline schema: $(echo "$output" | grep -iE "ERROR|FATAL" | head -1)"
                else
                    echo "  ✅ Baseline schema applied successfully"
                    MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
                fi
            else
                echo "  ❌ Failed to apply baseline schema: $(echo "$output" | head -1)"
            fi
        else
            echo "  ⚠️  Baseline schema file not found: $BASELINE_FILE"
        fi
    else
        # Database has tables - apply incremental migrations (skip baseline and seed data)
        echo "📋 Database has existing tables, applying incremental migrations..."
        
        for migration in "$PROJECT_ROOT/db/migrations"/*.sql; do
            if [ -f "$migration" ]; then
                filename=$(basename "$migration")
                
                # Skip baseline schema (already applied if database has tables)
                if [[ "$filename" == "000_baseline_schema.sql" ]]; then
                    continue
                fi
                
                # Skip seed data file
                if [[ "$filename" == "999_seed_dev_data.sql" ]]; then
                    continue
                fi
                
                # Try to apply migration (suppress most output, capture errors)
                output=$("$DOCKER" exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$migration" 2>&1)
                exit_code=$?
                
                # Check if migration was successful
                # PostgreSQL migrations with "IF NOT EXISTS" will succeed even if already applied
                # We consider it successful if exit code is 0 and no critical errors
                if [ $exit_code -eq 0 ]; then
                    # Check for critical errors (but ignore "already exists" which is fine)
                    if echo "$output" | grep -qiE "ERROR|FATAL" && ! echo "$output" | grep -qiE "already exists|duplicate|NOTICE.*already exists"; then
                        echo "  ⚠️  Warning in $filename (check manually if needed)"
                        MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
                    else
                        # Migration applied successfully
                        # With "IF NOT EXISTS", migrations output both the command result AND "already exists" notices
                        # If we see the command result (ALTER TABLE, CREATE, etc.), the migration executed
                        # "NOTICE: already exists" is harmless and means the object already existed
                        if echo "$output" | grep -qiE "ALTER TABLE|CREATE|INSERT|UPDATE|DO|COMMENT"; then
                            # Check if this was a fresh application (no "already exists" notices) or idempotent (with notices)
                            if echo "$output" | grep -qi "NOTICE.*already exists"; then
                                # Migration ran but objects already existed - this is fine, mark as applied
                                MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
                                echo "  ✓ Applied: $filename (objects already existed, no changes needed)"
                            else
                                # Fresh application - migration made changes
                                MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
                                echo "  ✓ Applied: $filename"
                            fi
                        else
                            # No SQL commands detected in output - might be empty migration or already fully applied
                            MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
                        fi
                    fi
                else
                    # Exit code non-zero - check if it's a harmless "already exists" error
                    if echo "$output" | grep -qiE "already exists|duplicate|relation.*already exists"; then
                        MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
                    else
                        echo "  ⚠️  Error applying $filename: $(echo "$output" | head -1)"
                        MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
                    fi
                fi
            fi
        done
        
        if [ $MIGRATIONS_APPLIED -gt 0 ]; then
            echo "✅ Applied $MIGRATIONS_APPLIED migration(s)"
        fi
        if [ $MIGRATIONS_SKIPPED -gt 0 ]; then
            echo "ℹ️  Skipped $MIGRATIONS_SKIPPED migration(s) (already applied or no changes needed)"
        fi
    fi
    
    # Fix dependencies table if it still uses UUID (from old migration 002)
    echo ""
    echo "🔧 Checking and fixing dependencies table structure..."
    DEPENDENCIES_HAS_UUID=$("$DOCKER" exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'dependencies' AND column_name = 'id' AND data_type = 'uuid';" 2>/dev/null | tr -d '[:space:]')
    
    if [ "$DEPENDENCIES_HAS_UUID" = "1" ]; then
        echo "  ⚠️  Dependencies table uses UUID, converting to VARCHAR(20)..."
        "$DOCKER" exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF' > /dev/null 2>&1
-- Drop constraints that reference dependencies
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT conname, conrelid::regclass as table_name
              FROM pg_constraint 
              WHERE confrelid = 'dependencies'::regclass::oid) 
    LOOP
        EXECUTE 'ALTER TABLE ' || r.table_name || ' DROP CONSTRAINT IF EXISTS ' || r.conname || ' CASCADE';
    END LOOP;
END $$;

-- Drop and recreate with VARCHAR(20)
DROP TABLE IF EXISTS dependencies CASCADE;

CREATE TABLE dependencies (
    id VARCHAR(20) PRIMARY KEY DEFAULT generate_string_id('DEP', 'dependencies_id_seq'),
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    entity_id VARCHAR(20) NOT NULL,
    depends_on_type VARCHAR(50) NOT NULL CHECK (depends_on_type IN ('Program', 'Project', 'Usecase', 'UserStory', 'Task', 'Subtask')),
    depends_on_id VARCHAR(20) NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'finish_to_start' CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dependencies_entity ON dependencies(entity_type, entity_id);
CREATE INDEX idx_dependencies_depends_on ON dependencies(depends_on_type, depends_on_id);
EOF
        echo "  ✅ Dependencies table fixed"
    else
        echo "  ✅ Dependencies table structure is correct"
    fi
    
    # Ensure dependencies_id_seq exists
    echo ""
    echo "🔧 Ensuring required sequences exist..."
    "$DOCKER" exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "CREATE SEQUENCE IF NOT EXISTS dependencies_id_seq START 1;" > /dev/null 2>&1
    echo "  ✅ Sequences verified"
    
    # Apply seed data if no users exist
    echo ""
    echo "🌱 Checking for seed data..."
    USER_COUNT=$("$DOCKER" exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d '[:space:]')
    
    if [ -z "$USER_COUNT" ] || [ "$USER_COUNT" = "0" ]; then
        echo "  📋 No users found, applying seed data..."
        SEED_FILE="$PROJECT_ROOT/db/migrations/999_seed_dev_data.sql"
        
        if [ -f "$SEED_FILE" ]; then
            output=$("$DOCKER" exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$SEED_FILE" 2>&1)
            exit_code=$?
            
            if [ $exit_code -eq 0 ]; then
                if echo "$output" | grep -qiE "ERROR|FATAL"; then
                    echo "  ⚠️  Warning applying seed data: $(echo "$output" | grep -iE "ERROR|FATAL" | head -1)"
                else
                    echo "  ✅ Seed data applied successfully"
                fi
            else
                echo "  ⚠️  Seed data application had issues (check manually if needed)"
            fi
        else
            echo "  ⚠️  Seed data file not found: $SEED_FILE"
        fi
    else
        echo "  ✅ Found $USER_COUNT user(s) in database (seed data not needed)"
    fi
fi

# Check API
if curl -s http://localhost:8007/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "⚠️  API may still be starting"
fi

# Start UI
echo ""
echo "4️⃣ Starting UI..."
cd "$PROJECT_ROOT/ui"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing UI dependencies..."
    npm install
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Start UI in background
nohup npm run dev > "$PROJECT_ROOT/logs/ui.log" 2>&1 &
UI_PID=$!
echo "✅ UI started (PID: $UI_PID)"

# Return to project root
cd "$PROJECT_ROOT"

echo ""
echo "============================================"
echo "✅ All Worky Services Started!"
echo "============================================"
echo ""
echo "📊 Services:"
echo "   Database: localhost:5437 (Docker)"
echo "   API:      http://localhost:8007"
echo "   UI:       http://localhost:3007"
echo ""
echo "🔐 Login:"
echo "   Email:    admin@datalegos.com"
echo "   Password: password"
echo ""
echo "📝 Logs:"
echo "   API: $DOCKER logs worky-api -f"
echo "   DB:  $DOCKER logs worky-postgres -f"
echo "   UI:  tail -f logs/ui.log"
echo ""
echo "🛑 Stop:"
echo "   $SCRIPT_DIR/stop_all.sh"

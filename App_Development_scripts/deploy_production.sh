#!/bin/bash
# Production Deployment Script for Worky
# This script deploys Worky to production with a FRESH database (NO seed data)
# Usage: ./App_Development_scripts/deploy_production.sh

set -e

echo "🚀 Worky Production Deployment"
echo "=============================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found"
    echo "   Please create it from env.production.template:"
    echo "   cp env.production.template .env.production"
    echo "   Then edit .env.production with your production values"
    exit 1
fi

# Check if UI is built
if [ ! -d "ui/dist" ]; then
    echo "📦 Building UI for production..."
    cd "$PROJECT_ROOT/ui"
    if [ ! -d "node_modules" ]; then
        echo "   Installing dependencies..."
        npm install
    fi
    echo "   Building production bundle..."
    npm run build
    cd "$PROJECT_ROOT"
    
    if [ ! -d "ui/dist" ]; then
        echo "❌ Error: UI build failed"
        exit 1
    fi
    echo "✅ UI built successfully"
else
    echo "✅ UI already built"
fi

# Set up Docker commands
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    DOCKER="docker"
else
    DOCKER_COMPOSE="docker compose"
    DOCKER="docker"
fi

# Stop any existing containers
echo ""
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE -f docker-compose.prod.yml --env-file .env.production down 2>/dev/null || true

# Build and start services
echo ""
echo "🏗️  Building and starting production services..."
$DOCKER_COMPOSE -f docker-compose.prod.yml --env-file .env.production up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for database to be healthy
echo ""
echo "⏳ Waiting for database to be healthy..."
DB_CONTAINER="worky-postgres-prod"
DB_READY=false
for i in {1..60}; do
    if $DOCKER exec $DB_CONTAINER pg_isready -U ${DATABASE_USER:-worky_user} -d ${DATABASE_NAME:-worky} > /dev/null 2>&1; then
        echo "✅ Database is healthy"
        DB_READY=true
        break
    fi
    sleep 1
done

if [ "$DB_READY" = false ]; then
    echo "⚠️  Database may still be starting"
fi

# Wait a bit more for database to be fully ready
sleep 5

# Apply migrations (EXCLUDING seed data - CRITICAL for production)
echo ""
echo "📋 Applying database migrations (EXCLUDING seed data)..."
DB_NAME=${DATABASE_NAME:-worky}
DB_USER=${DATABASE_USER:-worky_user}

MIGRATIONS_APPLIED=0
MIGRATIONS_SKIPPED=0

# Check if database is empty (no tables exist)
TABLE_COUNT=$($DOCKER exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d '[:space:]')

if [ -z "$TABLE_COUNT" ] || [ "$TABLE_COUNT" = "0" ]; then
    # Database is empty - apply baseline schema
    echo "📋 Database is empty, applying baseline schema..."
    BASELINE_FILE="$PROJECT_ROOT/db/migrations/000_baseline_schema.sql"
    
    if [ -f "$BASELINE_FILE" ]; then
        output=$($DOCKER exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$BASELINE_FILE" 2>&1)
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            if echo "$output" | grep -qiE "ERROR|FATAL"; then
                echo "  ❌ Error applying baseline schema"
            else
                echo "  ✅ Baseline schema applied successfully"
                MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
            fi
        else
            echo "  ❌ Failed to apply baseline schema"
        fi
    fi
else
    echo "📋 Database has existing tables, applying incremental migrations..."
fi

# Apply all migrations EXCEPT seed data (999_seed_dev_data.sql)
for migration in "$PROJECT_ROOT/db/migrations"/*.sql; do
    if [ -f "$migration" ]; then
        filename=$(basename "$migration")
        
        # SKIP seed data file - this is CRITICAL for production
        if [[ "$filename" == "999_seed_dev_data.sql" ]]; then
            echo "  ⏭️  Skipping seed data file (production mode): $filename"
            continue
        fi
        
        # Skip baseline if already applied
        if [[ "$filename" == "000_baseline_schema.sql" ]] && [ "$TABLE_COUNT" != "0" ]; then
            continue
        fi
        
        # Apply migration
        output=$($DOCKER exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$migration" 2>&1)
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            if echo "$output" | grep -qiE "ERROR|FATAL" && ! echo "$output" | grep -qiE "already exists|duplicate|NOTICE.*already exists"; then
                echo "  ⚠️  Warning in $filename"
                MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
            else
                if echo "$output" | grep -qiE "ALTER TABLE|CREATE|INSERT|UPDATE|DO|COMMIT"; then
                    MIGRATIONS_APPLIED=$((MIGRATIONS_APPLIED + 1))
                    echo "  ✓ Applied: $filename"
                else
                    MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
                fi
            fi
        else
            if echo "$output" | grep -qiE "already exists|duplicate"; then
                MIGRATIONS_SKIPPED=$((MIGRATIONS_SKIPPED + 1))
            else
                echo "  ⚠️  Error applying $filename"
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

# Verify seed data was NOT loaded
echo ""
echo "🔍 Verifying no seed data was loaded..."
USER_COUNT=$($DOCKER exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d '[:space:]')

if [ -z "$USER_COUNT" ] || [ "$USER_COUNT" = "0" ]; then
    echo "✅ Database is fresh - no users found (as expected for production)"
    echo ""
    echo "⚠️  IMPORTANT: You need to create your first admin user!"
    echo "   You can do this via:"
    echo "   1. API endpoint: POST /api/v1/auth/register (if registration is enabled)"
    echo "   2. Direct database insert (see documentation)"
    echo "   3. Admin panel (if available)"
else
    echo "⚠️  Warning: Found $USER_COUNT user(s) in database"
    echo "   If this is a fresh deployment, this should be 0"
fi

# Check API health
echo ""
echo "🏥 Checking API health..."
sleep 5
if curl -s http://localhost:8007/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "⚠️  API may still be starting"
fi

# Check services status
echo ""
echo "📊 Services Status:"
$DOCKER ps --filter "name=worky" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "============================================"
echo "✅ Production Deployment Complete!"
echo "============================================"
echo ""
echo "📝 Next Steps:"
echo "   1. Start UI separately (not using nginx):"
echo "      cd ui && npm run build && npm run preview"
echo "      OR for development mode:"
echo "      cd ui && npm run dev"
echo ""
echo "   2. Create your first admin user via API:"
echo "      POST http://62.171.191.132:8007/api/v1/auth/register"
echo ""
echo "   3. Set up database backups"
echo "   4. Configure monitoring"
echo ""
echo "🌐 Access:"
echo "   API: http://62.171.191.132:8007"
echo "   UI:  http://62.171.191.132:3007 (after starting UI)"
echo ""
echo "📚 Documentation:"
echo "   See DEPLOYMENT.md for detailed instructions"
echo ""

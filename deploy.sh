#!/bin/bash

# Worky Unified Deployment Script
# Works for both local development and production deployment
# Auto-detects environment and configures accordingly

set -e

echo "🚀 Worky Deployment Script"
echo "============================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect if running locally or on remote server
# Check if we're on localhost (127.0.0.1) or have a public IP
CURRENT_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

# Determine if this is local or production
if [[ "$CURRENT_IP" == "127.0.0.1" ]] || [[ "$CURRENT_IP" == "localhost" ]] || [[ -z "$CURRENT_IP" ]]; then
    ENVIRONMENT="local"
    API_URL="http://localhost:8007/api/v1"
    echo "📍 Environment: LOCAL DEVELOPMENT"
else
    ENVIRONMENT="production"
    API_URL="http://${CURRENT_IP}:8007/api/v1"
    echo "📍 Environment: PRODUCTION"
    echo "📍 Server IP: $CURRENT_IP"
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        echo "📋 Creating .env from .env.example..."
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        
        # Auto-configure based on environment
        if [ "$ENVIRONMENT" == "production" ]; then
            sed -i "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=$API_URL|g" "$SCRIPT_DIR/.env"
            echo "✅ .env configured for production with IP: $CURRENT_IP"
        else
            echo "✅ .env configured for local development"
        fi
    else
        echo "⚠️  Warning: .env.example not found"
    fi
fi

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "📋 Loading environment variables..."
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | grep -v '^$' | xargs)
    
    # Override with detected environment if needed
    if [ "$ENVIRONMENT" == "production" ] && [[ "$VITE_API_BASE_URL" == *"localhost"* ]]; then
        echo "⚠️  Detected localhost in .env but running on production server"
        echo "   Overriding with: $API_URL"
        export VITE_API_BASE_URL="$API_URL"
    fi
else
    echo "⚠️  Warning: .env not found, using auto-detected values"
    export VITE_API_BASE_URL="$API_URL"
fi

echo "   API URL: $VITE_API_BASE_URL"
echo ""

# Stop existing containers
echo "📦 Stopping existing containers..."
docker compose down 2>/dev/null || true

# Remove old UI image to force rebuild
echo "🗑️  Removing old UI image..."
docker rmi worky-ui 2>/dev/null || echo "No existing UI image"

# Clear build cache for clean build
if [ "$ENVIRONMENT" == "production" ]; then
    echo "🧹 Clearing Docker build cache..."
    docker builder prune -f
fi

# Build and start all services
echo ""
echo "🔧 Building services..."
docker compose build --no-cache

echo ""
echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo ""
echo "🔍 Checking service status..."
docker compose ps

# Check database
echo ""
DB_READY=false
for i in {1..30}; do
    if docker exec worky-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Database is healthy"
        DB_READY=true
        break
    fi
    sleep 1
done

if [ "$DB_READY" = false ]; then
    echo "⚠️  Database may still be starting..."
fi

# Check API health
echo ""
if curl -f http://localhost:8007/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed"
    echo "   Check logs: docker logs worky-api --tail 50"
fi

# Check UI
if curl -f http://localhost:3007 > /dev/null 2>&1; then
    echo "✅ UI is accessible"
else
    echo "⚠️  UI check failed"
    echo "   Check logs: docker logs worky-ui --tail 50"
fi

# Verify UI build contains correct API URL
echo ""
echo "🔍 Verifying UI configuration..."
UI_API_URL=$(docker exec worky-ui sh -c "grep -o 'http://[^\"]*8007' /app/dist/assets/index-*.js | head -1" 2>/dev/null || echo "")
if [ -n "$UI_API_URL" ]; then
    echo "   UI is configured to call: $UI_API_URL"
    if [ "$ENVIRONMENT" == "production" ] && [[ "$UI_API_URL" == *"localhost"* ]]; then
        echo "   ⚠️  WARNING: UI is using localhost on production server!"
    else
        echo "   ✅ UI configuration is correct"
    fi
else
    echo "   ⚠️  Could not verify API URL in UI build"
fi

# Apply database migrations (only for local or first-time production)
if [ "$ENVIRONMENT" == "local" ]; then
    echo ""
    echo "🔧 Applying database migrations..."
    sleep 2
    
    DB_CONTAINER="worky-postgres"
    DB_NAME="worky"
    DB_USER="postgres"
    
    # Check if database has tables
    TABLE_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d '[:space:]' || echo "0")
    
    if [ "$TABLE_COUNT" = "0" ]; then
        echo "   Database is empty, applying migrations..."
        
        if [ -d "$SCRIPT_DIR/db/migrations" ]; then
            for migration in "$SCRIPT_DIR/db/migrations"/*.sql; do
                if [ -f "$migration" ]; then
                    filename=$(basename "$migration")
                    if [[ "$filename" != "999_seed_dev_data.sql" ]]; then
                        docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$migration" > /dev/null 2>&1 || true
                    fi
                fi
            done
            echo "   ✅ Migrations applied"
            
            # Apply seed data
            if [ -f "$SCRIPT_DIR/db/migrations/999_seed_dev_data.sql" ]; then
                docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < "$SCRIPT_DIR/db/migrations/999_seed_dev_data.sql" > /dev/null 2>&1 || true
                echo "   ✅ Seed data applied"
            fi
        fi
    else
        echo "   ✅ Database already has $TABLE_COUNT tables"
    fi
fi

# Display summary
echo ""
echo "🎉 Deployment Complete!"
echo "============================================"

if [ "$ENVIRONMENT" == "local" ]; then
    echo "📍 Local Development:"
    echo "   UI:       http://localhost:3007"
    echo "   API:      http://localhost:8007"
    echo "   API Docs: http://localhost:8007/docs"
    echo "   Database: localhost:5437"
else
    echo "📍 Production Server:"
    echo "   UI:       http://${CURRENT_IP}:3007"
    echo "   API:      http://${CURRENT_IP}:8007"
    echo "   API Docs: http://${CURRENT_IP}:8007/docs"
    echo "   Database: localhost:5437"
fi

echo ""
echo "🔐 Default Login:"
echo "   Email:    admin@datalegos.com"
echo "   Password: password"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:     docker logs worky-api -f"
echo "   Stop services: docker compose down"
echo "   Restart API:   docker restart worky-api"
echo ""

if [ "$ENVIRONMENT" == "production" ]; then
    echo "⚠️  TROUBLESHOOTING:"
    echo ""
    echo "If login fails with 'password authentication failed':"
    echo "   docker exec -it worky-postgres psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
    echo "   docker restart worky-api"
    echo ""
fi

echo "============================================"

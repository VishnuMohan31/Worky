#!/bin/bash

# Contabo Production Deployment Script for Worky
# Server: 62.171.191.132

set -e  # Exit on error

echo "🚀 Starting Production Deployment..."
echo "============================================"

# Load production environment variables
if [ -f .env.production ]; then
    echo "📋 Loading production environment..."
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env.production not found, using defaults"
fi

# Stop existing containers
echo "📦 Stopping existing containers..."
docker compose down

# Remove old UI image to force rebuild
echo "🗑️  Removing old UI image..."
docker rmi worky-ui 2>/dev/null || echo "No existing UI image to remove"

# Clear build cache
echo "🧹 Clearing Docker build cache..."
docker builder prune -f

# Build and start all services with production config
echo "🔧 Building services with production configuration..."
echo "   API URL: $VITE_API_BASE_URL"
docker compose build --no-cache

echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
echo "🔍 Checking service status..."
docker compose ps

# Check API health
echo "🔍 Checking API health..."
sleep 5
curl -f http://localhost:8007/health && echo "✅ API is healthy" || echo "⚠️  API health check failed"

# Check UI
echo "🔍 Checking UI..."
curl -f http://localhost:3007 && echo "✅ UI is accessible" || echo "⚠️  UI check failed"

# Verify UI build contains production API URL
echo "🔍 Verifying UI configuration..."
docker exec worky-ui sh -c "grep -o 'http://[^\"]*8007' /app/dist/assets/index-*.js | head -3" || echo "Could not verify API URL in build"

echo ""
echo "🎉 Deployment Complete!"
echo "============================================"
echo "📍 Services:"
echo "   API:    http://62.171.191.132:8007"
echo "   UI:     http://62.171.191.132:3007"
echo "   Health: http://62.171.191.132:8007/health"
echo ""
echo "📝 View logs:"
echo "   docker compose logs -f api"
echo "   docker compose logs -f ui"
echo ""
echo "🛑 Stop services:"
echo "   docker compose down"
echo "============================================"
echo ""
echo "⚠️  IMPORTANT: If login fails with database errors, run:"
echo "   docker exec -it worky-postgres psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
echo "   docker restart worky-api"
echo "============================================"
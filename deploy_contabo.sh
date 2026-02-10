#!/bin/bash

# Contabo Deployment Script for Worky
echo "🚀 Starting Contabo deployment..."

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start all services (DB, API, UI) with production config
echo "🔧 Building and starting all services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Verify database is ready
echo "🗄️ Verifying database..."
docker-compose -f docker-compose.prod.yml exec -T db psql -U worky_user -d worky -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" || echo "⚠️  Database check failed (may still be initializing)"

# Check API health
echo "🔍 Checking API health..."
sleep 10
curl -f http://localhost:8007/health || echo "⚠️  API health check failed (may still be starting)"

# Check UI
echo "🔍 Checking UI..."
curl -f http://localhost:3007 || echo "⚠️  UI check failed (may still be starting)"

echo ""
echo "🎉 Deployment complete!"
echo "============================================"
echo "📍 Services:"
echo "   API:    http://62.171.191.132:8007"
echo "   UI:     http://62.171.191.132:3007"
echo "   Health: http://62.171.191.132:8007/health"
echo ""
echo "📝 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo "============================================"
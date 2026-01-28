#!/bin/bash

# Contabo Deployment Script for Worky
echo "🚀 Starting Contabo deployment..."

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start API + DB with production config
echo "🔧 Starting API and Database..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready (longer wait for initial DB setup)
echo "⏳ Waiting for services to start and database initialization..."
sleep 60

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Verify database is ready
echo "🗄️ Verifying database initialization..."
docker-compose -f docker-compose.prod.yml exec -T db psql -U worky_user -d worky -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Build UI for production
echo "🎨 Building UI for production..."
cd ui

# Use production environment for build
cp .env.production .env.local

npm run build
echo "✅ UI built successfully"

# Start UI in production mode
echo "🌐 Starting UI server..."
npm run preview -- --host 0.0.0.0 --port 3007 &

echo "🎉 Deployment complete!"
echo "📍 API: http://62.171.191.132:8007"
echo "📍 UI:  http://62.171.191.132:3007"
echo "📍 Health: http://62.171.191.132:8007/health"
echo ""
echo "ℹ️  Database initialized with initial scripts from db/initial_scripts/"
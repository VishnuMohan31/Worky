#!/bin/bash
# Comprehensive fix for production deployment issues
# Run this on the remote server at 62.171.191.132

set -e  # Exit on error

echo "=========================================="
echo "Production Deployment Fix Script"
echo "=========================================="
echo ""

# Step 1: Fix database password
echo "Step 1: Fixing database password..."
docker exec -it worky-postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" || {
    echo "✗ Failed to update database password"
    exit 1
}
echo "✓ Database password updated"
echo ""

# Step 2: Rebuild UI with production API URL
echo "Step 2: Rebuilding UI with production API URL..."
echo "Stopping containers..."
docker compose down

echo "Removing old UI image..."
docker rmi worky-ui 2>/dev/null || echo "No existing UI image to remove"

echo "Clearing Docker build cache..."
docker builder prune -f

echo "Building UI with production API URL..."
VITE_API_BASE_URL=http://62.171.191.132:8007/api/v1 docker compose build --no-cache ui

echo "✓ UI rebuilt with production configuration"
echo ""

# Step 3: Start all services
echo "Step 3: Starting all services..."
VITE_API_BASE_URL=http://62.171.191.132:8007/api/v1 docker compose up -d

echo "Waiting for services to start..."
sleep 10

# Step 4: Verify deployment
echo ""
echo "Step 4: Verifying deployment..."
echo ""

echo "Checking API health..."
curl -f http://localhost:8007/health && echo "✓ API is healthy" || echo "✗ API health check failed"
echo ""

echo "Checking UI is running..."
docker ps | grep worky-ui && echo "✓ UI container is running" || echo "✗ UI container not running"
echo ""

echo "Verifying UI build contains production API URL..."
docker exec worky-ui grep -o "http://[^\"]*8007" /app/dist/assets/index-*.js | head -3
echo ""

echo "=========================================="
echo "Deployment Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open browser to: http://62.171.191.132:3007"
echo "2. Try logging in with your credentials"
echo "3. Check browser console (F12) for any errors"
echo ""
echo "If issues persist, check logs:"
echo "  docker logs worky-api --tail 50"
echo "  docker logs worky-ui --tail 50"
echo ""

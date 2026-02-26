#!/bin/bash

echo "=========================================="
echo "Fixing Local Development Environment"
echo "=========================================="
echo ""

echo "ISSUE: Docker UI container is serving production build with production API URL"
echo "SOLUTION: Run UI in development mode to use local API"
echo ""

# Stop Docker UI container
echo "1. Stopping Docker UI container..."
docker stop worky-ui
docker rm worky-ui
echo "   ✓ Docker UI container stopped"
echo ""

# Verify ui/.env.local exists
if [ ! -f ui/.env.local ]; then
    echo "2. Creating ui/.env.local..."
    cat > ui/.env.local << 'EOF'
# Local Development Override
# This file has HIGHEST PRIORITY and overrides all other .env files
VITE_API_BASE_URL=http://localhost:8007/api/v1
VITE_API_TIMEOUT=30000
EOF
    echo "   ✓ Created ui/.env.local"
else
    echo "2. ui/.env.local already exists ✓"
fi
echo ""

# Install dependencies if needed
echo "3. Checking UI dependencies..."
cd ui
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
else
    echo "   ✓ Dependencies already installed"
fi
cd ..
echo ""

echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Clear your browser cache:"
echo "   - Press Ctrl+Shift+Delete"
echo "   - Select 'All time'"
echo "   - Check 'Cached images and files'"
echo "   - Click 'Clear data'"
echo ""
echo "2. Start UI in development mode:"
echo "   cd ui"
echo "   npm run dev"
echo ""
echo "3. Access the app at: http://localhost:5173"
echo "   (Vite dev server uses port 5173, not 3007)"
echo ""
echo "4. Verify in browser console (F12 → Network tab):"
echo "   - API requests should go to localhost:8007"
echo "   - NOT to 62.171.191.132:8007"
echo ""
echo "=========================================="
echo "IMPORTANT:"
echo "=========================================="
echo "- Development mode: http://localhost:5173 → localhost:8007 (local data)"
echo "- Docker container: http://localhost:3007 → 62.171.191.132:8007 (production data)"
echo ""
echo "For local development, ALWAYS use: npm run dev"
echo "=========================================="

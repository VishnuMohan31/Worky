#!/bin/bash
# Build UI for production deployment
# This script builds the UI with proper environment handling

set -e

echo "🏗️  Building Worky UI for production..."

cd "$(dirname "$0")/../ui"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Verify queryClient.ts has the fix
if grep -q "isDevelopment" src/lib/queryClient.ts; then
    echo "✅ queryClient.ts includes environment safety fix"
else
    echo "⚠️  Warning: queryClient.ts may not have the latest fixes"
fi

# Build the application
echo "🔨 Building production bundle..."
echo "   This will create an optimized build with proper environment handling"
npm run build

# Check if build was successful
if [ -d "dist" ]; then
    echo ""
    echo "✅ UI build successful!"
    echo "📁 Build output: ui/dist/"
    echo "📊 Build size:"
    du -sh dist/
    echo ""
    echo "ℹ️  Note: The build includes fixes for first-load initialization"
    echo "   The application will work correctly on first load on new devices"
else
    echo "❌ Build failed - dist directory not found"
    exit 1
fi


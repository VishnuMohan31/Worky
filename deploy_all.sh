#!/bin/bash

# Deploy Worky Application - Production Ready
# This script starts all services: DB, API, and UI

set -e

echo "=========================================="
echo "Deploying Worky Application"
echo "=========================================="

# Pull latest changes from git
echo "Pulling latest changes..."
git pull origin main

# Build and start all services
echo "Building and starting all services (DB, API, UI)..."
docker compose up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 15

# Check all services status
echo ""
echo "=========================================="
echo "Service Status:"
echo "=========================================="
docker compose ps

# Show recent logs
echo ""
echo "=========================================="
echo "Recent Logs:"
echo "=========================================="
echo ""
echo "--- Database Logs ---"
docker logs worky-postgres --tail=10
echo ""
echo "--- API Logs ---"
docker logs worky-api --tail=10
echo ""
echo "--- UI Logs ---"
docker logs worky-ui --tail=10

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "UI:       http://62.171.191.132:3007"
echo "API:      http://62.171.191.132:8007"
echo "Database: localhost:5437"
echo ""
echo "Login: admin@worky.com / password"
echo ""
echo "Commands:"
echo "  View logs:    docker compose logs -f"
echo "  Stop all:     docker compose down"
echo "  Restart all:  docker compose restart"
echo "=========================================="

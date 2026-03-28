#!/bin/bash
# Verify all Worky services are healthy and login works
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Verifying Worky services..."
echo ""

# Check DB
if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database: healthy${NC}"
else
    echo -e "${RED}❌ Database: not running${NC}"
    exit 1
fi

# Check API
if curl -sf http://localhost:8007/health > /dev/null; then
    echo -e "${GREEN}✅ API: healthy${NC}"
else
    echo -e "${RED}❌ API: not running${NC}"
    exit 1
fi

# Check UI
if curl -sf http://localhost:3007 > /dev/null; then
    echo -e "${GREEN}✅ UI: healthy${NC}"
else
    echo -e "${RED}❌ UI: not running${NC}"
    exit 1
fi

# Test login
echo ""
echo "Testing login..."
RESPONSE=$(curl -sf -X POST http://localhost:8007/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@datalegos.com","password":"password"}' || echo "")

if echo "$RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login: working${NC}"
else
    echo -e "${RED}❌ Login: failed${NC}"
    exit 1
fi

echo ""
echo "All checks passed."

#!/bin/bash
# Run API integration tests against all main endpoints
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8007/api/v1"

echo "Running API integration tests..."
echo ""

# Login
TOKEN=$(curl -sf -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@datalegos.com","password":"password"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Login failed - cannot run tests${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Login successful${NC}"

AUTH="-H \"Authorization: Bearer $TOKEN\""

test_endpoint() {
    local name=$1
    local url=$2
    if curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/$url" > /dev/null; then
        echo -e "${GREEN}✅ $name${NC}"
    else
        echo -e "${RED}❌ $name${NC}"
    fi
}

echo ""
test_endpoint "Clients"      "clients/"
test_endpoint "Programs"     "programs/"
test_endpoint "Projects"     "projects/"
test_endpoint "Use Cases"    "usecases/"
test_endpoint "User Stories" "user-stories/"
test_endpoint "Tasks"        "tasks/"
test_endpoint "Subtasks"     "subtasks/"
test_endpoint "Bugs"         "bugs/"
test_endpoint "Users"        "users/"
test_endpoint "Phases"       "phases/"

echo ""
echo "Tests complete."

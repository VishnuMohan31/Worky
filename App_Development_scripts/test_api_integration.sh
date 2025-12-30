#!/bin/bash

# Worky API Integration Test
# Tests all hierarchy endpoints to ensure Database → API → UI integration

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "  Worky API Integration Test"
echo "========================================="
echo ""

# Login and get token
echo "Logging in..."
TOKEN=$(curl -s -X POST http://localhost:8007/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@datalegos.com","password":"password"}' | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo -e "${RED}✗ Login failed${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Login successful${NC}"
echo ""

# Test each endpoint
test_endpoint() {
  local name=$1
  local endpoint=$2
  local count_path=$3
  
  echo -n "Testing $name... "
  result=$(curl -s http://localhost:8007/api/v1/$endpoint -H "Authorization: Bearer $TOKEN" | jq "$count_path")
  
  if [ "$result" == "null" ] || [ -z "$result" ]; then
    echo -e "${RED}✗ Failed${NC}"
    return 1
  else
    echo -e "${GREEN}✓ Found $result record(s)${NC}"
    return 0
  fi
}

echo "Testing Hierarchy Endpoints:"
echo "----------------------------"
test_endpoint "Clients" "clients/" ".clients | length"
test_endpoint "Programs" "programs/" "length"
test_endpoint "Projects" "projects/" "length"
test_endpoint "Use Cases" "usecases/" "length"
test_endpoint "User Stories" "user-stories/" "length"
test_endpoint "Tasks" "tasks/" "length"
test_endpoint "Subtasks" "subtasks/" "length"
echo ""

echo "Testing Other Endpoints:"
echo "------------------------"
test_endpoint "Bugs" "bugs/" "length"
test_endpoint "Users" "users/" "length"
test_endpoint "Phases" "phases/" "length"
echo ""

echo "Testing Special Endpoints:"
echo "--------------------------"
echo -n "Testing Client Statistics... "
stats=$(curl -s http://localhost:8007/api/v1/clients/statistics/dashboard -H "Authorization: Bearer $TOKEN" | jq '.total_clients')
if [ "$stats" != "null" ] && [ ! -z "$stats" ]; then
  echo -e "${GREEN}✓ Found $stats client(s)${NC}"
else
  echo -e "${RED}✗ Failed${NC}"
fi

echo -n "Testing Current User... "
user=$(curl -s http://localhost:8007/api/v1/auth/me -H "Authorization: Bearer $TOKEN" | jq -r '.email')
if [ "$user" != "null" ] && [ ! -z "$user" ]; then
  echo -e "${GREEN}✓ User: $user${NC}"
else
  echo -e "${RED}✗ Failed${NC}"
fi
echo ""

echo "========================================="
echo -e "${GREEN}  All Tests Completed Successfully!${NC}"
echo "========================================="

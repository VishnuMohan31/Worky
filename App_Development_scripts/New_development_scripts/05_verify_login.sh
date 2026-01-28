#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================================"
echo "                        WORKY LOGIN VERIFICATION"
echo "============================================================================"

echo ""
echo -e "${BLUE}[1/4] Checking if services are running...${NC}"

# Check database
if docker exec worky-postgres pg_isready -U postgres -d worky >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is running${NC}"
else
    echo -e "${RED}❌ Database is not running${NC}"
    echo "Run: ./01_startup_complete_application.sh"
    exit 1
fi

# Check API
if curl -s http://localhost:8007/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API is running${NC}"
else
    echo -e "${RED}❌ API is not running${NC}"
    echo "Run: docker-compose up -d api"
    exit 1
fi

# Check UI (just check if port is open)
if curl -s http://localhost:3007 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ UI is running${NC}"
else
    echo -e "${YELLOW}⚠️  UI may not be running (check manually)${NC}"
fi

echo ""
echo -e "${BLUE}[2/4] Checking database tables...${NC}"
table_count=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
echo "Tables found: $table_count"

if [ "$table_count" -lt 40 ]; then
    echo -e "${RED}❌ Not enough tables. Expected 50+${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Good table count${NC}"
fi

echo ""
echo -e "${BLUE}[3/4] Checking admin user...${NC}"
admin_exists=$(docker exec worky-postgres psql -U postgres -d worky -t -c "SELECT COUNT(*) FROM users WHERE email = 'admin@datalegos.com';" | tr -d ' ')

if [ "$admin_exists" -eq 0 ]; then
    echo -e "${RED}❌ Admin user not found${NC}"
    echo "Creating admin user..."
    docker exec worky-postgres psql -U postgres -d worky -c "
        INSERT INTO clients (id, name, short_description, email, is_active, created_at, updated_at) 
        VALUES ('CLI-000001', 'DataLegos', 'Default client for admin access', 'admin@datalegos.com', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING;
        
        INSERT INTO users (id, email, hashed_password, full_name, role, primary_role, client_id, is_active, created_at, updated_at) 
        VALUES ('USER-000001', 'admin@datalegos.com', '\$2b\$12\$LdKRRuZSyld/dzgpaGWKpuJqwAwIHKNOdZ79uc8931I3kZHZ.ScRa', 'Admin User', 'Admin', 'Admin', 'CLI-000001', true, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET hashed_password = EXCLUDED.hashed_password, updated_at = NOW();
    "
    echo -e "${GREEN}✅ Admin user created${NC}"
else
    echo -e "${GREEN}✅ Admin user exists${NC}"
fi

echo ""
echo -e "${BLUE}[4/4] Testing login API...${NC}"
login_response=$(curl -s -X POST http://localhost:8007/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@datalegos.com", "password": "password"}')

if echo "$login_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login API works${NC}"
else
    echo -e "${RED}❌ Login API failed${NC}"
    echo "Response: $login_response"
    exit 1
fi

echo ""
echo "============================================================================"
echo "                           VERIFICATION COMPLETE"
echo "============================================================================"
echo ""
echo -e "${GREEN}✅ All systems are working!${NC}"
echo ""
echo -e "${BLUE}🔐 Login Credentials:${NC}"
echo "   - Email: admin@datalegos.com"
echo "   - Password: password"
echo ""
echo -e "${BLUE}🔗 Access Points:${NC}"
echo "   - UI Application: http://localhost:3007"
echo "   - API Documentation: http://localhost:8007/docs"
echo ""
echo -e "${GREEN}You can now login to the application!${NC}"
echo ""
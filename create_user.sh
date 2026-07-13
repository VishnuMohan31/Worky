#!/bin/bash

# Script to create a new user in the Worky database
# Usage: ./create_user.sh <email> <full_name> <role> <password>

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Usage: $0 <email> <full_name> <role> [password]${NC}"
    echo ""
    echo "Example: $0 john@example.com 'John Doe' Developer password123"
    echo ""
    echo "Available roles:"
    echo "  - Admin"
    echo "  - HR"
    echo "  - Developer"
    echo "  - Tester"
    echo "  - Architect"
    echo "  - Designer"
    echo "  - Product Manager"
    echo "  - DevOps"
    echo "  - Owner"
    echo "  - Contact Person"
    exit 1
fi

EMAIL=$1
FULL_NAME=$2
ROLE=$3
PASSWORD=${4:-password123}  # Default password is 'password123'

echo "=========================================="
echo "🔧 Creating User"
echo "=========================================="
echo "Email: $EMAIL"
echo "Name: $FULL_NAME"
echo "Role: $ROLE"
echo "Password: $PASSWORD"
echo ""

# Check if user already exists
EXISTING=$(docker exec -i worky-postgres psql -U postgres -d worky -t -c "SELECT email FROM users WHERE email = '$EMAIL';")
if [ -n "$EXISTING" ]; then
    echo -e "${RED}❌ User with email $EMAIL already exists!${NC}"
    exit 1
fi

# Generate password hash
echo "🔐 Generating password hash..."
HASHED_PASSWORD=$(python3 -c "
import bcrypt
password = '$PASSWORD'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
")

if [ -z "$HASHED_PASSWORD" ]; then
    echo -e "${RED}❌ Failed to generate password hash${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Password hash generated${NC}"

# Create user in database
echo "📝 Creating user in database..."
docker exec -i worky-postgres psql -U postgres -d worky << EOF
INSERT INTO users (
  id, 
  email, 
  hashed_password, 
  full_name, 
  role, 
  client_id, 
  theme, 
  language, 
  is_active, 
  created_at, 
  updated_at
) VALUES (
  'USR-' || LPAD(CAST((SELECT COUNT(*) + 1 FROM users) AS TEXT), 6, '0'),
  '$EMAIL',
  '$HASHED_PASSWORD',
  '$FULL_NAME',
  '$ROLE',
  'CLI-000001',
  'snow',
  'en',
  true,
  NOW(),
  NOW()
);
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ User created successfully!${NC}"
    echo ""
    
    # Show user details
    echo "📋 User Details:"
    docker exec -i worky-postgres psql -U postgres -d worky -c "SELECT id, email, full_name, role, is_active FROM users WHERE email = '$EMAIL';"
    
    echo ""
    echo -e "${GREEN}🎉 User can now login with:${NC}"
    echo "   Email: $EMAIL"
    echo "   Password: $PASSWORD"
else
    echo -e "${RED}❌ Failed to create user${NC}"
    exit 1
fi

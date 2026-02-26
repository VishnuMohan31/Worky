#!/bin/bash

# Fix User Roles Constraint
# This script ensures the database has the correct role constraint with all 10 roles

echo "=========================================="
echo "Fixing User Roles Constraint"
echo "=========================================="
echo ""

# Check if database is running
if ! docker compose ps db | grep -q "Up"; then
    echo "❌ PostgreSQL container is not running"
    echo "Please start the application first:"
    echo "  cd App_Development_scripts/New_development_scripts"
    echo "  ./01_startup_complete_application.sh"
    exit 1
fi

echo "✓ PostgreSQL container is running"
echo ""

# Check current constraint
echo "Checking current role constraint..."
CURRENT_CONSTRAINT=$(docker compose exec -T db psql -U postgres -d worky -t -c "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'users_role_check';" 2>/dev/null)

if [ -z "$CURRENT_CONSTRAINT" ]; then
    echo "⚠ No users_role_check constraint found"
else
    echo "Current constraint:"
    echo "$CURRENT_CONSTRAINT"
fi

echo ""
echo "Applying fix..."
echo ""

# Apply the fix
docker compose exec -T db psql -U postgres -d worky << 'EOF'
BEGIN;

-- Drop the existing constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add the new constraint with all 10 roles
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (
    role IN (
        'Admin',
        'Developer', 
        'Tester',
        'Architect',
        'Designer',
        'HR',
        'Product Manager',
        'DevOps',
        'Owner',
        'Contact Person'
    )
);

-- Update the comment on the role column
COMMENT ON COLUMN users.role IS 'User role: Admin, Developer, Tester, Architect, Designer, HR, Product Manager, DevOps, Owner, Contact Person';

COMMIT;

-- Verify the constraint
SELECT 'Constraint updated successfully!' as status;
SELECT pg_get_constraintdef(oid) as constraint_definition 
FROM pg_constraint 
WHERE conname = 'users_role_check';
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ User roles constraint fixed successfully!"
    echo "=========================================="
    echo ""
    echo "You can now create users with these roles:"
    echo "  - Admin"
    echo "  - Developer"
    echo "  - Tester"
    echo "  - Architect"
    echo "  - Designer"
    echo "  - HR"
    echo "  - Product Manager"
    echo "  - DevOps"
    echo "  - Owner"
    echo "  - Contact Person"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Failed to fix constraint"
    echo "=========================================="
    echo ""
    exit 1
fi

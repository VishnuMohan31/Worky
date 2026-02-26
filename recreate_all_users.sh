#!/bin/bash

# Script to recreate all users shown in the UI screenshot
# Default password for all users: password123

echo "=========================================="
echo "🔧 Recreating All Users from Screenshot"
echo "=========================================="
echo ""

# Check if create_user.sh exists
if [ ! -f "./create_user.sh" ]; then
    echo "❌ Error: create_user.sh not found!"
    exit 1
fi

# Make sure it's executable
chmod +x ./create_user.sh

# List of users to create (from the screenshot)
# Format: email|full_name|role

USERS=(
    "sathwiks222@gmail.com|Sai Sathwik|Admin"
    "test@gmail.com|test|Developer"
    "mohanvishnu937@gmail.com|Vishnu Mohan|Admin"
    "ravikiran.ponduri@gmail.com|Ravi Kiran|Admin"
    "meghavardhanpc@gmail.com|Meghavardhan|Admin"
    "gokul.k.raj1436@gmail.com|Gokul Raj|Admin"
    "sgadepalli21@gmail.com|Sumanth|Admin"
    "gunapaneniaveenkumar@gmail.com|Naveen|DevOps"
)

echo "📋 Users to create: ${#USERS[@]}"
echo ""

SUCCESS_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

for user_data in "${USERS[@]}"; do
    IFS='|' read -r email name role <<< "$user_data"
    
    echo "-------------------------------------------"
    echo "Creating: $name ($email) - $role"
    
    # Check if user already exists
    EXISTING=$(docker exec -i worky-postgres psql -U postgres -d worky -t -c "SELECT email FROM users WHERE email = '$email';" 2>/dev/null | xargs)
    
    if [ -n "$EXISTING" ]; then
        echo "⏭️  User already exists, skipping..."
        ((SKIP_COUNT++))
        continue
    fi
    
    # Create user with default password
    if ./create_user.sh "$email" "$name" "$role" "password123" > /dev/null 2>&1; then
        echo "✅ Created successfully"
        ((SUCCESS_COUNT++))
    else
        echo "❌ Failed to create"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "=========================================="
echo "📊 Summary"
echo "=========================================="
echo "✅ Created: $SUCCESS_COUNT"
echo "⏭️  Skipped (already exist): $SKIP_COUNT"
echo "❌ Failed: $FAIL_COUNT"
echo ""

# Show all users in database
echo "📋 All users in database:"
docker exec -i worky-postgres psql -U postgres -d worky -c "SELECT id, email, full_name, role, is_active FROM users ORDER BY email;"

echo ""
echo "=========================================="
echo "🔐 Login Credentials"
echo "=========================================="
echo "All users created with password: password123"
echo ""
echo "⚠️  IMPORTANT: Clear browser cache after this!"
echo "   Press Ctrl + Shift + Delete"
echo "   Or use Incognito mode"
echo ""

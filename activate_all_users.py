#!/usr/bin/env python3
"""
Activate all users in the database to fix the inactive display issue
"""
import asyncio
import asyncpg

async def activate_all_users():
    """Activate all users in the database"""
    
    # Database connection details
    DB_HOST = "localhost"
    DB_PORT = 5437
    DB_NAME = "worky"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        print("✅ Connected to database")
        
        # Get all users and their current status
        users = await conn.fetch(
            "SELECT id, email, full_name, is_active FROM users ORDER BY email"
        )
        
        print(f"\n📋 Found {len(users)} users:")
        print("-" * 60)
        
        inactive_count = 0
        for user in users:
            status = "✅ Active" if user['is_active'] else "❌ Inactive"
            print(f"  {user['email']} ({user['full_name']}) - {status}")
            if not user['is_active']:
                inactive_count += 1
        
        if inactive_count > 0:
            print(f"\n⚠️ Found {inactive_count} inactive users. Activating all users...")
            
            # Activate all users
            result = await conn.execute(
                "UPDATE users SET is_active = TRUE, updated_at = NOW()"
            )
            
            print(f"✅ Updated {result.split()[-1]} users to active status")
        else:
            print("\n✅ All users are already active")
        
        # Verify the update
        print("\n🔍 Verifying user status after update:")
        print("-" * 60)
        
        users_after = await conn.fetch(
            "SELECT id, email, full_name, is_active FROM users ORDER BY email"
        )
        
        all_active = True
        for user in users_after:
            status = "✅ Active" if user['is_active'] else "❌ Inactive"
            print(f"  {user['email']} ({user['full_name']}) - {status}")
            if not user['is_active']:
                all_active = False
        
        await conn.close()
        print("\n✅ Database connection closed")
        
        if all_active:
            print("\n🎉 SUCCESS! All users are now active")
            print("The Users page should now show all users as active")
        else:
            print("\n❌ Some users are still inactive")
        
        # Test API response
        print("\n🧪 Testing API response...")
        await test_users_api()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

async def test_users_api():
    """Test the users API to see if it returns active users"""
    import requests
    
    API_BASE = "http://localhost:8007/api/v1"
    
    # Login first
    login_data = {
        "email": "admin@datalegos.com",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        result = response.json()
        token = result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get users from API
        response = requests.get(f"{API_BASE}/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ API returned {len(users)} users")
            
            active_count = sum(1 for user in users if user.get('is_active', False))
            print(f"   Active users: {active_count}/{len(users)}")
            
            if active_count == len(users):
                print("✅ All users are showing as active in API")
            else:
                print("⚠️ Some users still showing as inactive in API")
                
        else:
            print(f"❌ API request failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(activate_all_users())
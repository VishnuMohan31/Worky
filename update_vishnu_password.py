#!/usr/bin/env python3
"""
Update Vishnu's password to Vishnu54321$
"""
import asyncio
import asyncpg
import bcrypt

async def update_vishnu_password():
    """Update mohanvishnu937@gmail.com password"""
    
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
        
        # Check if Vishnu user exists
        result = await conn.fetchrow(
            "SELECT id, email, full_name, is_active FROM users WHERE email = $1",
            "mohanvishnu937@gmail.com"
        )
        
        if result:
            print(f"Found user: {result['full_name']} ({result['email']})")
            print(f"User ID: {result['id']}")
            print(f"Active: {result['is_active']}")
            
            # Hash the new password
            new_password = "Vishnu54321$"
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            # Update the password and ensure user is active
            await conn.execute(
                "UPDATE users SET hashed_password = $1, is_active = $2, updated_at = NOW() WHERE email = $3",
                hashed_password.decode('utf-8'),
                True,
                "mohanvishnu937@gmail.com"
            )
            
            print("✅ Password updated successfully!")
            print(f"New password: {new_password}")
            
        else:
            print("❌ mohanvishnu937@gmail.com user not found in database")
        
        await conn.close()
        print("✅ Database connection closed")
        
        # Test the login
        print("\n🧪 Testing new login credentials...")
        await test_login()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

async def test_login():
    """Test the login with new password"""
    import requests
    
    API_BASE = "http://localhost:8007/api/v1"
    
    login_data = {
        "email": "mohanvishnu937@gmail.com",
        "password": "Vishnu54321$"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        print(f"Login test status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! mohanvishnu937@gmail.com / Vishnu54321$ login works!")
            result = response.json()
            user_info = result.get('user', {})
            print(f"   User: {user_info.get('full_name', 'N/A')}")
            print(f"   Role: {user_info.get('role', 'N/A')}")
            print(f"   Access token: {result['access_token'][:30]}...")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(update_vishnu_password())
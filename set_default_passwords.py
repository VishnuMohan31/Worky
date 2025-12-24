#!/usr/bin/env python3
"""
Set default passwords for users that don't have working passwords
"""
import asyncio
import asyncpg
import bcrypt

async def set_default_passwords():
    """Set default passwords for users"""
    
    # Database connection details
    DB_HOST = "localhost"
    DB_PORT = 5437
    DB_NAME = "worky"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    
    # Users that need password updates
    users_to_update = [
        {"email": "abc@gmail.com", "password": "password"},
        {"email": "hello@gmail.com", "password": "password"},
        {"email": "jane@datalegos.com", "password": "password"},
        {"email": "john@datalegos.com", "password": "password"},
        {"email": "testuser@example.com", "password": "password"}
    ]
    
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
        print("\n🔑 Setting default passwords for users...")
        print("-" * 50)
        
        for user_info in users_to_update:
            email = user_info["email"]
            password = user_info["password"]
            
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT id, full_name FROM users WHERE email = $1", email
            )
            
            if user:
                # Hash the password
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
                
                # Update password
                await conn.execute(
                    "UPDATE users SET hashed_password = $1, is_active = TRUE, updated_at = NOW() WHERE email = $2",
                    hashed_password.decode('utf-8'),
                    email
                )
                
                print(f"✅ {email} ({user['full_name']}) - Password: {password}")
            else:
                print(f"❌ {email} - User not found")
        
        await conn.close()
        print("\n✅ Database connection closed")
        
        # Test some of the updated passwords
        print("\n🧪 Testing updated passwords...")
        await test_updated_passwords()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

async def test_updated_passwords():
    """Test the updated passwords"""
    import requests
    
    API_BASE = "http://localhost:8007/api/v1"
    
    test_users = [
        {"email": "jane@datalegos.com", "password": "password"},
        {"email": "john@datalegos.com", "password": "password"},
        {"email": "abc@gmail.com", "password": "password"}
    ]
    
    print("-" * 50)
    for user in test_users:
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=user, timeout=5)
            if response.status_code == 200:
                result = response.json()
                user_info = result.get('user', {})
                print(f"✅ {user['email']} - Login successful ({user_info.get('full_name', 'N/A')})")
            else:
                print(f"❌ {user['email']} - Login failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {user['email']} - Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(set_default_passwords())
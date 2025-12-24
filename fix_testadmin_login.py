#!/usr/bin/env python3
"""
Fix testadmin@gmail.com login by directly updating the database
"""
import asyncio
import asyncpg
import bcrypt
import os

async def fix_testadmin_password():
    """Fix testadmin password directly in database"""
    
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
        
        # Check if testadmin user exists
        result = await conn.fetchrow(
            "SELECT id, email, full_name FROM users WHERE email = $1",
            "testadmin@gmail.com"
        )
        
        if result:
            print(f"Found testadmin user: {result['id']} - {result['full_name']}")
            
            # Hash the new password
            new_password = "testadmin@123"
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            # Update the password and activate the user
            await conn.execute(
                "UPDATE users SET hashed_password = $1, is_active = $2 WHERE email = $3",
                hashed_password.decode('utf-8'),
                True,
                "testadmin@gmail.com"
            )
            
            print("✅ Password updated and user activated successfully!")
            
        else:
            print("❌ testadmin@gmail.com user not found in database")
            
            # Get a client_id to create the user
            client_result = await conn.fetchrow("SELECT id FROM clients LIMIT 1")
            if not client_result:
                print("❌ No clients found in database")
                await conn.close()
                return
            
            client_id = client_result['id']
            print(f"Using client_id: {client_id}")
            
            # Hash the password
            new_password = "testadmin@123"
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            # Create the user
            await conn.execute("""
                INSERT INTO users (id, email, full_name, hashed_password, role, client_id, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
            """, 
                f"USR-{int(asyncio.get_event_loop().time() * 1000)}",
                "testadmin@gmail.com",
                "Test Admin",
                hashed_password.decode('utf-8'),
                "Admin",
                client_id,
                True
            )
            
            print("✅ testadmin@gmail.com user created successfully!")
        
        await conn.close()
        print("✅ Database connection closed")
        
        # Test the login
        print("\n🧪 Testing login...")
        await test_login()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        print("Make sure the database is running and accessible")

async def test_login():
    """Test the login with requests"""
    import requests
    
    API_BASE = "http://localhost:8007/api/v1"
    
    login_data = {
        "email": "testadmin@gmail.com",
        "password": "testadmin@123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        print(f"Login test status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! testadmin@gmail.com / testadmin@123 login now works!")
            result = response.json()
            print(f"Access token: {result['access_token'][:30]}...")
        else:
            print(f"❌ Login still failed: {response.text}")
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_testadmin_password())
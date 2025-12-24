#!/usr/bin/env python3
"""
Get all user credentials from the system
"""
import requests

API_BASE = "http://localhost:8007/api/v1"

def get_all_credentials():
    """Get all user credentials"""
    
    print("🔐 WORKY APPLICATION - ALL USER CREDENTIALS")
    print("=" * 60)
    
    # Login with admin to get all users
    login_data = {
        "email": "admin@datalegos.com",
        "password": "password"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.text}")
        return
    
    result = response.json()
    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users
    response = requests.get(f"{API_BASE}/users", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get users: {response.text}")
        return
    
    users = response.json()
    
    print(f"\n📋 TOTAL USERS: {len(users)}")
    print("-" * 60)
    
    # Known working credentials
    working_credentials = [
        {
            "email": "admin@datalegos.com",
            "password": "password",
            "name": "Admin User",
            "role": "Admin",
            "status": "✅ VERIFIED WORKING"
        },
        {
            "email": "testadmin@gmail.com", 
            "password": "testadmin@123",
            "name": "Test Admin",
            "role": "Admin", 
            "status": "✅ VERIFIED WORKING"
        }
    ]
    
    # Common passwords to try for other users
    common_passwords = ["password", "123456", "admin123", "user123", "test123"]
    
    print("\n🎯 VERIFIED WORKING CREDENTIALS:")
    print("-" * 40)
    for cred in working_credentials:
        print(f"📧 Email: {cred['email']}")
        print(f"🔑 Password: {cred['password']}")
        print(f"👤 Name: {cred['name']}")
        print(f"🏷️ Role: {cred['role']}")
        print(f"✅ Status: {cred['status']}")
        print()
    
    print("\n👥 ALL USERS IN SYSTEM:")
    print("-" * 40)
    for i, user in enumerate(users, 1):
        print(f"{i}. 📧 {user['email']}")
        print(f"   👤 {user['full_name']}")
        print(f"   🏷️ {user.get('role', 'N/A')}")
        print(f"   📊 Active: {user.get('is_active', 'N/A')}")
        
        # Try to determine password for known users
        if user['email'] in ['admin@datalegos.com', 'testadmin@gmail.com']:
            for cred in working_credentials:
                if cred['email'] == user['email']:
                    print(f"   🔑 Password: {cred['password']} ✅")
                    break
        else:
            print(f"   🔑 Password: Unknown (try common passwords)")
        print()
    
    print("\n🔧 SYSTEM ACCESS INFORMATION:")
    print("-" * 40)
    print(f"🌐 Application URL: http://localhost:3007")
    print(f"🔌 API URL: http://localhost:8007")
    print(f"📊 Database: PostgreSQL on localhost:5437")
    print(f"   - Database Name: worky")
    print(f"   - Username: postgres") 
    print(f"   - Password: postgres")
    
    print(f"\n💡 RECOMMENDED LOGIN:")
    print("-" * 40)
    print(f"Use either of these verified credentials:")
    print(f"1. admin@datalegos.com / password")
    print(f"2. testadmin@gmail.com / testadmin@123")
    
    print(f"\n🚀 FEATURES AVAILABLE:")
    print("-" * 40)
    print(f"✅ Multiple Assignment System (FIXED)")
    print(f"✅ Team Management")
    print(f"✅ Decision Tracking System") 
    print(f"✅ Project Hierarchy Management")
    print(f"✅ User Management")
    print(f"✅ Client Management")
    
    # Test other users with common passwords
    print(f"\n🔍 TESTING OTHER USER PASSWORDS:")
    print("-" * 40)
    
    for user in users:
        if user['email'] not in ['admin@datalegos.com', 'testadmin@gmail.com']:
            print(f"\n📧 Testing {user['email']} ({user['full_name']}):")
            
            for password in common_passwords:
                test_login = {
                    "email": user['email'],
                    "password": password
                }
                
                try:
                    response = requests.post(f"{API_BASE}/auth/login", json=test_login, timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ Password found: {password}")
                        break
                    elif response.status_code == 400 and "Inactive user" in response.text:
                        print(f"   ⚠️ User is inactive (password might be: {password})")
                        break
                except:
                    pass
            else:
                print(f"   ❌ No common password worked")

if __name__ == "__main__":
    get_all_credentials()
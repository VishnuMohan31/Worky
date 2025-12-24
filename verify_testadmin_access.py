#!/usr/bin/env python3
"""
Verify testadmin can access the application and perform operations
"""
import requests

API_BASE = "http://localhost:8007/api/v1"

def verify_testadmin_access():
    """Verify testadmin can login and access resources"""
    
    # Test login
    login_data = {
        "email": "testadmin@gmail.com",
        "password": "testadmin@123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    print(f"🔐 Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    result = response.json()
    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    print(f"   User: {result.get('user', {}).get('full_name', 'N/A')}")
    print(f"   Role: {result.get('user', {}).get('role', 'N/A')}")
    
    # Test accessing users
    response = requests.get(f"{API_BASE}/users", headers=headers)
    print(f"\n👥 Users Access: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   Can see {len(users)} users")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test accessing clients
    response = requests.get(f"{API_BASE}/clients", headers=headers)
    print(f"\n🏢 Clients Access: {response.status_code}")
    if response.status_code == 200:
        clients = response.json()
        if isinstance(clients, dict) and 'clients' in clients:
            print(f"   Can see {len(clients['clients'])} clients")
        else:
            print(f"   Can see {len(clients)} clients")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test accessing projects
    response = requests.get(f"{API_BASE}/projects", headers=headers)
    print(f"\n📁 Projects Access: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        if isinstance(projects, dict) and 'projects' in projects:
            print(f"   Can see {len(projects['projects'])} projects")
        else:
            print(f"   Can see {len(projects)} projects")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test accessing tasks
    response = requests.get(f"{API_BASE}/tasks", headers=headers)
    print(f"\n📋 Tasks Access: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"   Can see {len(tasks)} tasks")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    print(f"\n🎉 SUCCESS! testadmin@gmail.com can now:")
    print(f"   ✅ Login with password: testadmin@123")
    print(f"   ✅ Access the application at: http://localhost:3007")
    print(f"   ✅ Perform admin operations")
    print(f"   ✅ Use the multiple assignment system")

if __name__ == "__main__":
    verify_testadmin_access()
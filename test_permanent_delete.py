#!/usr/bin/env python3
"""
Test permanent delete functionality
"""
import requests
import time

def test_permanent_delete():
    time.sleep(3)  # Wait for API to start
    
    # Login as admin
    login = requests.post('http://localhost:8007/api/v1/auth/login', json={'email':'admin@datalegos.com','password':'password'})
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create a test user
    create_data = {
        'full_name': 'Permanent Delete Test',
        'email': 'permdeletetest@example.com',
        'role': 'Developer',
        'password': 'password123',
        'client_id': 'CLI-001',
        'language': 'en',
        'theme': 'snow'
    }

    create_response = requests.post('http://localhost:8007/api/v1/users', json=create_data, headers=headers)
    if create_response.status_code == 201:
        user = create_response.json()
        print(f'✅ Created test user: {user["id"]} - {user["email"]}')
        
        # Delete the user permanently
        delete_response = requests.delete(f'http://localhost:8007/api/v1/users/{user["id"]}', headers=headers)
        print(f'Delete response: {delete_response.status_code}')
        
        if delete_response.status_code == 204:
            print('✅ Delete API call successful')
            
            # Try to get the user - should return 404
            check_response = requests.get(f'http://localhost:8007/api/v1/users/{user["id"]}', headers=headers)
            print(f'Get deleted user response: {check_response.status_code}')
            
            if check_response.status_code == 404:
                print('✅ User permanently deleted - cannot be retrieved')
            else:
                print(f'❌ User still exists: {check_response.json()}')
                
            # Check users list
            users_response = requests.get('http://localhost:8007/api/v1/users', headers=headers)
            users = users_response.json()
            deleted_user_in_list = any(u['id'] == user['id'] for u in users)
            
            if not deleted_user_in_list:
                print('✅ User not in users list - permanently removed')
            else:
                print('❌ User still appears in users list')
        else:
            print(f'❌ Delete failed: {delete_response.text}')
    else:
        print(f'❌ Failed to create test user: {create_response.text}')

if __name__ == "__main__":
    test_permanent_delete()
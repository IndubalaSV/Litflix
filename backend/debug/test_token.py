#!/usr/bin/env python3
"""
Test to verify token authentication
"""

import requests
import json

def test_token_auth():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing token authentication...")
    
    # Step 1: Register a user
    register_data = {
        "username": "testuser456",
        "email": "test456@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"📝 Registration: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"✅ Got token: {token[:20]}...")
            
            # Step 2: Test protected endpoint with token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/api/saved/list", headers=headers)
            print(f"🔒 Protected endpoint: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Token authentication working!")
                return True
            else:
                print(f"❌ Protected endpoint failed: {response.text}")
                return False
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_token_auth() 
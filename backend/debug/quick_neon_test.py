#!/usr/bin/env python3
"""
Quick test to check Neon database state
"""

import requests
import json

def quick_test():
    base_url = "http://localhost:8000"
    
    print("🔍 Quick Neon Database Test")
    print("=" * 30)
    
    # Test 1: Register a user
    print("1. Testing user registration...")
    user_data = {
        "username": "test_user_456",
        "email": "test456@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=user_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"   ✅ Got token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test 2: Save preferences
            print("\n2. Testing preferences save...")
            prefs = {
                "movie_name": "Test Movie",
                "book_name": "Test Book",
                "age": "25_to_29",
                "gender": "male"
            }
            
            response = requests.post(f"{base_url}/api/auth/preferences", json=prefs, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Test 3: Save an item
            print("\n3. Testing item save...")
            item = {
                "item_id": "test_item_123",
                "item_name": "Test Item",
                "item_type": "book",
                "item_image": "https://example.com/test.jpg",
                "item_description": "Test description"
            }
            
            response = requests.post(f"{base_url}/api/saved/save", json=item, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Test 4: Get saved items
            print("\n4. Testing get saved items...")
            response = requests.get(f"{base_url}/api/saved/list", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
        else:
            print(f"   ❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    quick_test() 
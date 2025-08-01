#!/usr/bin/env python3
"""
Comprehensive test for Neon database integration
Tests user preferences and saved items functionality
"""

import requests
import json
import time

def test_neon_integration():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Neon Database Integration...")
    print("=" * 50)
    
    # Test user credentials
    test_user = {
        "username": "neon_test_user",
        "email": "neon_test@example.com",
        "password": "password123"
    }
    
    token = None
    
    try:
        # Step 1: Register user
        print("📝 Step 1: Registering user...")
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        print(f"   Registration status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"   ✅ Got token: {token[:20]}...")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Test user preferences
        print("\n📊 Step 2: Testing user preferences...")
        test_preferences = {
            "movie_name": "The Matrix",
            "book_name": "1984",
            "place_name": "New York",
            "age": "25_to_29",
            "gender": "male"
        }
        
        # Save preferences
        response = requests.post(f"{base_url}/api/auth/preferences", 
                               json=test_preferences, headers=headers)
        print(f"   Save preferences status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Preferences saved successfully")
        else:
            print(f"   ❌ Failed to save preferences: {response.text}")
            return False
        
        # Get preferences
        response = requests.get(f"{base_url}/api/auth/preferences", headers=headers)
        print(f"   Get preferences status: {response.status_code}")
        
        if response.status_code == 200:
            saved_prefs = response.json()
            print(f"   ✅ Retrieved preferences: {saved_prefs}")
        else:
            print(f"   ❌ Failed to get preferences: {response.text}")
            return False
        
        # Step 3: Test saved items
        print("\n📚 Step 3: Testing saved items...")
        
        # Save a book
        test_book = {
            "item_id": "book_123",
            "item_name": "The Great Gatsby",
            "item_type": "book",
            "item_image": "https://example.com/gatsby.jpg",
            "item_description": "A classic American novel"
        }
        
        response = requests.post(f"{base_url}/api/saved/save", 
                               json=test_book, headers=headers)
        print(f"   Save book status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Book saved successfully")
        else:
            print(f"   ❌ Failed to save book: {response.text}")
            return False
        
        # Save a movie
        test_movie = {
            "item_id": "movie_456",
            "item_name": "Inception",
            "item_type": "movie",
            "item_image": "https://example.com/inception.jpg",
            "item_description": "A mind-bending thriller"
        }
        
        response = requests.post(f"{base_url}/api/saved/save", 
                               json=test_movie, headers=headers)
        print(f"   Save movie status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Movie saved successfully")
        else:
            print(f"   ❌ Failed to save movie: {response.text}")
            return False
        
        # Get all saved items
        response = requests.get(f"{base_url}/api/saved/list", headers=headers)
        print(f"   Get saved items status: {response.status_code}")
        
        if response.status_code == 200:
            saved_items = response.json()
            print(f"   ✅ Retrieved {len(saved_items)} saved items:")
            for item in saved_items:
                print(f"      - {item['item_name']} ({item['item_type']})")
        else:
            print(f"   ❌ Failed to get saved items: {response.text}")
            return False
        
        # Check if specific item is saved
        response = requests.get(f"{base_url}/api/saved/check/book_123", headers=headers)
        print(f"   Check book status: {response.status_code}")
        
        if response.status_code == 200:
            check_result = response.json()
            print(f"   ✅ Book check result: {check_result}")
        else:
            print(f"   ❌ Failed to check book: {response.text}")
            return False
        
        # Step 4: Test recommendations with preferences
        print("\n🎯 Step 4: Testing recommendations with saved preferences...")
        
        response = requests.post(f"{base_url}/api/recommendations", 
                               json=test_preferences, headers=headers)
        print(f"   Recommendations status: {response.status_code}")
        
        if response.status_code == 200:
            recommendations = response.json()
            print("   ✅ Got recommendations:")
            if 'movies' in recommendations and recommendations['movies']:
                print(f"      - {len(recommendations['movies'])} movies")
            if 'books' in recommendations and recommendations['books']:
                print(f"      - {len(recommendations['books'])} books")
            if 'tv_shows' in recommendations and recommendations['tv_shows']:
                print(f"      - {len(recommendations['tv_shows'])} TV shows")
            if 'popular_books' in recommendations and recommendations['popular_books']:
                print(f"      - {len(recommendations['popular_books'])} popular books")
        else:
            print(f"   ❌ Failed to get recommendations: {response.text}")
            return False
        
        print("\n🎉 All tests passed! Neon integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_neon_integration()
    if success:
        print("\n✅ Neon Database Integration: SUCCESS")
    else:
        print("\n❌ Neon Database Integration: FAILED") 
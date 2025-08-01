#!/usr/bin/env python3
"""
Test to verify frontend can access images from API response
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_frontend_images():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Frontend Image Access")
    print("=" * 40)
    
    # Test getting recommendations and check image fields
    print("1. Getting recommendations...")
    
    try:
        response = requests.post(f"{base_url}/api/recommendations", json={
            "book_name": "Lolita",
            "age": "24_and_younger",
            "gender": "female"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Got recommendations")
            
            # Check each category for images
            categories = ['book_recs', 'popular_books', 'movie_recs', 'tv_show_recs']
            
            for category in categories:
                if category in data and data[category]:
                    print(f"\n2. Checking {category}...")
                    first_item = data[category][0]
                    
                    # Check for image fields
                    image_url = None
                    
                    # Check direct fields
                    if 'image_url' in first_item:
                        image_url = first_item['image_url']
                        print(f"   ✅ Found image_url: {image_url}")
                    elif 'cover_image' in first_item:
                        image_url = first_item['cover_image']
                        print(f"   ✅ Found cover_image: {image_url}")
                    elif 'properties' in first_item and 'image' in first_item['properties']:
                        image_url = first_item['properties']['image'].get('url')
                        print(f"   ✅ Found properties.image.url: {image_url}")
                    else:
                        print(f"   ❌ No image found in {category}")
                        print(f"   Available fields: {list(first_item.keys())}")
                        if 'properties' in first_item:
                            print(f"   Properties fields: {list(first_item['properties'].keys())}")
                    
                    if image_url:
                        print(f"   📸 Image URL: {image_url}")
                        
                        # Test if image URL is accessible
                        try:
                            img_response = requests.head(image_url, timeout=5)
                            if img_response.status_code == 200:
                                print(f"   ✅ Image URL is accessible")
                            else:
                                print(f"   ⚠️ Image URL returned status: {img_response.status_code}")
                        except Exception as e:
                            print(f"   ⚠️ Could not test image URL: {e}")
                    
                    break  # Only check first category with data
        else:
            print(f"   ❌ Failed to get recommendations: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_images() 
#!/usr/bin/env python3
"""
Test to see the actual API response structure
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_response():
    QLOO_API_BASE = "https://hackathon.api.qloo.com"
    QLOO_API_KEY = os.getenv("QLOO_API_KEY")
    HEADERS = {
        "accept": "application/json",
        "x-api-key": QLOO_API_KEY
    }
    
    print("🔍 Testing Qloo API Response Structure")
    print("=" * 50)
    
    # Test 1: Get entity ID for a book
    print("1. Getting entity ID for 'Lolita'...")
    try:
        response = requests.get(
            f"{QLOO_API_BASE}/search",
            params={"query": "Lolita", "types": "urn:entity:book"},
            headers=HEADERS
        )
        
        if response.ok:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Response structure: {json.dumps(data, indent=2)[:500]}...")
            
            # Get the first entity ID
            entity_id = None
            if 'results' in data and len(data['results']) > 0:
                entity_id = data['results'][0].get('entity_id')
            elif isinstance(data, list) and len(data) > 0:
                entity_id = data[0].get('entity_id')
            
            if entity_id:
                print(f"   ✅ Got entity ID: {entity_id}")
                
                # Test 2: Get insights for books
                print(f"\n2. Getting book insights for entity ID: {entity_id}")
                
                params = {
                    "filter.type": "urn:entity:book",
                    "signal.interests.entities": entity_id,
                    "signal.demographics.age": "24_and_younger",
                    "signal.demographics.gender": "female",
                    "feature.explainability": "true",
                    "take": "3"
                }
                
                response = requests.get(
                    f"{QLOO_API_BASE}/v2/insights",
                    params=params,
                    headers=HEADERS
                )
                
                if response.ok:
                    data = response.json()
                    print(f"   Status: {response.status_code}")
                    
                    # Extract entities
                    entities = []
                    if 'results' in data and 'entities' in data['results']:
                        entities = data['results']['entities']
                    elif 'entities' in data:
                        entities = data['entities']
                    elif isinstance(data, list):
                        entities = data
                    
                    if entities:
                        print(f"   ✅ Got {len(entities)} entities")
                        print(f"   First entity structure:")
                        first_entity = entities[0]
                        print(f"   {json.dumps(first_entity, indent=2)}")
                        
                        # Check for image fields
                        print(f"\n3. Checking for image fields in first entity:")
                        image_fields = []
                        for key, value in first_entity.items():
                            if 'image' in key.lower() or 'cover' in key.lower() or 'url' in key.lower():
                                image_fields.append((key, value))
                        
                        if image_fields:
                            print(f"   ✅ Found image fields:")
                            for field, value in image_fields:
                                print(f"      {field}: {value}")
                        else:
                            print(f"   ❌ No obvious image fields found")
                            print(f"   All fields: {list(first_entity.keys())}")
                    else:
                        print(f"   ❌ No entities found in response")
                else:
                    print(f"   ❌ Insights request failed: {response.status_code}")
                    print(f"   {response.text}")
            else:
                print(f"   ❌ No entity ID found")
        else:
            print(f"   ❌ Search request failed: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_response() 
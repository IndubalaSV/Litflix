#!/usr/bin/env python3
"""
Simple test script for Gemini integration
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test if Gemini API is working"""
    try:
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("Please add your Gemini API key to the .env file")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try different model names
        model = None
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ Using gemini-1.5-pro model")
        except Exception as e:
            try:
                model = genai.GenerativeModel('gemini-pro')
                print("✅ Using gemini-pro model")
            except Exception as e2:
                print(f"❌ Failed to initialize any Gemini model: {e2}")
                return False
        
        # Simple test
        response = model.generate_content("Say 'Hello from Gemini!'")
        print(f"✅ Gemini API is working!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_natural_language_conversion():
    """Test natural language to entity conversion"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try different model names
        model = None
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            try:
                model = genai.GenerativeModel('gemini-pro')
            except Exception as e2:
                print(f"❌ Failed to initialize any Gemini model: {e2}")
                return False
        
        # Test query
        query = "I loved a movie about finance and ambition in New York"
        entity_type = "movie"
        
        prompt = f"""
        You are a helpful assistant that converts natural language descriptions into specific entity names.
        
        Given a description and entity type, return the most likely specific entity name.
        
        Entity Type: {entity_type}
        Description: {query}
        
        Rules:
        1. Return ONLY a JSON object with these fields:
           - entity_name: The specific name of the entity
           - entity_type: The entity type (should match the input)
           - confidence: A number between 0 and 1 indicating your confidence
           - explanation: A brief explanation of why you chose this entity
        
        2. For movies, return the exact movie title
        3. For books, return the exact book title
        4. For TV shows, return the exact show title
        5. If you're not confident, set confidence to 0.3 or lower
        6. If you can't find a good match, set success to false
        
        Examples:
        - "I loved a movie about finance and ambition in New York" -> {{"entity_name": "The Wolf of Wall Street", "entity_type": "movie", "confidence": 0.9, "explanation": "This matches the description of a movie about finance and ambition set in New York"}}
        - "A book about a wizard school" -> {{"entity_name": "Harry Potter and the Sorcerer's Stone", "entity_type": "book", "confidence": 0.8, "explanation": "This is the first book in the Harry Potter series about a wizard school"}}
        - "A TV show about friends in New York" -> {{"entity_name": "Friends", "entity_type": "tv_show", "confidence": 0.9, "explanation": "This matches the description of a popular TV show about friends living in New York"}}
        
        Return only the JSON object, no other text.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        print(f"✅ Natural language conversion test successful!")
        print(f"Query: '{query}'")
        print(f"Result: {json.dumps(result, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ Natural language conversion test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini Integration...")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1. Testing Gemini API connection...")
    connection_ok = test_gemini_connection()
    
    # Test 2: Natural language conversion
    if connection_ok:
        print("\n2. Testing natural language conversion...")
        conversion_ok = test_natural_language_conversion()
        
        if conversion_ok:
            print("\n🎉 All tests passed! Gemini integration is working correctly.")
        else:
            print("\n❌ Natural language conversion test failed.")
    else:
        print("\n❌ Gemini API connection failed. Please check your API key.")
    
    print("\n" + "=" * 50) 
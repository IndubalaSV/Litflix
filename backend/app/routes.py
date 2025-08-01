# app/routes.py
import requests
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from app.auth import get_current_user
from app.database import UserPreference, get_db

async def get_current_user_optional():
    try:
        return await get_current_user()
    except:
        return None

# Load environment variables
load_dotenv()

recommendation_router = APIRouter()

QLOO_API_BASE = "https://hackathon.api.qloo.com"
QLOO_API_KEY = os.getenv("QLOO_API_KEY")
HEADERS = {
    "accept": "application/json",
    "x-api-key": QLOO_API_KEY
}

class PreferenceInput(BaseModel):
    book_name: Optional[str] = None
    movie_name: Optional[str] = None
    place_name: Optional[str] = None
    age: Optional[str] = None  # Must match one of the accepted enums when provided
    gender: Optional[str] = None  # "male" or "female" when provided

class SearchInput(BaseModel):
    query: str
    entity_type: str  # "book", "movie", "tv_show", "place"


def fetch_entity_id(name: str, entity_type: str) -> Optional[str]:
    try:
        response = requests.get(
            f"{QLOO_API_BASE}/search",
            params={"query": name, "types": f"urn:entity:{entity_type}"},
            headers=HEADERS
        )
        
        if response.ok:
            data = response.json()
            # Check if the response has 'results' key (new format)
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0].get('entity_id')
            # Check if the response is a direct array (old format)
            elif isinstance(data, list) and len(data) > 0 and "entity_id" in data[0]:
                return data[0]["entity_id"]
        
        return None
    except Exception:
        return None


def get_insights(entity_ids: list[str], age: str, gender: str, domain: str) -> list:
    joined_ids = ",".join(entity_ids)
    
    # Debug: Log the API call parameters
    print(f"🔍 Qloo API call for {domain}:")
    print(f"   - Entity IDs: {entity_ids}")
    print(f"   - Joined IDs: {joined_ids}")
    print(f"   - Age: {age}, Gender: {gender}")
    
    try:
        params = {
            "filter.type": f"urn:entity:{domain}",
            "signal.interests.entities": joined_ids,
            "signal.demographics.age": age,
            "signal.demographics.gender": gender,
            "feature.explainability": "true",
            "take": "10"
        }
        
        print(f"   - Full URL params: {params}")
        
        response = requests.get(
            f"{QLOO_API_BASE}/v2/insights",
            params=params,
            headers=HEADERS
        )
        
        if response.ok:
            data = response.json()
            # Handle the nested structure: {success: true, results: {entities: [...]}}
            if 'results' in data and 'entities' in data['results']:
                return data['results']['entities']
            # Fallback for other response formats
            elif 'entities' in data:
                return data['entities']
            elif isinstance(data, list):
                return data
        
        return []
    except Exception:
        return []


def get_popular_books(entity_ids: list[str], age: str, gender: str) -> list:
    # For best sellers, we'll get general popular books without user-specific signals
    try:
        params = {
            "filter.type": "urn:entity:book",
            "filter.popularity.min": "0.95",
            "feature.explainability": "true",
            "take": "10"
        }
        
        
        response = requests.get(
            f"{QLOO_API_BASE}/v2/insights",
            params=params,
            headers=HEADERS
        )
        
        if response.ok:
            data = response.json()
            # Handle the nested structure: {success: true, results: {entities: [...]}}
            if 'results' in data and 'entities' in data['results']:
                return data['results']['entities']
            # Fallback for other response formats
            elif 'entities' in data:
                return data['entities']
            elif isinstance(data, list):
                return data
        
        return []
    except Exception:
        return []


@recommendation_router.post("/search")
async def search_entities(search_input: SearchInput):
    """Search for entities by name and type"""
    try:
        # try to get the entity ID
        entity_id = fetch_entity_id(search_input.query, search_input.entity_type)
        
        if entity_id:
            # Get details for the found entity
            params = {
                "filter.type": f"urn:entity:{search_input.entity_type}",
                "filter.entity_id": entity_id,
                "feature.explainability": "true",
                "take": "1"
            }
            
            response = requests.get(
                f"{QLOO_API_BASE}/v2/insights",
                params=params,
                headers=HEADERS
            )
            
            if response.ok:
                data = response.json()
                entities = []
                if 'results' in data and 'entities' in data['results']:
                    entities = data['results']['entities']
                elif 'entities' in data:
                    entities = data['entities']
                elif isinstance(data, list):
                    entities = data
                
                return {"results": entities}
        
        # If no entity found, try direct search
        try:
            response = requests.get(
                f"{QLOO_API_BASE}/search",
                params={"query": search_input.query, "types": f"urn:entity:{search_input.entity_type}"},
                headers=HEADERS
            )
            
            if response.ok:
                data = response.json()
                # Convert search results to entity format
                if 'results' in data and len(data['results']) > 0:
                     entities = []
                     for result in data['results'][:5]:  # Limit to 5 results
                         entity_id = result.get('entity_id')
                         
                         # Get full details from insights API if we have an entity_id
                         full_details = None
                         if entity_id:
                             try:
                                 insights_response = requests.get(
                                     f"{QLOO_API_BASE}/v2/insights",
                                     params={
                                         "filter.type": f"urn:entity:{search_input.entity_type}",
                                         "filter.entity_id": entity_id,
                                         "feature.explainability": "true",
                                         "take": "1"
                                     },
                                     headers=HEADERS
                                 )
                                 
                                 if insights_response.ok:
                                     insights_data = insights_response.json()
                                     if 'results' in insights_data and 'entities' in insights_data['results'] and len(insights_data['results']['entities']) > 0:
                                         full_details = insights_data['results']['entities'][0]
                                     elif 'entities' in insights_data and len(insights_data['entities']) > 0:
                                         full_details = insights_data['entities'][0]
                             except Exception as e:
                                 print(f"Failed to get insights for {entity_id}: {e}")
                         
                         # Use full details if available, otherwise use search result
                         details = full_details if full_details else result
                         
                         # Debug: Log what we got
                         if full_details:
                             print(f"✅ Got full details for {details.get('name')}: {details.get('short_description', 'No description')[:100]}...")
                         else:
                             print(f"⚠️ Using basic search result for {result.get('name')}")
                         
                         # Try to get image from various possible fields
                         image_url = (
                             details.get('image_url') or 
                             details.get('image') or 
                             details.get('cover_image') or
                             (details.get('properties', {}).get('image', {}).get('url') if details.get('properties') else None)
                         )
                         
                         entity = {
                             "entity_id": details.get('entity_id'),
                             "name": details.get('name', search_input.query),
                             "type": search_input.entity_type,
                             "image": image_url,
                             "image_url": image_url,  # Add both for compatibility
                             "rating": details.get('rating'),
                             "rating_count": details.get('rating_count'),
                             "author": details.get('author'),
                             "properties": {
                                 "short_description": details.get('short_description') or details.get('properties', {}).get('short_description'),
                                 "description": details.get('description') or details.get('properties', {}).get('description'),
                                 "publication_year": details.get('publication_year') or details.get('properties', {}).get('publication_year'),
                                 "publication_date": details.get('publication_date') or details.get('properties', {}).get('publication_date'),
                                 "genre": details.get('genre') or details.get('properties', {}).get('genre'),
                                 "page_count": details.get('page_count') or details.get('properties', {}).get('page_count'),
                                 "language": details.get('language') or details.get('properties', {}).get('language'),
                                 "publisher": details.get('publisher') or details.get('properties', {}).get('publisher'),
                                 "isbn13": details.get('isbn13') or details.get('properties', {}).get('isbn13'),
                                 "format": details.get('format') or details.get('properties', {}).get('format'),
                                 "image": {
                                     "url": image_url
                                 } if image_url else None
                             },
                             "external": {
                                 "goodreads": details.get('goodreads_id') or details.get('external', {}).get('goodreads')
                             } if (details.get('goodreads_id') or details.get('external', {}).get('goodreads')) else None
                         }
                         entities.append(entity)
                     return {"results": entities}
        
        except Exception as search_error:
            print(f"Direct search failed: {search_error}")
        
        return {"results": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@recommendation_router.post("/recommendations")
async def get_recommendations(preference: PreferenceInput, current_user: Optional[dict] = Depends(get_current_user_optional)):
    # Get user preferences and favorites from database if user is authenticated
    user_preferences = {}
    favorite_entities = []
    
    if current_user:
        from app.database import SessionLocal, SavedItem
        db = SessionLocal()
        try:
            # Get user preferences
            user_pref = db.query(UserPreference).filter(UserPreference.user_id == current_user["id"]).first()
            if user_pref:
                user_preferences = {
                    "book_name": user_pref.book_name,
                    "movie_name": user_pref.movie_name,
                    "place_name": user_pref.place_name,
                    "age": user_pref.age,
                    "gender": user_pref.gender
                }
            
            # Get user's favorite items (saved items with favorited=True)
            print(f"🔍 Querying for favorited items for user {current_user['id']}")
            
            # First, let's see all saved items for this user
            all_saved_items = db.query(SavedItem).filter(SavedItem.user_id == current_user["id"]).all()
            print(f"Total saved items for user: {len(all_saved_items)}")
            for item in all_saved_items:
                print(f"  - {item.item_name} (ID: {item.item_id}, Favorited: {item.favorited}, Type: {type(item.favorited)})")
            
            # Now get only favorited items
            saved_items = db.query(SavedItem).filter(
                SavedItem.user_id == current_user["id"],
                SavedItem.favorited == True
            ).all()
            favorite_entities = [item.item_id for item in saved_items if item.item_id]
            
            print(f"🔍 Favorited items query result: {len(saved_items)} items")
            for item in saved_items:
                print(f"  - FAVORITED: {item.item_name} (ID: {item.item_id}, Favorited: {item.favorited})")
            
            # Debug: Log favorited items
            print(f"Found {len(saved_items)} favorited items for user {current_user['id']}")
            print(f"Raw saved_items: {[(item.item_name, item.item_id, item.favorited) for item in saved_items]}")
            for item in saved_items:
                print(f"  - {item.item_name} (ID: {item.item_id}, Type: {item.item_type}, Favorited: {item.favorited})")
            print(f"Extracted favorite_entities: {favorite_entities}")
            
        finally:
            db.close()
    
    # Use fallback values if none provided
    fallback_preference = {
        "book_name": "Lolita",
        "movie_name": "The Wolf of Wall Street",
        "place_name": "Paris",
        "age": "24_and_younger",
        "gender": "female"
    }
    
    # Use provided values, then user preferences, then fallback to defaults
    book_name = preference.book_name or user_preferences.get("book_name") or fallback_preference["book_name"]
    movie_name = preference.movie_name or user_preferences.get("movie_name") or fallback_preference["movie_name"]
    place_name = preference.place_name or user_preferences.get("place_name") or fallback_preference["place_name"]
    age = preference.age or user_preferences.get("age") or fallback_preference["age"]
    gender = preference.gender or user_preferences.get("gender") or fallback_preference["gender"]
    
    entity_ids = []

    # Use main preferences for recommendations
    if book_name:
        book_id = fetch_entity_id(book_name, "book")
        if book_id:
            entity_ids.append(book_id)

    if movie_name:
        movie_id = fetch_entity_id(movie_name, "movie")
        if movie_id:
            entity_ids.append(movie_id)

    if place_name:
        place_id = fetch_entity_id(place_name, "place")
        if place_id:
            entity_ids.append(place_id)

    # Add favorites as additional signals (not just fallback)
    print(f"Before adding favorites: entity_ids = {entity_ids}")
    if favorite_entities:
        print(f"Adding favorites: {favorite_entities}")
        entity_ids.extend(favorite_entities)
        print(f"After adding favorites: entity_ids = {entity_ids}")
    else:
        print("No favorites to add")

    if not entity_ids:
        raise HTTPException(status_code=400, detail="No valid entity IDs found.")

    # Debug: Log what entity IDs are being used
    print(f"Using entity IDs for recommendations: {entity_ids}")
    print(f"Main preferences: book={book_name}, movie={movie_name}, place={place_name}")
    print(f"Favorites count: {len(favorite_entities)}")
    print(f"Favorites: {favorite_entities}")
    print(f"Main preference IDs: {[id for id in entity_ids if id not in favorite_entities]}")

    # Get insights for each content type using fallback values if needed
    book_recs = get_insights(entity_ids, age, gender, "book")
    popular_books = get_popular_books(entity_ids, age, gender)
    movie_recs = get_insights(entity_ids, age, gender, "movie")
    tv_show_recs = get_insights(entity_ids, age, gender, "tv_show")

    return {
        "book_recs": book_recs,
        "popular_books": popular_books,
        "movie_recs": movie_recs,
        "tv_show_recs": tv_show_recs
    }


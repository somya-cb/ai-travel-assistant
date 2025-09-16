# hotel_service.py

import re
from couchbase.search import MatchQuery, ConjunctionQuery, SearchRequest
from couchbase_connection import get_cluster, get_hotels_collection, config

# Get shared connections
cluster = get_cluster()
collection = get_hotels_collection()

def search_hotels(city, country, limit=10):
    """Search hotels using FTS index"""
    try:
        city_query = MatchQuery(city, field="cityName")
        country_query = MatchQuery(country, field="countyName")  
        fts_query = ConjunctionQuery(city_query, country_query)

        search_req = SearchRequest.create(fts_query)
        search_req.limit = limit

        index_name = config["fts_index_name"]
        results = cluster.search(index_name, search_req)

        return [row.id for row in results]

    except Exception as e:
        print(f"FTS hotel search failed: {e}")
        return []

def format_hotel_for_display(doc_id):
    """Fetch hotel doc by ID and format it for display"""
    try:
        result = collection.get(doc_id)
        hotel = result.content_as[dict]

        # Parse coordinates
        coordinates = hotel.get("Map", "").split("|")
        lat, lon = "", ""
        if len(coordinates) == 2:
            try:
                lat, lon = float(coordinates[0]), float(coordinates[1])
            except ValueError:
                lat, lon = "", ""

        # Clean description
        description = re.sub('<.*?>', '', hotel.get("Description", "")).replace('\\n', ' ').strip()
        if len(description) > 300:
            description = description[:300] + "..."

        # Parse facilities
        facilities = hotel.get("HotelFacilities", "").split() if hotel.get("HotelFacilities") else []
        
        # Clean rating
        rating = hotel.get("HotelRating", "Not Rated")
        if rating and rating != "Not Rated" and "star" not in rating.lower():
            rating = f"{rating} Star"

        return {
            "id": doc_id,
            "name": hotel.get("HotelName", "Unknown Hotel"),
            "address": hotel.get("Address", "Address not available"),
            "city": hotel.get("cityName", ""),
            "country": hotel.get("countyName", ""), 
            "rating": rating,
            "description": description,
            "facilities": facilities[:10],
            "phone": hotel.get("PhoneNumber", ""),
            "website": hotel.get("HotelWebsiteUrl", ""),
            "latitude": lat,
            "longitude": lon,
            "raw_data": hotel  # For debugging
        }

    except Exception as e:
        print(f"⚠️ Error formatting hotel with ID {doc_id}: {e}")
        return None

def get_hotel_by_id(doc_id):
    """Simple function to get raw hotel document"""
    try:
        result = collection.get(doc_id)
        return result.content_as[dict]
    except Exception as e:
        print(f"Error getting hotel {doc_id}: {e}")
        return None
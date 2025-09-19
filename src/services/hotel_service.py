# hotel_service.py

import re
import logging
from couchbase.search import MatchQuery, ConjunctionQuery, SearchRequest
from services.couchbase_connection import get_cluster, get_hotels_collection, config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Couchbase connections
cluster = get_cluster()
collection = get_hotels_collection()


def search_hotels(city, county, limit=10):
    """Search hotels using FTS index and return formatted hotel objects"""
    try:
        logger.info(f"Starting hotel search for city='{city}', county='{county}', limit={limit}")

        if not city or not county:
            logger.warning("City or county is empty, skipping search")
            return []

        # Build FTS queries
        city_query = MatchQuery(city, field="cityName")
        county_query = MatchQuery(county, field="countyName")
        fts_query = ConjunctionQuery(city_query, county_query)
        logger.info(f"FTS query built: {fts_query}")

        # Create search request
        search_req = SearchRequest.create(fts_query)
        search_req.limit = limit

        # Get index name from config
        index_name = config.get("fts_index_name")
        if not index_name:
            logger.error("FTS index name missing in config")
            return []

        # Execute FTS search
        results = cluster.search(index_name, search_req)
        logger.info("FTS search executed successfully")

        # Collect hotel IDs and format them 
        rows_list = list(results.rows())
        hotel_ids = [row.id for row in rows_list]
        logger.info(f"Hotel search returned {len(hotel_ids)} hotel IDs")

        # Format all hotels
        formatted_hotels = []
        for hotel_id in hotel_ids:
            formatted_hotel = format_hotel_for_display(hotel_id)
            if formatted_hotel:  
                formatted_hotels.append(formatted_hotel)
        
        logger.info(f"Successfully formatted {len(formatted_hotels)} out of {len(hotel_ids)} hotels")
        return formatted_hotels

    except Exception as e:
        logger.error(f"FTS hotel search failed: {e}", exc_info=True)
        return []


def format_hotel_for_display(doc_id):
    """Fetch hotel doc by ID and format it for display"""
    try:
        logger.info(f"Fetching hotel document by ID: {doc_id}")

        result = collection.get(doc_id)
        hotel = result.content_as[dict]

        # Parse coordinates
        coordinates = hotel.get("Map", "").split("|")
        lat, lon = None, None
        if len(coordinates) == 2:
            try:
                lat, lon = float(coordinates[0]), float(coordinates[1])
            except (ValueError, TypeError):
                logger.warning(f"Invalid coordinates for hotel {doc_id}: {coordinates}")
                lat, lon = None, None

        # Clean description 
        description = hotel.get("Description", "")
        if description:
            description = re.sub('<.*?>', '', description).replace('\\n', ' ').strip()
            if len(description) > 300:
                description = description[:300] + "..."
        else:
            description = "No description available"

        # Parse facilities 
        facilities_str = hotel.get("HotelFacilities", "")
        facilities = []
        if facilities_str:
            # Split by common delimiters and clean up
            facilities = [f.strip() for f in re.split(r'[,;|]', facilities_str) if f.strip()]
            facilities = facilities[:10]  # Limit to first 10

        # Normalize rating 
        rating = hotel.get("HotelRating", "")
        if rating and rating.lower() != "not rated":
            if "star" not in rating.lower():
                rating = f"{rating} Star"
        else:
            rating = "Not Rated"

        # Create formatted hotel object
        formatted_hotel = {
            "id": doc_id,
            "name": hotel.get("HotelName", "Unknown Hotel"),
            "address": hotel.get("Address", "Address not available"),
            "city": hotel.get("cityName", ""),
            "county": hotel.get("countyName", ""),
            "rating": rating,
            "description": description,
            "facilities": facilities,
            "phone": hotel.get("PhoneNumber", ""),
            "website": hotel.get("HotelWebsiteUrl", ""),
            "latitude": lat,
            "longitude": lon,
        }

        logger.info(f"Successfully formatted hotel: {formatted_hotel['name']} ({doc_id})")
        return formatted_hotel

    except Exception as e:
        logger.error(f"Error formatting hotel with ID {doc_id}: {e}", exc_info=True)
        return None


def get_hotel_summary(hotel):
    """Get a summary string for the hotel"""
    if not hotel:
        return "No hotel selected"
    
    name = hotel.get('name', 'Unknown Hotel')
    city = hotel.get('city', '')
    county = hotel.get('county', '')
    rating = hotel.get('rating', 'Not Rated')
    
    location = f"{city}, {county}" if city or county else "Location not available"
    return f"{name} ({rating}) - {location}"


def validate_hotel_data(hotel):
    """Validate that hotel data has required fields"""
    if not hotel:
        return False
    
    required_fields = ['id', 'name']
    for field in required_fields:
        if not hotel.get(field):
            logger.warning(f"Hotel missing required field: {field}")
            return False
    
    return True
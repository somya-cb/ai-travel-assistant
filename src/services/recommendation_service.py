# recommendation_service.py 

import streamlit as st
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from couchbase.search import ConjunctionQuery, MatchQuery
from couchbase.vector_search import VectorQuery, VectorSearch
from couchbase.search import SearchRequest
from couchbase.options import SearchOptions
from src.services.couchbase_connection import (
    get_cluster, 
    get_destinations_collection, 
    get_scope,
    config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get shared connections
cluster = get_cluster()
scope = get_scope()
collection = get_destinations_collection()

# Load embedding model (cache this to avoid reloading)
@st.cache_resource
def load_sentence_transformer():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_sentence_transformer()

def build_fts_filters(filters: dict, debug: bool = False) -> Optional[ConjunctionQuery]:
    """Build FTS filter query from user filters"""
    if not filters:
        return None
    
    valid_fields = ["region", "country", "city", "budget_level"]
    clauses = []

    for field in valid_fields:
        val = filters.get(field)
        if val and str(val).strip():
            # Clean the value
            cleaned_val = str(val).strip().lower()
            clauses.append(MatchQuery(cleaned_val, field=field))
            if debug:
                logger.info(f"Added filter: {field} = '{cleaned_val}'")

    # Handle minimum rating filter
    min_rating = filters.get("min_rating")
    if min_rating and min_rating > 0:
        # This would need a range query if you have rating fields
        pass  # Implement based on your rating field structure

    if clauses:
        if debug:
            logger.info(f"Built {len(clauses)} filter clauses")
        return ConjunctionQuery(*clauses)
    
    return None

def generate_query_from_persona(persona: Dict) -> str:
    """Convert persona to search query string"""
    if not persona:
        return "travel destinations"
    
    query_parts = []
    
    # Add travel style
    if persona.get("travel_style"):
        query_parts.append(persona["travel_style"])
    
    # Add budget preference
    if persona.get("budget"):
        query_parts.append(persona["budget"])
    
    # Add activities
    activities = persona.get("activities", [])
    if activities:
        query_parts.extend(activities[:3])  
    
    # Add companions context
    companions = persona.get("companions", [])
    if companions:
        query_parts.extend(companions[:2]) 
    
    query = " ".join(str(part) for part in query_parts if part)
    return query or "travel destinations"

def run_vector_search(query_str: str, filters: Optional[Dict] = None, k: int = 10, debug: bool = False):
    """Execute vector search with optional filters"""
    try:
        if debug:
            logger.info(f"Vector search query: '{query_str}' with {k} results")
            
        # Generate embedding
        embedding = model.encode(query_str).tolist()
        
        # Build prefilter
        prefilter = build_fts_filters(filters, debug=debug)
        
        # Create vector query
        vector_query = VectorQuery(
            field_name=config["vector_field"],
            vector=embedding,
            prefilter=prefilter,
            num_candidates=k * 2  
        )

        # Execute search
        vs = VectorSearch.from_vector_query(vector_query)
        search_request = SearchRequest.create(vs)
        
        results = scope.search(
            config["vector_index_name"], 
            search_request,
            SearchOptions(limit=k, fields=["*"])
        )

        # Fetch documents
        documents = []
        for row in results.rows():
            try:
                doc = collection.get(row.id).content_as[dict]
                doc["_id"] = row.id  # Add document ID
                doc["_score"] = getattr(row, 'score', 0)  # Add relevance score
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Could not fetch document {row.id}: {e}")
                continue
        
        if debug:
            logger.info(f"Successfully retrieved {len(documents)} documents")
            
        return documents
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []

def get_recommendations(
    search_mode: str,
    user_persona: Dict,
    filters: Optional[Dict] = None,
    user_query: Optional[str] = None,
    debug: bool = False
) -> List[Dict]:
    """
    Main recommendation API
    
    Args:
        search_mode: "surprise" or "filter_search"
        user_persona: User's travel preferences
        filters: Search filters (region, country, city, etc.)
        user_query: Custom search query
        debug: Enable debug logging
    """
    
    try:
        if debug:
            logger.info(f"Getting recommendations - mode: {search_mode}")
        
        # Determine search query
        if user_query:
            query = user_query
        elif filters and filters.get("search_text"):
            query = filters["search_text"]
        else:
            query = generate_query_from_persona(user_persona)
        
        # Determine filters to use
        search_filters = None
        if search_mode == "filter_search" and filters:
            search_filters = filters
        elif search_mode == "surprise":
            search_filters = None
        
        # Execute search
        results = run_vector_search(
            query_str=query,
            filters=search_filters,
            k=10,
            debug=debug
        )
        
        if debug and results:
            logger.info(f"Returning {len(results)} recommendations")
            
        return results
        
    except Exception as e:
        logger.error(f"Recommendation service failed: {e}")
        return []
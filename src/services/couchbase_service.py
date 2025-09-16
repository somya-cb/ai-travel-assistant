# couchbase_service.py
from couchbase.exceptions import DocumentNotFoundException
import couchbase.subdocument as SD
from couchbase_connection import (
    get_cluster, 
    get_destinations_collection, 
    get_user_profiles_collection,
    config
)
import streamlit as st

# Get shared connections
cluster = get_cluster()
collection = get_user_profiles_collection()
destinations_collection = get_destinations_collection()

# ── Persona functions ─────────────────────────────────────────
def get_persona_by_user_id(user_id):
    try:
        result = collection.get(user_id)
        return result.content_as[dict]
    except DocumentNotFoundException:
        return None

def save_persona(user_id, persona_dict):
    collection.upsert(user_id, persona_dict)

# ── Embedding utilities ──────────────────────────────────────
def get_all_destination_ids():
    query = f"SELECT META().id FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}`"
    result = cluster.query(query)
    return [row['id'] for row in result]

def get_destination_doc(doc_id):
    return destinations_collection.get(doc_id).content_as[dict]

def update_destination_embedding(doc_id, embedding):
    destinations_collection.mutate_in(
        doc_id,
        [SD.upsert("description_embedding", embedding)]
    )

# ── Destination retrieval ─────────────────────────────────────
def get_recommended_destinations(persona):
    st.write("Persona used for recommendation:", persona)

    persona_tags = set(
        [persona.get("travel_style", "")] +
        persona.get("activities", []) +
        persona.get("companions", [])
    )
    persona_tags = set(tag.lower() for tag in persona_tags if tag)

    all_ids = get_all_destination_ids()
    matching_destinations = []

    for doc_id in all_ids:
        try:
            doc = get_destination_doc(doc_id)
            dest_tags = set(tag.lower() for tag in doc.get("tags", []))
            if persona_tags & dest_tags:
                doc["id"] = doc_id
                matching_destinations.append(doc)
        except Exception as e:
            st.warning(f"⚠️ Skipping doc {doc_id}: {e}")

    return matching_destinations

def get_destinations_by_filter(filters):
    st.write("🔍 Filter used:", filters)

    all_ids = get_all_destination_ids()
    filtered_destinations = []

    for doc_id in all_ids:
        try:
            doc = get_destination_doc(doc_id)

            if filters.get("region") and filters["region"].lower() != doc.get("region", "").lower():
                continue
            if filters.get("country") and filters["country"].lower() not in doc.get("country", "").lower():
                continue
            if filters.get("city") and filters["city"].lower() not in doc.get("city", "").lower():
                continue

            doc["id"] = doc_id
            filtered_destinations.append(doc)

        except Exception as e:
            st.warning(f"⚠️ Skipping doc {doc_id}: {e}")

    return filtered_destinations

def upsert_destination_doc(doc_id: str, doc_data: dict):
    """Insert or update a destination document in Couchbase"""
    try:
        result = destinations_collection.upsert(doc_id, doc_data)
        return result
    except Exception as e:
        print(f"Error upserting document {doc_id}: {e}")
        raise

def delete_all_destinations():
    """Delete all destination documents"""
    try:
        query = f"DELETE FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}`"
        result = cluster.query(query)
        print("Deleted all existing destinations")
        return result
    except Exception as e:
        print(f"Error deleting destinations: {e}")
        raise

def get_destinations_count():
    """Get count of destination documents"""
    try:
        query = f"SELECT COUNT(*) as count FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}`"
        result = cluster.query(query)
        return list(result)[0]['count']
    except Exception as e:
        print(f"Error getting destinations count: {e}")
        raise

# ── Functions for dropdown data ──────────────────────────
def get_unique_values(field_name: str) -> list:
    """Get unique values for dropdown population"""
    try:
        query = f"SELECT DISTINCT {field_name} FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}` WHERE {field_name} IS NOT NULL ORDER BY {field_name}"
        result = cluster.query(query)
        return [row[field_name] for row in result if row[field_name]]
    except Exception as e:
        return []

def get_countries_by_region(region: str) -> list:
    """Get countries in a specific region"""
    try:
        query = f"SELECT DISTINCT country FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}` WHERE region = $1 ORDER BY country"
        result = cluster.query(query, region)
        return [row['country'] for row in result if row['country']]
    except Exception as e:
        return []

def get_cities_by_country(country: str) -> list:
    """Get cities in a specific country"""
    try:
        query = f"SELECT DISTINCT city FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}` WHERE country = $1 ORDER BY city"
        result = cluster.query(query, country)
        return [row['city'] for row in result if row['city']]
    except Exception as e:
        return []
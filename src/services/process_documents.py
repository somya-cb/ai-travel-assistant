# process_documents.py

import logging
from sentence_transformers import SentenceTransformer
from couchbase_connection import get_cluster, get_destinations_collection, get_hotels_collection, config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
BATCH_SIZE = 200  


# ── DESTINATIONS FUNCTIONS ─────────────────────────────────────
def format_destination(doc: dict) -> dict:
    """Format and clean up a destination document before saving back"""

    if "latitude" in doc:
        try:
            doc["latitude"] = float(doc["latitude"])
        except (ValueError, TypeError):
            doc["latitude"] = None
    
    if "longitude" in doc:
        try:
            doc["longitude"] = float(doc["longitude"])
        except (ValueError, TypeError):
            doc["longitude"] = None
    
    if "avg_temp_monthly" in doc and isinstance(doc["avg_temp_monthly"], str):
        try:
            import json
            doc["avg_temp_monthly"] = json.loads(doc["avg_temp_monthly"])
        except Exception:
            doc["avg_temp_monthly"] = []
    
    if "budget_level" in doc and isinstance(doc["budget_level"], str):
        doc["budget_level"] = doc["budget_level"].strip().lower()
    
    return doc

def vectorize_destination(doc: dict) -> dict:
    """Generate and attach embedding for a destination document."""
    text = doc.get("short_description", "")
    if text:
        doc["embedding"] = model.encode(text).tolist()
    return doc

def get_all_destination_ids():
    """Get all destination document IDs"""
    cluster = get_cluster()
    query = f"SELECT META().id FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['destinations_collection']}`"
    result = cluster.query(query)
    return [row["id"] for row in result]

def main():
    collection = get_destinations_collection()
    doc_ids = get_all_destination_ids()
    total = len(doc_ids)
    processed = 0
    
    logger.info(f"Starting processing of {total} destination documents...")

    for i, doc_id in enumerate(doc_ids, 1):
        try:
            doc = collection.get(doc_id).content_as[dict]

            # Skip if embedding already exists
            if "embedding" not in doc or not doc["embedding"]:
                # Format + vectorize
                doc = format_destination(doc)
                doc = vectorize_destination(doc)

                # Upsert back
                collection.upsert(doc_id, doc)
                processed += 1
            else:
                logger.info(f"Skipping {doc_id}, embedding already exists")

            # Progress update every 100 documents
            if i % 100 == 0:
                logger.info(f"Processed {i}/{total} documents...")

        except Exception as e:
            logger.error(f"Error processing {doc_id}: {e}")

    logger.info(f"Completed processing {processed}/{total} destination documents.")


# ── HOTELS FUNCTIONS ─────────────────────────────────────
def format_hotel(doc: dict) -> dict:
    """Clean up hotel document fields and names"""
    cleaned_doc = {}
    for k, v in doc.items():
        # Strip trailing/leading spaces from field names
        key = k.strip()
        
        # If value is string, strip spaces
        if isinstance(v, str):
            v = v.strip()
        cleaned_doc[key] = v

    # Convert numeric fields if present
    if "Latitude" in cleaned_doc:
        try:
            cleaned_doc["Latitude"] = float(cleaned_doc["Latitude"])
        except (ValueError, TypeError):
            cleaned_doc["Latitude"] = None

    if "Longitude" in cleaned_doc:
        try:
            cleaned_doc["Longitude"] = float(cleaned_doc["Longitude"])
        except (ValueError, TypeError):
            cleaned_doc["Longitude"] = None

    return cleaned_doc

def vectorize_hotel(doc: dict) -> dict:
    """Generate embedding from hotel description"""
    text = doc.get("Description", "")
    if text:
        doc["embedding"] = model.encode(text).tolist()
    return doc

def get_all_hotel_ids():
    """Get all hotel document IDs"""
    cluster = get_cluster()
    query = f"SELECT META().id FROM `{config['couchbase_bucket']}`.`{config['couchbase_scope']}`.`{config['hotels_collection']}`"
    result = cluster.query(query)
    return [row["id"] for row in result]

def process_hotels():
    collection = get_hotels_collection()
    doc_ids = get_all_hotel_ids()
    total = len(doc_ids)
    processed = 0
    logger.info(f"Starting processing of {total} hotel documents...")

    for i, doc_id in enumerate(doc_ids, 1):
        try:
            doc = collection.get(doc_id).content_as[dict]

            # Skip if embedding already exists
            if "embedding" not in doc or not doc["embedding"]:
                # Format + vectorize
                doc = format_hotel(doc)
                doc = vectorize_hotel(doc)

                # Upsert back
                collection.upsert(doc_id, doc)
                processed += 1
            else:
                logger.info(f"Skipping hotel {doc_id}, embedding already exists")

            # Log progress every 100
            if i % 100 == 0:
                logger.info(f"Processed {i}/{total} hotels...")

        except Exception as e:
            logger.error(f"Error processing hotel {doc_id}: {e}")

    logger.info(f"Completed processing {processed}/{total} hotel documents.")


# ── RUN BOTH ─────────────────────────────────────
if __name__ == "__main__":
    main()           # process destinations
    process_hotels()  # process hotels

# process_destinations.py

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer

from couchbase_service import (  
    get_all_destination_ids,
    get_destination_doc,
    update_destination_embedding,
    upsert_destination_doc,
    delete_all_destinations,
    get_destinations_count
)

def preprocess_csv_row(row: pd.Series) -> Dict[str, Any]:
    """Preprocess a single CSV row to fix data types and JSON parsing."""
    processed_doc: Dict[str, Any] = {}

    # Copy basic string fields
    string_fields = ['id', 'city', 'country', 'region', 'short_description', 'budget_level']
    for field in string_fields:
        if field in row and pd.notna(row[field]):
            processed_doc[field] = str(row[field])

    # Convert numeric fields
    numeric_fields = [
        'latitude', 'longitude', 'culture', 'adventure', 'nature',
        'beaches', 'nightlife', 'cuisine', 'wellness', 'urban', 'seclusion'
    ]
    for field in numeric_fields:
        if field in row and pd.notna(row[field]):
            try:
                processed_doc[field] = float(row[field])
                # Convert to int for rating-like fields
                if field in ['culture', 'adventure', 'nature', 'beaches', 'nightlife',
                             'cuisine', 'wellness', 'urban', 'seclusion']:
                    processed_doc[field] = int(processed_doc[field])
            except (ValueError, TypeError):
                processed_doc[field] = row[field]

    # Parse JSON fields
    json_fields = ['avg_temp_monthly', 'ideal_durations']
    for field in json_fields:
        if field in row and pd.notna(row[field]):
            try:
                if isinstance(row[field], str):
                    processed_doc[field] = json.loads(row[field])
                else:
                    processed_doc[field] = row[field]
            except json.JSONDecodeError:
                processed_doc[field] = row[field]

    return processed_doc

def load_and_preprocess_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load CSV and preprocess all rows."""
    print(f"Loading CSV from {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} rows in CSV")

    processed_docs = []
    for idx, row in df.iterrows():
        try:
            processed_doc = preprocess_csv_row(row)
            processed_docs.append(processed_doc)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue

    print(f"Preprocessed {len(processed_docs)} documents")
    return processed_docs

def upload_destinations_to_couchbase(docs: List[Dict[str, Any]]) -> List[str]:
    """Upload destinations to Couchbase."""
    print("Uploading destinations to Couchbase...")
    uploaded_ids = []
    errors = 0

    for i, doc in enumerate(docs, 1):
        try:
            doc_id = doc.get('id')
            if not doc_id:
                continue

            upsert_destination_doc(doc_id, doc)
            uploaded_ids.append(doc_id)
            
            if i % 500 == 0:
                print(f"...processed {i}/{len(docs)} (errors: {errors})")
        except Exception as e:
            errors += 1

    print(f"Upload complete: {len(uploaded_ids)}/{len(docs)} succeeded, {errors} errors")
    return uploaded_ids

def vectorize_destinations(doc_ids: List[str]) -> None:
    """Generate embeddings for destinations and update in Couchbase."""
    print(f"Starting vectorization for {len(doc_ids)} destinations...")
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    success, skipped, errors = 0, 0, 0

    for i, doc_id in enumerate(doc_ids, 1):
        try:
            doc = get_destination_doc(doc_id)
            text = doc.get("short_description", "")
            if not text:
                skipped += 1
                continue

            vector = model.encode(text).tolist()
            update_destination_embedding(doc_id, vector)
            success += 1
            
            if i % 500 == 0:
                print(f"...processed {i}/{len(doc_ids)} (ok: {success}, skipped: {skipped}, errors: {errors})")
        except Exception as e:
            errors += 1

    print(f"Vectorization complete: ok={success}, skipped={skipped}, errors={errors}")

def main() -> None:
    """Main function to process CSV, upload to Couchbase, and vectorize."""
    import argparse

    parser = argparse.ArgumentParser(description='Process destinations CSV and vectorize')
    parser.add_argument('--csv-path', default='Worldwide Travel Cities Dataset (Ratings and Climate).csv')
    parser.add_argument('--skip-upload', action='store_true', help='Skip upload, only vectorize')
    parser.add_argument('--skip-vectorize', action='store_true', help='Skip vectorization, only upload')
    parser.add_argument('--clean-start', action='store_true', help='Delete existing destinations first')

    args = parser.parse_args()

    # Check CSV file
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return

    print("Starting destination processing pipeline...")

    uploaded_ids = []

    if not args.skip_upload:
        # Load and upload
        docs = load_and_preprocess_csv(str(csv_path))

        if args.clean_start:
            print("Deleting existing destinations...")
            delete_all_destinations()
            print("Deleted all existing destinations")

        uploaded_ids = upload_destinations_to_couchbase(docs)

    # Vectorize
    if not args.skip_vectorize:
        if args.skip_upload:
            uploaded_ids = get_all_destination_ids()
            print(f"Found {len(uploaded_ids)} existing destinations to vectorize")

        if uploaded_ids:
            vectorize_destinations(uploaded_ids)

    print("Processing pipeline completed.")

if __name__ == "__main__":
    main()
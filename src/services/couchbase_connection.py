# couchbase_connection.py

import streamlit as st
import logging
from datetime import timedelta
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from .config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config once
config = load_config()

@st.cache_resource
def get_couchbase_cluster():
    """
    Create and return a cached Couchbase cluster connection
    Uses Streamlit's cache to ensure single connection per session
    """
    try:
        cluster = Cluster(
            config["couchbase_connection_string"],
            ClusterOptions(PasswordAuthenticator(
                config["couchbase_username"],
                config["couchbase_password"]
            ))
        )
        cluster.wait_until_ready(timeout=timedelta(seconds=10))
        logger.info("✅ Couchbase cluster connection established")
        return cluster
    except Exception as e:
        logger.error(f"❌ Failed to connect to Couchbase: {e}")
        raise

@st.cache_resource
def get_collections():
    """
    Get all collections used in the app
    Returns a dictionary of collection objects
    """
    try:
        cluster = get_couchbase_cluster()
        bucket = cluster.bucket(config["couchbase_bucket"])
        scope = bucket.scope(config["couchbase_scope"])
        
        collections = {
            "destinations": scope.collection(config["destinations_collection"]),
            "user_profiles": scope.collection(config["user_profiles_collection"]),
            "hotels": scope.collection(config["hotels_collection"]),
        }
        
        logger.info("✅ Collections initialized")
        return {
            "cluster": cluster,
            "bucket": bucket, 
            "scope": scope,
            **collections
        }
    except Exception as e:
        logger.error(f"❌ Failed to initialize collections: {e}")
        raise

# Convenience functions for common operations
def get_cluster():
    """Get the cluster connection"""
    return get_collections()["cluster"]

def get_destinations_collection():
    """Get destinations collection"""
    return get_collections()["destinations"]

def get_user_profiles_collection():
    """Get user profiles collection"""
    return get_collections()["user_profiles"]

def get_hotels_collection():
    """Get hotels collection"""
    return get_collections()["hotels"]

def get_scope():
    """Get the scope"""
    return get_collections()["scope"]

# Health check function
def test_connection():
    """Test if Couchbase connection is working"""
    try:
        cluster = get_cluster()
        # Try a simple operation
        result = cluster.query("SELECT 1 as test").execute_query()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
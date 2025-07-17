
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, ClusterTimeoutOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CouchbaseService:
    
    def __init__(self, config_file='config.json'):
        self.cluster = None
        self.bucket = None
        self.scope = None
        self.user_profiles_collection = None
        self.destinations_collection = None
        self._load_config(config_file)
        self._connect()
    
    def _load_config(self, config_file: str):
        """Load Couchbase configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.connection_string = config['couchbase_connection_string']
            self.username = config['couchbase_username']
            self.password = config['couchbase_password']
            self.bucket_name = config['couchbase_bucket']
            
            # Simple scope and collections - only what we need
            self.scope_name = config.get('couchbase_scope', 'travel_data')
            self.user_profiles_collection_name = config.get('user_profiles_collection', 'user_profiles')
            self.destinations_collection_name = config.get('destinations_collection', 'destinations')
            
        except Exception as e:
            logger.error(f"Error loading Couchbase config: {e}")
            raise
    
    def _connect(self):
        """Connect to Couchbase cluster"""
        try:
            # Set up authentication
            auth = PasswordAuthenticator(self.username, self.password)
            
            # Configure timeout options
            timeout_options = ClusterTimeoutOptions(
                bootstrap_timeout=timedelta(seconds=30),
                resolve_timeout=timedelta(seconds=10),
                connect_timeout=timedelta(seconds=10),
                kv_timeout=timedelta(seconds=10),
                query_timeout=timedelta(seconds=75),
            )
            
            # Connect to cluster
            cluster_options = ClusterOptions(auth, timeout_options=timeout_options)
            self.cluster = Cluster(self.connection_string, cluster_options)
            
            # Wait for cluster to be ready
            self.cluster.wait_until_ready(timedelta(seconds=30))
            
            # Get bucket and scope
            self.bucket = self.cluster.bucket(self.bucket_name)
            self.scope = self.bucket.scope(self.scope_name)
            
            # Get collections - only the ones we need
            self.user_profiles_collection = self.scope.collection(self.user_profiles_collection_name)
            
            # Try to get destinations collection
            try:
                self.destinations_collection = self.scope.collection(self.destinations_collection_name)
            except Exception as e:
                logger.warning(f"Destinations collection not available: {e}")
                self.destinations_collection = None
            
            logger.info(f"Connected to Couchbase successfully")
            logger.info(f"Using bucket: {self.bucket_name}")
            logger.info(f"Using scope: {self.scope_name}")
            logger.info(f"User profiles collection: {self.user_profiles_collection_name}")
            logger.info(f"Destinations collection: {self.destinations_collection_name}")
            
        except Exception as e:
            logger.error(f"Error connecting to Couchbase: {e}")
            logger.error("Troubleshooting tips:")
            logger.error("1. Check internet connection")
            logger.error("2. Verify connection string format: couchbases://cb.xxx.cloud.couchbase.com")
            logger.error("3. Confirm username and password are correct")
            logger.error("4. Ensure bucket name exists")
            raise
    
    # ==========================================
    # USER MANAGEMENT METHODS
    # ==========================================
    
    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address"""
        try:
            normalized_email = email.lower().strip()
            
            query = f"""
            SELECT * FROM `{self.bucket_name}`.`{self.scope_name}`.`{self.user_profiles_collection_name}` 
            WHERE email = $email AND type = 'user_record'
            LIMIT 1
            """
            
            result = self.cluster.query(query, email=normalized_email)
            users = [row for row in result]
            
            if users:
                logger.info(f"Found existing user for email {normalized_email}")
                return users[0]
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def create_user_record(self, user_id: str, email: str, name: str) -> bool:
        """Create a user record"""
        try:
            user_record = {
                "user_id": user_id,
                "email": email.lower().strip(),
                "name": name.strip(),
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "profile_completed": False,
                "type": "user_record"
            }
            
            doc_id = f"user::{user_id}"
            self.user_profiles_collection.upsert(doc_id, user_record)
            logger.info(f"Created user record for {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user record: {e}")
            return False
    
    def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            doc_id = f"user::{user_id}"
            result = self.user_profiles_collection.get(doc_id)
            user_data = result.content_as[dict]
            user_data["last_login"] = datetime.now().isoformat()
            self.user_profiles_collection.upsert(doc_id, user_data)
            logger.info(f"Updated last login for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    # ==========================================
    # PERSONA MANAGEMENT METHODS
    # ==========================================
    
    def save_persona(self, persona_dict: Dict[str, Any], user_id: str) -> bool:
        """Save travel persona"""
        try:
            doc_id = f"persona::{user_id}"
            
            # Add metadata
            persona_dict.update({
                "last_updated": datetime.now().isoformat(),
                "profile_version": persona_dict.get("profile_version", 1),
                "type": "travel_persona"
            })
            
            self.user_profiles_collection.upsert(doc_id, persona_dict)
            logger.info(f"Saved persona for user {user_id}")
            
            # Mark user profile as completed
            self._mark_profile_completed(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving persona: {e}")
            return False
    
    def get_persona(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get travel persona"""
        try:
            doc_id = f"persona::{user_id}"
            result = self.user_profiles_collection.get(doc_id)
            persona_data = result.content_as[dict]
            logger.info(f"Retrieved persona for user {user_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"Error getting persona for user {user_id}: {e}")
            return None
    
    def _mark_profile_completed(self, user_id: str) -> bool:
        """Mark user profile as completed"""
        try:
            doc_id = f"user::{user_id}"
            result = self.user_profiles_collection.get(doc_id)
            user_data = result.content_as[dict]
            user_data["profile_completed"] = True
            self.user_profiles_collection.upsert(doc_id, user_data)
            return True
        except Exception as e:
            logger.error(f"Error marking profile completed: {e}")
            return False
    
    # ==========================================
    # DESTINATIONS METHODS
    # ==========================================
    
    def get_destinations_collection(self):
        """Get destinations collection"""
        return self.destinations_collection
    
    def get_all_destinations(self) -> List[Dict[str, Any]]:
        """Get all destinations"""
        try:
            if not self.destinations_collection:
                logger.warning("Destinations collection not available")
                return []
            
            query = f"""
            SELECT * FROM `{self.bucket_name}`.`{self.scope_name}`.`{self.destinations_collection_name}`
            WHERE type = 'destination'
            """
            
            result = self.cluster.query(query)
            destinations = [row for row in result]
            
            logger.info(f"Retrieved {len(destinations)} destinations")
            return destinations
            
        except Exception as e:
            logger.error(f"Error getting destinations: {e}")
            return []
    
    def get_destination_by_name(self, destination_name: str) -> Optional[Dict[str, Any]]:
        """Get destination by name"""
        try:
            if not self.destinations_collection:
                return None
            
            query = f"""
            SELECT * FROM `{self.bucket_name}`.`{self.scope_name}`.`{self.destinations_collection_name}`
            WHERE (city LIKE '%{destination_name}%' OR country LIKE '%{destination_name}%')
            AND type = 'destination'
            LIMIT 1
            """
            
            result = self.cluster.query(query)
            destinations = [row for row in result]
            
            if destinations:
                logger.info(f"Found destination for: {destination_name}")
                return destinations[0]
            return None
            
        except Exception as e:
            logger.error(f"Error finding destination {destination_name}: {e}")
            return None
    
    # ==========================================
    #  CHAT METHODS 
    # ==========================================
    
    def save_chat_message(self, user_id: str, message: Dict[str, Any], trip_id: str = None) -> bool:
        """Simple chat message saving (optional - for basic logging)"""
        try:
            # For the simple prototype, we can just log this or skip it entirely
            logger.info(f"Chat message from user {user_id}: {message.get('content', '')[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return False
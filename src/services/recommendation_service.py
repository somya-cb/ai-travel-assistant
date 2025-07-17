import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleRecommendationService:
    
    def __init__(self, couchbase_service, csv_path: str):
        self.db = couchbase_service
        self.csv_path = csv_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.destinations_loaded = False
        self.load_destinations_from_csv()
    
    def load_destinations_from_csv(self):
        """Load destinations from CSV and store in Couchbase with embeddings"""
        try:
            # Load CSV
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df)} destinations from CSV")
            
            # Create embeddings for short descriptions
            descriptions = df['short_description'].fillna('').tolist()
            embeddings = self.embedding_model.encode(descriptions)
            logger.info(f"Created embeddings for {len(descriptions)} destinations")
            
            # Store in Couchbase
            self.store_destinations_in_couchbase(df, embeddings)
            self.destinations_loaded = True
            
        except Exception as e:
            logger.error(f"Error loading destinations: {e}")
            raise
    
    def store_destinations_in_couchbase(self, df: pd.DataFrame, embeddings: np.ndarray):
        """Store destinations with embeddings in Couchbase"""
        try:
            stored_count = 0
            
            for idx, row in df.iterrows():
                # Create destination document
                destination_doc = {
                    "destination_id": str(row['id']),
                    "city": str(row['city']),
                    "country": str(row['country']),
                    "region": str(row['region']),
                    "short_description": str(row['short_description']),
                    "latitude": float(row['latitude']) if pd.notna(row['latitude']) else None,
                    "longitude": float(row['longitude']) if pd.notna(row['longitude']) else None,
                    "avg_temp_monthly": str(row['avg_temp_monthly']),
                    "ideal_durations": str(row['ideal_durations']),
                    "budget_level": str(row['budget_level']),
                    
                    # Activity scores
                    "culture_score": int(row['culture']) if pd.notna(row['culture']) else 0,
                    "adventure_score": int(row['adventure']) if pd.notna(row['adventure']) else 0,
                    "nature_score": int(row['nature']) if pd.notna(row['nature']) else 0,
                    "beaches_score": int(row['beaches']) if pd.notna(row['beaches']) else 0,
                    "nightlife_score": int(row['nightlife']) if pd.notna(row['nightlife']) else 0,
                    "cuisine_score": int(row['cuisine']) if pd.notna(row['cuisine']) else 0,
                    "wellness_score": int(row['wellness']) if pd.notna(row['wellness']) else 0,
                    "urban_score": int(row['urban']) if pd.notna(row['urban']) else 0,
                    "seclusion_score": int(row['seclusion']) if pd.notna(row['seclusion']) else 0,
                    
                    # Vector for search
                    "description_embedding": embeddings[idx].tolist(),
                    "type": "destination",
                    "created_at": datetime.now().isoformat()
                }
                
                # Store in Couchbase
                doc_id = f"destination::{row['id']}"
                self.db.destinations_collection.upsert(doc_id, destination_doc)
                stored_count += 1
            
            logger.info(f"Stored {stored_count} destinations in Couchbase")
            
        except Exception as e:
            logger.error(f"Error storing destinations: {e}")
            raise
    
    def get_recommendations(self, user_profile: Dict[str, Any], 
                          trip_month: str = None, 
                          trip_duration: str = None,
                          preference_changes: str = None) -> List[Dict[str, Any]]:
        """Get travel recommendations based on user profile"""
        
        try:
            # Create search query from user profile
            search_query = self.create_search_query(user_profile, preference_changes)
            
            # Get embedding for search query
            query_embedding = self.embedding_model.encode([search_query])[0]
            
            # Get all destinations
            destinations = self.get_all_destinations()
            
            if not destinations:
                logger.warning("No destinations found in database")
                return []
            
            # Score destinations
            scored_destinations = []
            
            for dest in destinations:
                # Vector similarity
                dest_embedding = np.array(dest['description_embedding'])
                similarity = np.dot(query_embedding, dest_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(dest_embedding)
                )
                
                # Activity matching score
                activity_score = self.calculate_activity_match(user_profile, dest)
                
                # Budget compatibility
                budget_score = self.calculate_budget_match(user_profile, dest['budget_level'])
                
                # Duration compatibility
                duration_score = self.calculate_duration_match(trip_duration, dest['ideal_durations'])
                
                # Combined score
                combined_score = (
                    similarity * 0.5 +          # 50% semantic similarity
                    activity_score * 0.3 +      # 30% activity match
                    budget_score * 0.15 +       # 15% budget match
                    duration_score * 0.05       # 5% duration match
                )
                
                scored_destinations.append({
                    **dest,
                    'similarity_score': float(similarity),
                    'activity_score': float(activity_score),
                    'budget_score': float(budget_score),
                    'duration_score': float(duration_score),
                    'combined_score': float(combined_score)
                })
            
            # Sort by combined score
            scored_destinations.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Return top 5
            return scored_destinations[:5]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def create_search_query(self, user_profile: Dict[str, Any], preference_changes: str = None) -> str:
        """Create search query from user profile"""
        
        search_terms = []
        
        # If user wants something different, use their input
        if preference_changes:
            search_terms.append(preference_changes)
        
        # Travel personalities
        personality_terms = {
            "cultural_explorer": "culture museums history heritage temples",
            "adventure_seeker": "adventure outdoor hiking mountains trekking",
            "luxury_traveler": "luxury premium upscale elegant sophisticated",
            "foodie": "food cuisine restaurants culinary dining",
            "nature_lover": "nature wildlife parks forests mountains",
            "budget_backpacker": "budget affordable backpacker authentic local",
            "wellness_guru": "wellness spa relaxation peaceful tranquil",
            "family_vacationer": "family friendly safe entertainment activities"
        }
        
        for personality in user_profile.get('traveler_types', []):
            search_terms.append(personality_terms.get(personality, personality))
        
        # Activity preferences
        activity_terms = {
            "museums_culture": "museums cultural heritage",
            "outdoor_adventure": "outdoor adventure hiking",
            "food_wine": "food wine cuisine",
            "beaches": "beaches coastal ocean",
            "nightlife": "nightlife entertainment",
            "wellness_spa": "wellness spa relaxation",
            "nature_wildlife": "nature wildlife parks"
        }
        
        for activity in user_profile.get('activity_preferences', []):
            search_terms.append(activity_terms.get(activity, activity))
        
        # Budget style
        budget_terms = {
            "budget_conscious": "affordable budget",
            "mid_range": "moderate",
            "luxury": "luxury premium"
        }
        
        budget_style = user_profile.get('budget_style', 'mid_range')
        search_terms.append(budget_terms.get(budget_style, 'moderate'))
        
        return ' '.join(search_terms)
    
    def calculate_activity_match(self, user_profile: Dict[str, Any], destination: Dict[str, Any]) -> float:
        """Calculate activity matching score"""
        
        # Map user preferences to destination scores
        preference_mappings = {
            "cultural_explorer": ["culture_score", "urban_score"],
            "adventure_seeker": ["adventure_score", "nature_score"],
            "luxury_traveler": ["urban_score", "cuisine_score"],
            "foodie": ["cuisine_score"],
            "nature_lover": ["nature_score", "seclusion_score"],
            "budget_backpacker": ["culture_score", "adventure_score"],
            "wellness_guru": ["wellness_score", "seclusion_score"],
            "family_vacationer": ["urban_score", "beaches_score"]
        }
        
        activity_mappings = {
            "museums_culture": ["culture_score"],
            "outdoor_adventure": ["adventure_score", "nature_score"],
            "food_wine": ["cuisine_score"],
            "beaches": ["beaches_score"],
            "nightlife": ["nightlife_score"],
            "wellness_spa": ["wellness_score"],
            "nature_wildlife": ["nature_score"]
        }
        
        total_score = 0
        total_weight = 0
        
        # Score based on traveler types
        for traveler_type in user_profile.get('traveler_types', []):
            for score_key in preference_mappings.get(traveler_type, []):
                total_score += destination.get(score_key, 0)
                total_weight += 100
        
        # Score based on activity preferences
        for activity in user_profile.get('activity_preferences', []):
            for score_key in activity_mappings.get(activity, []):
                total_score += destination.get(score_key, 0)
                total_weight += 100
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def calculate_budget_match(self, user_profile: Dict[str, Any], dest_budget: str) -> float:
        """Calculate budget compatibility"""
        
        user_budget = user_profile.get('budget_style', 'mid_range')
        
        compatibility = {
            ('budget_conscious', 'Budget'): 1.0,
            ('budget_conscious', 'Mid-Range'): 0.7,
            ('budget_conscious', 'Luxury'): 0.3,
            ('mid_range', 'Budget'): 0.8,
            ('mid_range', 'Mid-Range'): 1.0,
            ('mid_range', 'Luxury'): 0.6,
            ('luxury', 'Budget'): 0.4,
            ('luxury', 'Mid-Range'): 0.7,
            ('luxury', 'Luxury'): 1.0
        }
        
        return compatibility.get((user_budget, dest_budget), 0.5)
    
    def calculate_duration_match(self, trip_duration: str, ideal_durations: str) -> float:
        """Calculate duration compatibility"""
        
        if not trip_duration or not ideal_durations:
            return 0.5
        
        # Simple duration matching
        if 'short' in trip_duration.lower() and ('3-5' in ideal_durations or '2-4' in ideal_durations):
            return 1.0
        elif 'long' in trip_duration.lower() and ('7-10' in ideal_durations or '1-2 weeks' in ideal_durations):
            return 1.0
        else:
            return 0.5
    
    def get_all_destinations(self) -> List[Dict[str, Any]]:
        """Get all destinations from Couchbase"""
        try:
            query = f"""
            SELECT * FROM `{self.db.bucket_name}`.`{self.db.scope_name}`.`{self.db.destinations_collection_name}`
            WHERE type = 'destination'
            """
            
            result = self.db.cluster.query(query)
            destinations = [row for row in result]
            
            logger.info(f"Retrieved {len(destinations)} destinations from database")
            return destinations
            
        except Exception as e:
            logger.error(f"Error getting destinations from database: {e}")
            return []
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for display"""
        
        if not recommendations:
            return "I couldn't find any destinations matching your preferences right now. Let me try a different approach - what kind of experience are you looking for?"
        
        formatted = "🌟 **Perfect destinations for you:**\n\n"
        
        for i, dest in enumerate(recommendations, 1):
            formatted += f"**{i}. {dest['city']}, {dest['country']}**\n"
            formatted += f"📍 {dest['region']}\n"
            formatted += f"💭 {dest['short_description']}\n"
            formatted += f"💰 Budget: {dest['budget_level']}\n"
            formatted += f"⏰ Ideal duration: {dest['ideal_durations']}\n"
            formatted += f"🎯 Match score: {dest['combined_score']:.2f}\n\n"
        
        formatted += "**Which destination interests you most?** I can create a detailed itinerary for any of these! 🎒"
        
        return formatted
    
    def get_destination_by_name(self, destination_name: str) -> Optional[Dict[str, Any]]:
        """Get destination data by name for itinerary creation"""
        try:
            query = f"""
            SELECT * FROM `{self.db.bucket_name}`.`{self.db.scope_name}`.`{self.db.destinations_collection_name}`
            WHERE (city LIKE '%{destination_name}%' OR country LIKE '%{destination_name}%')
            AND type = 'destination'
            LIMIT 1
            """
            
            result = self.db.cluster.query(query)
            destinations = [row for row in result]
            
            if destinations:
                return destinations[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting destination {destination_name}: {e}")
            return None
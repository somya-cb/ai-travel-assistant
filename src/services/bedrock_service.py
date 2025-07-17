import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from langchain_aws.chat_models import ChatBedrock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockService:
    """AWS Bedrock service for travel recommendations"""
    
    def __init__(self, config_file='config.json'):
        self.chat_model = None
        self._load_config(config_file)
        self._initialize_bedrock()
    
    def _load_config(self, config_file: str):
        """Load AWS credentials"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Set AWS environment variables
            os.environ["AWS_ACCESS_KEY_ID"] = config['aws_access_key_id']
            os.environ["AWS_SECRET_ACCESS_KEY"] = config['aws_secret_access_key']
            
            self.region = "us-east-2"
            self.inference_profile_id = "us.meta.llama4-maverick-17b-instruct-v1:0"
            
        except Exception as e:
            logger.error(f"Error loading AWS config: {e}")
            raise
    
    def _initialize_bedrock(self):
        """Initialize Bedrock chat model"""
        try:
            model_kwargs = {
                "temperature": 0.7,
                "max_tokens": 1500,
                "top_p": 0.9
            }
            
            self.chat_model = ChatBedrock(
                model_id=self.inference_profile_id,
                region_name=self.region,
                model_kwargs=model_kwargs
            )
            
            logger.info(f"Bedrock service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Bedrock: {e}")
            raise
    
    def clean_response(self, response_text: str) -> str:
        """Clean and format Llama 4 response"""
        # Remove common artifacts
        cleaned = response_text.replace('```', '')
        
        # Fix formatting
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  
        cleaned = re.sub(r'\*{3,}', '**', cleaned)    
        
        # Remove weird characters
        cleaned = re.sub(r'[^\w\s\-\*\.\,\!\?\:\(\)\$\n\#\&\%\@]', '', cleaned)
        
        return cleaned.strip()
    
    def create_travel_plan(self, user_message: str, persona_summary: str, 
                          chat_history: List[Dict[str, str]] = None) -> str:
        """Main method - creates travel responses with basic logic"""
        
        message_lower = user_message.lower()
        
        # Simple greeting detection
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        if any(keyword in message_lower for keyword in greeting_keywords) and len(message_lower) < 20:
            return self.create_greeting_response()
        
        # Check for recommendation requests
        recommend_keywords = ['recommend', 'suggest', 'where should i go', 'places to visit']
        if any(keyword in message_lower for keyword in recommend_keywords):
            return self.create_recommendation_response(user_message, persona_summary)
        
        # Simple destination + duration detection for itinerary
        destination_keywords = ['go to', 'visit', 'travel to', 'trip to']
        duration_keywords = ['days', 'weeks', 'weekend']
        
        has_destination = any(keyword in message_lower for keyword in destination_keywords)
        has_duration = any(keyword in message_lower for keyword in duration_keywords)
        
        if has_destination and has_duration:
            # Create itinerary
            return self.create_simple_itinerary_from_message(user_message, persona_summary)
        elif has_destination:
            # Just destination mentioned
            destination = self.extract_destination_from_message(user_message)
            return self.create_destination_response(destination, persona_summary)
        
        # General travel conversation
        return self.create_general_chat_response(user_message, persona_summary)
    
    def create_greeting_response(self) -> str:
        """Create a warm greeting response"""
        
        prompt = """You are a friendly, helpful travel assistant. The user just greeted you.

Respond warmly and ask about their travel interests. Keep it conversational, welcoming, and under 3 sentences.

Ask what they're thinking about for travel or if they want recommendations."""
        
        try:
            response = self.chat_model.invoke(prompt)
            return self.clean_response(response.content)
        except Exception as e:
            logger.error(f"Error creating greeting response: {e}")
            return "Hello! I'm excited to help you plan your next adventure. What destination are you thinking about, or would you like me to recommend some places? ✈️"
    
    def create_recommendation_response(self, user_message: str, persona_summary: str) -> str:
        """Handle recommendation requests - let conversation handler take over"""
        
        # For the prototype, this will be handled by the conversation handler
        # Just provide a helpful response asking for more details
        
        prompt = f"""The user is asking for travel recommendations: "{user_message}"

Their travel profile: {persona_summary}

Ask them for trip duration (short/long trip) if not mentioned. Be helpful and enthusiastic.
Keep response under 3 sentences."""
        
        try:
            response = self.chat_model.invoke(prompt)
            return self.clean_response(response.content)
        except Exception as e:
            logger.error(f"Error creating recommendation response: {e}")
            return "I'd love to recommend perfect destinations for you! Are you looking for a short trip (2-4 days) or a long trip (1-2 weeks)?"
    
    def create_general_chat_response(self, user_message: str, persona_summary: str) -> str:
        """Create response for general travel conversation"""
        
        prompt = f"""You are a helpful travel assistant. 

User's travel profile: {persona_summary}
User message: "{user_message}"

Respond naturally and helpfully. If they want travel planning, ask about their destination and dates.
Keep response conversational and under 4 sentences."""
        
        try:
            response = self.chat_model.invoke(prompt)
            return self.clean_response(response.content)
        except Exception as e:
            logger.error(f"Error creating general chat response: {e}")
            return "I'm here to help with your travel planning! What would you like to know?"
    
    def create_destination_response(self, destination: str, persona_summary: str) -> str:
        """Create response when user mentions a destination"""
        
        prompt = f"""The user mentioned wanting to visit {destination}.

Their travel style: {persona_summary}

Give 2-3 enthusiastic suggestions about {destination} that match their style.
Then ask when they're planning to go and for how long.
Keep response brief and engaging."""
        
        try:
            response = self.chat_model.invoke(prompt)
            return self.clean_response(response.content)
        except Exception as e:
            logger.error(f"Error creating destination response: {e}")
            return f"{destination} is a fantastic choice! When are you planning to visit and for how many days? I'll create a personalized itinerary for you!"
    
    def extract_destination_from_message(self, user_message: str) -> str:
        """Extract destination from user message"""
        
        message_lower = user_message.lower()
        
        # Look for destination after keywords
        for keyword in ['go to', 'visit', 'travel to', 'trip to']:
            if keyword in message_lower:
                parts = message_lower.split(keyword, 1)
                if len(parts) > 1:
                    dest_words = parts[1].strip().split()[:2]  # Take first 1-2 words
                    destination = ' '.join(dest_words).strip().title()
                    return destination
        
        return "that destination"
    
    def create_simple_itinerary_from_message(self, user_message: str, persona_summary: str) -> str:
        """Create simple itinerary from user message"""
        
        message_lower = user_message.lower()
        
        # Extract destination
        destination = self.extract_destination_from_message(user_message)
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*days?', message_lower)
        num_days = 3
        if duration_match:
            num_days = min(int(duration_match.group(1)), 7)  # Cap at 7 days
        
        return self.create_detailed_itinerary(destination, num_days, persona_summary)
    
    def create_detailed_itinerary(self, destination: str, num_days: int, persona_summary: str, 
                                destination_data: Dict[str, Any] = None) -> str:
        """Create detailed itinerary - main method for the prototype"""
        
        # Enhanced prompt with destination data if available
        if destination_data:
            data_context = f"""
**REAL DESTINATION DATA:**
- Description: {destination_data.get('short_description', 'Amazing destination')}
- Budget Level: {destination_data.get('budget_level', 'Mid-Range')}
- Culture Score: {destination_data.get('culture_score', 50)}/100
- Adventure Score: {destination_data.get('adventure_score', 50)}/100
- Nature Score: {destination_data.get('nature_score', 50)}/100
- Food Score: {destination_data.get('cuisine_score', 50)}/100
- Ideal Duration: {destination_data.get('ideal_durations', f'{num_days} days')}"""
        else:
            data_context = f"**DESTINATION:** {destination} - Create realistic recommendations based on what this destination is known for."
        
        prompt = f"""Create a detailed {num_days}-day travel itinerary for {destination}.

{data_context}

**TRAVELER PROFILE:** {persona_summary}

Create a comprehensive itinerary following this EXACT format:

**{destination} {num_days}-Day Personalized Itinerary**

**Day 1: [Theme based on traveler interests]**
🌅 **Morning (9:00 AM - 12:00 PM)**
- **Activity**: [Specific venue/activity name]
- **Why perfect for you**: [Connect to traveler's interests in 1 sentence]
- **Cost**: $XX per person
- **Location**: [Specific area]

🌞 **Afternoon (1:00 PM - 5:00 PM)**
- **Activity**: [Specific venue/activity name]
- **Why perfect for you**: [Connect to traveler's interests]
- **Cost**: $XX per person
- **Pro tip**: [Local insight]

🌙 **Evening (6:00 PM - 10:00 PM)**
- **Dinner**: [Specific restaurant/area name]
- **Cost**: $XX per person
- **Evening Activity**: [Specific activity]
- **Cost**: $XX per person

[Continue this format for each day up to {num_days} days]

**🏨 Accommodation Recommendation**
- **Hotel**: [Name and description] - $XX per night
- **Why recommended**: [Match to traveler preferences]

**💰 Budget Summary**
- Accommodation: $XX ({num_days} nights)
- Meals: $XX (avg $XX per day)
- Activities: $XX
- **Total**: $XX per person

**🎒 Personalized Tips**
- [3-4 specific tips based on traveler's style and destination]

IMPORTANT: Use realistic prices. Include specific venue names. Match all recommendations to the traveler's profile."""
        
        try:
            response = self.chat_model.invoke(prompt)
            cleaned_response = self.clean_response(response.content)
            
            cleaned_response += f"\n\n✨ **Have an amazing trip to {destination}!** Let me know if you'd like me to adjust anything!"
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Error creating detailed itinerary: {e}")
            return f"I'd love to create a detailed itinerary for your {num_days}-day trip to {destination}! However, I'm experiencing some technical difficulties right now. Please try again in a moment."
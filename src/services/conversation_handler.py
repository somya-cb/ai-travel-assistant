"""Simple Conversation Handler for Travel Recommendations"""

import re
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SimpleConversationHandler:
    """Simple handler for travel recommendation conversations"""
    
    def __init__(self, recommendation_service, bedrock_service):
        self.rec_service = recommendation_service
        self.bedrock_service = bedrock_service
    
    def detect_recommendation_request(self, message: str) -> Dict[str, Any]:
        """Detect if user is asking for travel recommendations"""
        
        message_lower = message.lower()
        
        # Keywords for recommendation requests
        recommend_keywords = [
            'recommend', 'suggest', 'where should i go', 'where to go',
            'places to visit', 'destinations', 'travel ideas', 'best places',
            'where can i travel', 'travel suggestions', 'recommend places'
        ]
        
        # Month detection
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        
        detected_month = None
        for month in months:
            if month in message_lower:
                detected_month = month
                break
        
        # Duration hints
        duration_hints = ['short', 'long', 'weekend', 'week', 'days']
        detected_duration = None
        for hint in duration_hints:
            if hint in message_lower:
                detected_duration = hint
                break
        
        is_recommendation_request = any(keyword in message_lower for keyword in recommend_keywords)
        
        return {
            'is_recommendation_request': is_recommendation_request,
            'detected_month': detected_month,
            'detected_duration': detected_duration,
            'has_travel_context': detected_month or detected_duration
        }
    
    def detect_destination_selection(self, message: str) -> Optional[str]:
        """Detect if user is selecting a destination from recommendations"""
        
        message_lower = message.lower()
        
        # Common selection phrases
        selection_phrases = [
            'tell me about', 'more about', 'details about', 'interested in',
            'pick', 'choose', 'select', 'go with', 'itinerary for',
            'plan for', 'create itinerary', 'detailed plan'
        ]
        
        for phrase in selection_phrases:
            if phrase in message_lower:
                # Extract destination name after the phrase
                parts = message_lower.split(phrase, 1)
                if len(parts) > 1:
                    potential_dest = parts[1].strip()
                    # Clean up common words
                    potential_dest = re.sub(r'\b(the|a|an|please|for|me)\b', '', potential_dest).strip()
                    return potential_dest
        
        # Check if message contains a city name (simple heuristic)
        # This is basic - could be enhanced with NER
        words = message_lower.split()
        if len(words) <= 3:  # Short message, likely a destination name
            return ' '.join(words)
        
        return None
    
    def handle_recommendation_flow(self, message: str, user_profile: Dict[str, Any], 
                                 conversation_state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle the recommendation conversation flow"""
        
        try:
            # Check current state
            current_state = conversation_state.get('recommendation_state', 'none')
            
            # State 1: Initial recommendation request
            if current_state == 'none':
                request_info = self.detect_recommendation_request(message)
                
                if request_info['is_recommendation_request']:
                    return self.handle_initial_request(message, user_profile, request_info)
                else:
                    return None, conversation_state  # Not a recommendation request
            
            # State 2: Waiting for duration
            elif current_state == 'waiting_duration':
                return self.handle_duration_response(message, user_profile, conversation_state)
            
            # State 3: Waiting for preference confirmation
            elif current_state == 'waiting_preferences':
                return self.handle_preference_response(message, user_profile, conversation_state)
            
            # State 4: Showing recommendations, waiting for selection
            elif current_state == 'showing_recommendations':
                return self.handle_destination_selection(message, user_profile, conversation_state)
            
            else:
                # Reset state
                conversation_state['recommendation_state'] = 'none'
                return None, conversation_state
                
        except Exception as e:
            logger.error(f"Error in recommendation flow: {e}")
            conversation_state['recommendation_state'] = 'none'
            return "I encountered an error processing your request. How can I help you with travel recommendations?", conversation_state
    
    def handle_initial_request(self, message: str, user_profile: Dict[str, Any], 
                             request_info: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle initial recommendation request"""
        
        # Store detected information
        new_state = {
            'recommendation_state': 'waiting_duration',
            'detected_month': request_info['detected_month'],
            'detected_duration': request_info['detected_duration']
        }
        
        # If duration is missing, ask for it
        if not request_info['detected_duration']:
            month_text = f" in {request_info['detected_month'].title()}" if request_info['detected_month'] else ""
            
            response = f"""Great! I'd love to recommend perfect destinations for you{month_text}! 🌟

Are you looking for:
• **Short trip** (2-4 days) - Weekend getaway or quick escape
• **Long trip** (1-2 weeks) - Proper vacation with time to explore

Which sounds better for you?"""
            
            return response, new_state
        
        # If we have duration, move to preference confirmation
        else:
            new_state['recommendation_state'] = 'waiting_preferences'
            return self.generate_preference_confirmation(user_profile, request_info), new_state
    
    def handle_duration_response(self, message: str, user_profile: Dict[str, Any], 
                               conversation_state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle user's duration response"""
        
        message_lower = message.lower()
        
        # Detect duration from response
        if any(word in message_lower for word in ['short', 'weekend', 'quick', '2', '3', '4']):
            detected_duration = 'short'
        elif any(word in message_lower for word in ['long', 'week', 'proper', '7', '10', '14']):
            detected_duration = 'long'
        else:
            # Ask for clarification
            response = """I'd like to help you choose the perfect trip length! 

Could you tell me:
• **Short trip** (2-4 days) for a quick getaway?
• **Long trip** (1-2 weeks) for a proper vacation?

Which one sounds right for you?"""
            
            return response, conversation_state
        
        # Store duration and move to preference confirmation
        conversation_state['detected_duration'] = detected_duration
        conversation_state['recommendation_state'] = 'waiting_preferences'
        
        request_info = {
            'detected_month': conversation_state.get('detected_month'),
            'detected_duration': detected_duration
        }
        
        return self.generate_preference_confirmation(user_profile, request_info), conversation_state
    
    def generate_preference_confirmation(self, user_profile: Dict[str, Any], 
                                       request_info: Dict[str, Any]) -> str:
        """Generate preference confirmation message"""
        
        # Format user profile
        personalities = user_profile.get('traveler_types', [])
        budget = user_profile.get('budget_style', 'mid_range')
        companions = user_profile.get('travel_companions', 'solo')
        
        # Format for display
        personality_names = {
            "cultural_explorer": "Cultural Explorer",
            "adventure_seeker": "Adventure Seeker", 
            "luxury_traveler": "Luxury Traveler",
            "foodie": "Foodie",
            "nature_lover": "Nature Lover",
            "budget_backpacker": "Budget Backpacker",
            "wellness_guru": "Wellness Guru",
            "family_vacationer": "Family Vacationer"
        }
        
        budget_names = {
            "budget_conscious": "budget-friendly",
            "mid_range": "mid-range",
            "luxury": "luxury"
        }
        
        companion_names = {
            "solo": "solo",
            "couple": "couple",
            "family_with_kids": "family with kids",
            "group_of_friends": "group of friends"
        }
        
        formatted_personalities = [personality_names.get(p, p.replace('_', ' ').title()) for p in personalities[:2]]
        formatted_budget = budget_names.get(budget, budget.replace('_', ' '))
        formatted_companions = companion_names.get(companions, companions.replace('_', ' '))
        
        # Build message
        duration_text = request_info['detected_duration'] or 'your'
        month_text = request_info['detected_month'].title() if request_info['detected_month'] else 'your chosen time'
        
        message = f"""Perfect! I see you're planning a {duration_text} trip in {month_text}! 🎯

Based on your profile, you typically enjoy:
• **{formatted_budget.title()}** travel experiences
• **{formatted_companions.title()}** trips
• **{', '.join(formatted_personalities)}** style adventures

**Would you like recommendations based on these usual preferences, or are you looking to try something different this time?**

Just say:
• **"Same as usual"** - I'll find destinations perfect for your style
• **"Something different"** - Tell me what you'd like to explore differently! ✨"""
        
        return message
    
    def handle_preference_response(self, message: str, user_profile: Dict[str, Any], 
                                 conversation_state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle user's preference confirmation response"""
        
        message_lower = message.lower()
        
        # Detect if they want same or different
        same_keywords = ['same', 'usual', 'normal', 'typical', 'regular', 'yes', 'yep', 'yeah']
        different_keywords = ['different', 'change', 'new', 'try', 'something else', 'no']
        
        wants_same = any(keyword in message_lower for keyword in same_keywords)
        wants_different = any(keyword in message_lower for keyword in different_keywords)
        
        # Get stored context
        trip_month = conversation_state.get('detected_month')
        trip_duration = conversation_state.get('detected_duration')
        
        if wants_same:
            # Use existing profile
            recommendations = self.rec_service.get_recommendations(
                user_profile=user_profile,
                trip_month=trip_month,
                trip_duration=trip_duration
            )
            
            response = self.rec_service.format_recommendations(recommendations)
            
            # Update state
            conversation_state['recommendation_state'] = 'showing_recommendations'
            conversation_state['current_recommendations'] = recommendations
            
            return response, conversation_state
        
        elif wants_different:
            # Ask what they want to change
            response = """Great! I love helping you explore new travel experiences! 🌟

What would you like to try differently this time? For example:
• **Budget**: "I want to splurge" or "I want to save money"
• **Activities**: "I want more adventure" or "I want to relax"
• **Style**: "I want luxury experiences" or "I want authentic local culture"
• **Companions**: "I'm traveling with family" or "I'm going solo"

Just tell me what you're in the mood for! ✨"""
            
            conversation_state['recommendation_state'] = 'waiting_preferences'  # Stay in this state
            return response, conversation_state
        
        else:
            # Try to interpret their response as preference changes
            preference_changes = message  # Use their full message as preference changes
            
            recommendations = self.rec_service.get_recommendations(
                user_profile=user_profile,
                trip_month=trip_month,
                trip_duration=trip_duration,
                preference_changes=preference_changes
            )
            
            response = f"Perfect! Based on your request for {preference_changes}, here are my recommendations:\n\n"
            response += self.rec_service.format_recommendations(recommendations)
            
            # Update state
            conversation_state['recommendation_state'] = 'showing_recommendations'
            conversation_state['current_recommendations'] = recommendations
            
            return response, conversation_state
    
    def handle_destination_selection(self, message: str, user_profile: Dict[str, Any], 
                                   conversation_state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle destination selection for itinerary creation"""
        
        selected_destination = self.detect_destination_selection(message)
        
        if selected_destination:
            # Get destination data
            destination_data = self.rec_service.get_destination_by_name(selected_destination)
            
            if destination_data:
                # Create itinerary using Bedrock
                itinerary = self.create_itinerary_with_bedrock(
                    destination_data=destination_data,
                    user_profile=user_profile,
                    trip_month=conversation_state.get('detected_month'),
                    trip_duration=conversation_state.get('detected_duration')
                )
                
                # Reset state
                conversation_state['recommendation_state'] = 'none'
                
                return itinerary, conversation_state
            else:
                # Destination not found
                response = f"""I couldn't find detailed information about {selected_destination}. 

Could you pick from the destinations I recommended above? Just say something like:
• "Tell me about Tokyo"
• "Create itinerary for Paris"
• "I'm interested in Bali"

Which one would you like to explore? 🌟"""
                
                return response, conversation_state
        
        else:
            # Ask for clarification
            response = """Which destination would you like to explore? 

Just tell me something like:
• "Tell me about Tokyo"
• "Create itinerary for the first one"
• "I'm interested in Paris"

Which destination caught your eye? ✨"""
            
            return response, conversation_state
    
    def create_itinerary_with_bedrock(self, destination_data: Dict[str, Any], 
                                    user_profile: Dict[str, Any],
                                    trip_month: str = None,
                                    trip_duration: str = None) -> str:
        """Create detailed itinerary using Bedrock with real destination data"""
        
        try:
            # Format user profile for prompt
            personalities = user_profile.get('traveler_types', [])
            budget = user_profile.get('budget_style', 'mid_range')
            companions = user_profile.get('travel_companions', 'solo')
            activities = user_profile.get('activity_preferences', [])
            
            # Create enhanced prompt with real data
            prompt = f"""Create a detailed travel itinerary for {destination_data['city']}, {destination_data['country']}.

**REAL DESTINATION DATA:**
- Description: {destination_data['short_description']}
- Budget Level: {destination_data['budget_level']}
- Ideal Duration: {destination_data['ideal_durations']}
- Culture Score: {destination_data['culture_score']}/100
- Adventure Score: {destination_data['adventure_score']}/100
- Nature Score: {destination_data['nature_score']}/100
- Food Score: {destination_data['cuisine_score']}/100
- Nightlife Score: {destination_data['nightlife_score']}/100

**TRAVELER PROFILE:**
- Travel Style: {', '.join(personalities)}
- Budget: {budget}
- Companions: {companions}
- Interests: {', '.join(activities)}

**TRIP DETAILS:**
- Duration: {trip_duration or 'flexible'}
- Month: {trip_month or 'flexible'}

**INSTRUCTIONS:**
Create a realistic, day-by-day itinerary that:
1. Focuses on the destination's highest-scoring activities that match the traveler's interests
2. Includes realistic costs appropriate for {destination_data['budget_level']} budget
3. Matches the traveler's style and preferences
4. Provides specific activity names and locations (not generic descriptions)
5. Includes cultural insights and local tips

**FORMAT:**
Use this exact format:

**{destination_data['city']}, {destination_data['country']} - Personalized Itinerary**

**Day 1: [Theme based on traveler interests]**
🌅 **Morning (9:00 AM - 12:00 PM)**
- **Activity**: [Specific activity/location name]
- **Why perfect for you**: [Connect to traveler's interests]
- **Cost**: $XX per person
- **Tip**: [Local insight]

🌞 **Afternoon (1:00 PM - 5:00 PM)**
- **Activity**: [Specific activity/location name]
- **Why perfect for you**: [Connect to traveler's interests]
- **Cost**: $XX per person

🌙 **Evening (6:00 PM - 10:00 PM)**
- **Dinner**: [Specific restaurant/area name]
- **Evening Activity**: [Specific activity]
- **Cost**: $XX per person

[Continue for 2-3 days based on duration]

**🏨 Accommodation Recommendation**
- **Hotel**: [Name and description matching budget]
- **Cost**: $XX per night
- **Why recommended**: [Match to traveler preferences]

**💰 Budget Summary**
- Accommodation: $XX ({trip_duration} trip)
- Meals: $XX (avg $XX per day)
- Activities: $XX
- Total: $XX per person

**🎒 Personalized Tips**
- [3-4 specific tips based on destination strengths and traveler style]

Create this itinerary now."""

            # Call Bedrock
            response = self.bedrock_service.create_travel_plan(
                prompt, 
                f"Traveler: {', '.join(personalities)}, {budget} budget, {companions} travel"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating itinerary with Bedrock: {e}")
            return f"I'd love to create a detailed itinerary for {destination_data['city']}, {destination_data['country']}, but I'm having some technical difficulties right now. This destination is perfect for {', '.join(user_profile.get('traveler_types', []))} travelers with its {destination_data['short_description']}. Please try again in a moment!"
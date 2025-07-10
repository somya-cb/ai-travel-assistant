"""Main Streamlit app for AI Travel Assistant MVP with Trip Context Integration"""

import streamlit as st

# Configure Streamlit page FIRST - before any other streamlit commands
st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import everything else
import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib
import uuid  # For unique user IDs

# Add src directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import our services and models
from models.simple_persona import SimpleTravelPersona
from services.couchbase_service import CouchbaseService
from services.bedrock_service import BedrockService

# NEW: Import Trip Context Manager
try:
    from services.trip_context_manager import TripContextManager
    TRIP_CONTEXT_AVAILABLE = True
except ImportError:
    TRIP_CONTEXT_AVAILABLE = False
    print("Trip Context Manager not available - using basic flow")

# Helper functions for clean display
def format_traveler_types(types_list):
    """Convert traveler type codes to readable names"""
    type_map = {
        "cultural_explorer": "Cultural Explorer",
        "adventure_seeker": "Adventure Seeker", 
        "luxury_traveler": "Luxury Traveler",
        "foodie": "Foodie",
        "nature_lover": "Nature Lover",
        "budget_backpacker": "Budget Backpacker",
        "wellness_guru": "Wellness Guru",
        "family_vacationer": "Family Vacationer"
    }
    return [type_map.get(t, t.replace('_', ' ').title()) for t in types_list]

def format_budget_style(budget):
    """Convert budget code to readable name"""
    budget_map = {
        "budget_conscious": "Budget-Conscious",
        "mid_range": "Mid-Range",
        "luxury": "Luxury"
    }
    return budget_map.get(budget, budget.replace('_', ' ').title())

def format_companions(companions):
    """Convert companion code to readable name"""
    companion_map = {
        "solo": "Solo",
        "couple": "Couple",
        "family_with_kids": "Family with Kids",
        "group_of_friends": "Group of Friends"
    }
    return companion_map.get(companions, companions.replace('_', ' ').title())

def format_activities(activities_list):
    """Convert activity codes to readable names"""
    activity_map = {
        "museums_culture": "Museums & Culture",
        "outdoor_adventure": "Outdoor & Adventure",
        "food_wine": "Food & Wine",
        "shopping": "Shopping",
        "nightlife": "Nightlife",
        "beaches": "Beaches",
        "historical_sites": "Historical Sites",
        "nature_wildlife": "Nature & Wildlife",
        "wellness_spa": "Wellness & Spa",
        "photography": "Photography"
    }
    return [activity_map.get(a, a.replace('_', ' ').title()) for a in activities_list]

# Debug function to check user data
def debug_user_data(couchbase_service, email: str):
    """Debug function to check what data exists for a user"""
    try:
        normalized_email = email.strip().lower()
        
        # Check for any records with this email
        all_query = f"""
        SELECT META().id as doc_id, user_profiles.* FROM `{couchbase_service.bucket_name}`.`{couchbase_service.scope_name}`.`{couchbase_service.user_profiles_collection_name}` as user_profiles
        WHERE user_profiles.email = $email
        """
        all_result = couchbase_service.cluster.query(all_query, email=normalized_email)
        all_records = [row for row in all_result]
        
        print(f"DEBUG for email {normalized_email}:")
        print(f"  Total records found: {len(all_records)}")
        
        for i, record in enumerate(all_records):
            print(f"  Record {i+1}:")
            print(f"    doc_id: {record.get('doc_id', 'N/A')}")
            print(f"    type: {record.get('type', 'None/Missing')}")
            print(f"    user_id: {record.get('user_id', 'N/A')}")
            print(f"    name: {record.get('name', 'N/A')}")
            print(f"    has traveler_types: {bool(record.get('traveler_types'))}")
            print(f"    completed: {record.get('completed', 'N/A')}")
            print(f"    profile_completed: {record.get('profile_completed', 'N/A')}")
        
        return all_records
        
    except Exception as e:
        print(f"Debug error: {e}")
        return None
def create_unique_user_id() -> str:
    """Create truly unique user ID"""
    return str(uuid.uuid4())

def find_user_by_email(couchbase_service, email: str):
    """Find existing user by email"""
    try:
        # Use proper query syntax to get all fields
        user_query = f"""
        SELECT user_profiles.* FROM `{couchbase_service.bucket_name}`.`{couchbase_service.scope_name}`.`{couchbase_service.user_profiles_collection_name}` as user_profiles
        WHERE user_profiles.email = $email AND user_profiles.type = 'user_record'
        LIMIT 1
        """
        
        result = couchbase_service.cluster.query(user_query, email=email)
        users = [row for row in result]
        
        if users:
            user_record = users[0]
            print(f"Found user record with user_id: {user_record.get('user_id')}")
            return user_record
        
        # Look for persona records (for backwards compatibility)
        persona_query = f"""
        SELECT user_profiles.* FROM `{couchbase_service.bucket_name}`.`{couchbase_service.scope_name}`.`{couchbase_service.user_profiles_collection_name}` as user_profiles
        WHERE user_profiles.email = $email AND (user_profiles.type = 'travel_persona' OR user_profiles.traveler_types IS NOT MISSING)
        LIMIT 1
        """
        
        persona_result = couchbase_service.cluster.query(persona_query, email=email)
        personas = [row for row in persona_result]
        
        if personas:
            persona_record = personas[0]
            user_id = persona_record.get('user_id')
            name = persona_record.get('name', 'User')
            
            if not user_id:
                print(f"Persona missing user_id, cannot create user record")
                return None
            
            print(f"Creating user record for existing persona: {user_id}")
            
            # Create user record
            user_data = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "profile_completed": True,
                "last_login": datetime.now().isoformat(),
                "type": "user_record"
            }
            
            doc_id = f"user::{user_id}"
            couchbase_service.user_profiles_collection.upsert(doc_id, user_data)
            return user_data
        
        # No records found
        return None
        
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None
        
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None

def create_new_user(couchbase_service, email: str, name: str) -> str:
    """Create new user with unique ID"""
    user_id = create_unique_user_id()
    
    user_record = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "profile_completed": False,
        "last_login": datetime.now().isoformat(),
        "type": "user_record"  # Add type for querying
    }
    
    # Save user record
    doc_id = f"user::{user_id}"
    try:
        couchbase_service.user_profiles_collection.upsert(doc_id, user_record)
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user_last_login(couchbase_service, user_id: str):
    """Update user's last login timestamp"""
    try:
        doc_id = f"user::{user_id}"
        result = couchbase_service.user_profiles_collection.get(doc_id)
        user_data = result.content_as[dict]
        user_data["last_login"] = datetime.now().isoformat()
        couchbase_service.user_profiles_collection.upsert(doc_id, user_data)
    except Exception as e:
        print(f"Error updating last login: {e}")

def save_persona_with_metadata(couchbase_service, persona, user_id):
    """Save persona with additional metadata"""
    persona_dict = persona.to_dict()
    
    # Add metadata
    persona_dict.update({
        "user_id": user_id,
        "email": st.session_state.get('user_email'),
        "completed": True,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "profile_version": 1,
        "type": "travel_persona"  # Add type for querying
    })
    
    return couchbase_service.save_persona(persona_dict, user_id)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize and cache services"""
    try:
        couchbase_service = CouchbaseService()
        bedrock_service = BedrockService()
        trip_context_manager = TripContextManager(couchbase_service) if TRIP_CONTEXT_AVAILABLE else None
        return couchbase_service, bedrock_service, trip_context_manager
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None

def main():
    """Main application function"""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'persona' not in st.session_state:
        st.session_state.persona = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_trip_id' not in st.session_state:  # NEW: Track current trip
        st.session_state.current_trip_id = None
    if 'awaiting_confirmation' not in st.session_state:  # NEW: Track confirmation state
        st.session_state.awaiting_confirmation = False
    
    # Get services
    couchbase_service, bedrock_service, trip_context_manager = get_services()
    
    if not couchbase_service or not bedrock_service:
        st.error("Failed to initialize services. Please check your configuration.")
        return
    
    # Route to appropriate page
    if st.session_state.current_page == "login":
        show_login(couchbase_service)
    elif st.session_state.current_page == "onboarding":
        show_onboarding(couchbase_service)
    elif st.session_state.current_page == "chat":
        show_chat_interface(couchbase_service, bedrock_service, trip_context_manager)

def show_login(couchbase_service):
    """Email-based login with unique user identification"""
    
    st.title("🧳 AI Travel Assistant")
    st.markdown("### Welcome! Please sign in")
    
    with st.form("login_form"):
        st.markdown("**Sign in to continue:**")
        
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email Address", placeholder="your.email@example.com")
        with col2:
            name = st.text_input("Full Name", placeholder="John Doe")
        
        submitted = st.form_submit_button("Continue", use_container_width=True)
        
        if submitted:
            # Validation
            if not email.strip() or not name.strip():
                st.error("Please enter both email and name")
                return
            
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
                return
            
            try:
                normalized_email = email.strip().lower()
                
                # Debug: Check what data exists
                debug_data = debug_user_data(couchbase_service, normalized_email)
                
                # Check if user exists by email
                existing_user = find_user_by_email(couchbase_service, normalized_email)
                
                if existing_user:
                    # Existing user found
                    user_id = existing_user["user_id"]
                    stored_name = existing_user["name"]
                    
                    # Update session
                    st.session_state.user_id = user_id
                    st.session_state.user_email = normalized_email
                    st.session_state.user_name = stored_name
                    
                    # Update last login
                    update_user_last_login(couchbase_service, user_id)
                    
                    # Check if they have a travel profile
                    persona_data = couchbase_service.get_persona(user_id)
                    
                    if persona_data and persona_data.get('completed', False):
                        # Existing user with complete profile - go to chat
                        try:
                            st.session_state.persona = SimpleTravelPersona.from_dict(persona_data)
                            st.session_state.current_page = "chat"
                            st.success(f"Welcome back, {stored_name}!")
                            
                            # Debug info
                            st.info(f"Debug: Found existing profile for {stored_name} (User ID: {user_id[:8]}...)")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error loading profile: {e}")
                            # If persona loading fails, go to onboarding
                            st.session_state.current_page = "onboarding"
                            st.info(f"Let's refresh your travel profile, {stored_name}.")
                            st.rerun()
                    else:
                        # Existing user without complete profile - go to onboarding
                        st.session_state.current_page = "onboarding"
                        st.info(f"Welcome back, {stored_name}! Let's complete your travel profile.")
                        st.rerun()
                
                else:
                    # New user
                    user_id = create_new_user(couchbase_service, normalized_email, name.strip())
                    
                    if user_id:
                        # Update session
                        st.session_state.user_id = user_id
                        st.session_state.user_email = normalized_email
                        st.session_state.user_name = name.strip()
                        
                        # Go to onboarding
                        st.session_state.current_page = "onboarding"
                        st.success(f"Welcome, {name}! Let's create your travel profile.")
                        st.rerun()
                    else:
                        st.error("Error creating account. Please try again.")
                
            except Exception as e:
                st.error(f"Error during login: {e}")

def show_onboarding(couchbase_service):
    """Show onboarding form for new users"""
    
    st.title("🧳 AI Travel Assistant")
    st.markdown(f"### Hi {st.session_state.user_name}! Let's create your travel profile")
    st.markdown("Tell us about your travel preferences so we can create personalized recommendations!")
    
    with st.form("travel_profile_form"):
        # Traveler Types
        st.markdown("**What describes you as a traveler?** (Select up to 3)")
        traveler_options = {
            "cultural_explorer": "🏛 Cultural Explorer - Museums, history, local traditions",
            "adventure_seeker": "🧗 Adventure Seeker - Outdoor activities, extreme sports",
            "luxury_traveler": "💎 Luxury Traveler - Premium experiences, high-end accommodations",
            "foodie": "🍲 Foodie - Local cuisine, cooking classes, food tours",
            "nature_lover": "🌿 Nature Lover - National parks, wildlife, outdoor activities",
            "budget_backpacker": "🎒 Budget Backpacker - Affordable travel, authentic experiences",
            "wellness_guru": "🧘 Wellness Guru - Spas, yoga, healthy living",
            "family_vacationer": "👨‍👩‍👧‍👦 Family Vacationer - Kid-friendly, family bonding"
        }
        
        selected_types = []
        cols = st.columns(2)
        for i, (key, description) in enumerate(traveler_options.items()):
            col = cols[i % 2]
            with col:
                if st.checkbox(description, key=f"type_{key}"):
                    selected_types.append(key)
        
        # Budget Style
        st.markdown("**What's your budget style?**")
        budget_style = st.radio(
            "Choose your budget preference:",
            ["budget_conscious", "mid_range", "luxury"],
            format_func=lambda x: {
                "budget_conscious": "💰 Budget-Conscious - Under $100/day",
                "mid_range": "💳 Mid-Range - $100-300/day", 
                "luxury": "💎 Luxury - $300+/day"
            }[x]
        )
        
        # Travel Companions
        st.markdown("**Who do you typically travel with?**")
        travel_companions = st.selectbox(
            "Select your travel style:",
            ["solo", "couple", "family_with_kids", "group_of_friends"],
            format_func=lambda x: {
                "solo": "👤 Solo - Independent travel",
                "couple": "💑 Couple - Romantic getaways",
                "family_with_kids": "👨‍👩‍👧‍👦 Family with Kids",
                "group_of_friends": "👥 Group of Friends"
            }[x]
        )
        
        # Activity Preferences
        st.markdown("**What activities do you enjoy?** (Select up to 5)")
        activity_options = {
            "museums_culture": "🏛 Museums & Culture",
            "outdoor_adventure": "🏔 Outdoor & Adventure",
            "food_wine": "🍷 Food & Wine",
            "shopping": "🛍 Shopping",
            "nightlife": "🌃 Nightlife",
            "beaches": "🏖 Beaches",
            "historical_sites": "🏛 Historical Sites",
            "nature_wildlife": "🦎 Nature & Wildlife",
            "wellness_spa": "🧘 Wellness & Spa",
            "photography": "📸 Photography"
        }
        
        selected_activities = []
        activity_cols = st.columns(3)
        for i, (key, description) in enumerate(activity_options.items()):
            col = activity_cols[i % 3]
            with col:
                if st.checkbox(description, key=f"activity_{key}"):
                    selected_activities.append(key)
        
        # Dietary Restrictions
        st.markdown("**Any dietary restrictions?**")
        dietary_options = ["no_restrictions", "vegetarian", "vegan", "gluten_free", "halal", "kosher"]
        dietary_restrictions = st.multiselect(
            "Select any that apply:",
            dietary_options,
            format_func=lambda x: {
                "no_restrictions": "🍽 No restrictions",
                "vegetarian": "🌱 Vegetarian",
                "vegan": "🌿 Vegan",
                "gluten_free": "🚫 Gluten-free",
                "halal": "🕌 Halal",
                "kosher": "✡️ Kosher"
            }[x]
        )
        
        # Submit button
        submitted = st.form_submit_button("Create My Profile", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            if len(selected_types) == 0:
                errors.append("Please select at least one travel type")
            if len(selected_types) > 3:
                errors.append("Please select up to 3 travel types only")
            if len(selected_activities) > 5:
                errors.append("Please select up to 5 activities only")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create persona with existing user_id
                persona = SimpleTravelPersona(
                    user_id=st.session_state.user_id,  # Use existing user_id
                    name=st.session_state.user_name,   # Use existing name
                    traveler_types=selected_types,
                    budget_style=budget_style,
                    travel_companions=travel_companions,
                    activity_preferences=selected_activities,
                    dietary_restrictions=dietary_restrictions,
                    completed=True
                )
                
                # Save with metadata
                if save_persona_with_metadata(couchbase_service, persona, st.session_state.user_id):
                    st.session_state.persona = persona
                    st.session_state.current_page = "chat"
                    st.success("Profile created successfully!")
                    st.rerun()
                else:
                    st.error("Error saving profile. Please try again.")

def show_chat_interface(couchbase_service, bedrock_service, trip_context_manager):
    """Enhanced chat interface with trip context support"""
    
    persona = st.session_state.persona
    
    # Sidebar with persona info
    with st.sidebar:
        st.title("🧳 Travel Assistant")
        st.markdown("### Your Profile")
        
        if persona:
            st.write(f"**Name:** {persona.name}")
            st.write(f"**Email:** {st.session_state.user_email}")
            
            # Format persona display properly
            formatted_types = format_traveler_types(persona.traveler_types)
            st.write(f"**Travel Style:** {', '.join(formatted_types)}")
            
            formatted_budget = format_budget_style(persona.budget_style)
            st.write(f"**Budget:** {formatted_budget}")
            
            formatted_companions = format_companions(persona.travel_companions)
            st.write(f"**Companions:** {formatted_companions}")
            
            if persona.activity_preferences:
                formatted_activities = format_activities(persona.activity_preferences)
                st.write(f"**Interests:** {', '.join(formatted_activities[:3])}{'...' if len(formatted_activities) > 3 else ''}")
            
            # NEW: Show current trip info if exists
            if st.session_state.current_trip_id and trip_context_manager:
                trip_context = couchbase_service.get_trip_context(st.session_state.current_trip_id)
                if trip_context:
                    st.markdown("---")
                    st.markdown("### Current Trip")
                    if trip_context.get('destination'):
                        st.write(f"**Destination:** {trip_context['destination']}")
                    if trip_context.get('duration'):
                        st.write(f"**Duration:** {trip_context['duration']}")
                    if trip_context.get('dates'):
                        st.write(f"**Dates:** {trip_context['dates']}")
            
            if st.button("✏️ Edit Profile"):
                st.session_state.current_page = "onboarding"
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.current_trip_id = None
            st.session_state.awaiting_confirmation = False
            st.rerun()
            
        if st.button("👤 Switch User"):
            # Reset user session
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.session_state.persona = None
            st.session_state.chat_history = []
            st.session_state.current_trip_id = None
            st.session_state.awaiting_confirmation = False
            st.session_state.current_page = "login"
            st.rerun()
    
    # Main chat interface
    st.title("✈️ AI Travel Assistant")
    
    # Welcome message
    if not st.session_state.chat_history and persona:
        formatted_types = format_traveler_types(persona.traveler_types)
        formatted_budget = format_budget_style(persona.budget_style)
        
        st.info(f"""
        👋 **Welcome back, {persona.name}!** 
        
        I'm your personal travel assistant. Based on your profile as a **{', '.join(formatted_types)}** with **{formatted_budget}** budget preferences, I'm ready to help you plan amazing trips!
        
        Just tell me where you'd like to go and when, and I'll create a personalized itinerary for you! 🌟
        """)
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Tell me about your travel plans..."):
        
        # Add user message to chat
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response with trip context
        with st.chat_message("assistant"):
            with st.spinner("Creating your personalized travel plan..."):
                try:
                    ai_response = process_user_message_with_context(
                        user_input, 
                        couchbase_service, 
                        bedrock_service, 
                        trip_context_manager, 
                        persona
                    )
                    
                    # Display AI response
                    st.write(ai_response)
                    
                    # Add AI response to chat history
                    ai_message = {
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.chat_history.append(ai_message)
                    
                    # Save chat messages to Couchbase
                    couchbase_service.save_chat_message(
                        st.session_state.user_id, 
                        user_message, 
                        st.session_state.current_trip_id
                    )
                    couchbase_service.save_chat_message(
                        st.session_state.user_id, 
                        ai_message, 
                        st.session_state.current_trip_id
                    )
                    
                except Exception as e:
                    error_message = f"I'm sorry, I encountered an error: {str(e)}"
                    st.error(error_message)

def process_user_message_with_context(user_input, couchbase_service, bedrock_service, trip_context_manager, persona):
    """Process user message with intelligent trip context handling"""
    
    if not trip_context_manager:
        # Fallback to basic response if trip context not available
        return process_basic_message(user_input, bedrock_service, persona)
    
    try:
        # Create persona summary
        formatted_types = format_traveler_types(persona.traveler_types)
        formatted_budget = format_budget_style(persona.budget_style)
        formatted_companions = format_companions(persona.travel_companions)
        formatted_activities = format_activities(persona.activity_preferences)
        persona_summary = f"Travel style: {', '.join(formatted_types)}; Budget: {formatted_budget}; Traveling: {formatted_companions}; Interests: {', '.join(formatted_activities)}"
        
        # Get current trip context if exists
        current_trip_context = None
        if st.session_state.current_trip_id:
            current_trip_context = couchbase_service.get_trip_context(st.session_state.current_trip_id)
        
        # Handle different conversation states
        if st.session_state.awaiting_confirmation:
            # User is responding to profile confirmation
            return handle_profile_confirmation_response(
                user_input, current_trip_context, trip_context_manager, 
                couchbase_service, bedrock_service, persona_summary
            )
        
        else:
            # Detect trip information in new message
            trip_info = trip_context_manager.detect_trip_info(user_input)
            
            # Check if we should ask for profile confirmation
            if trip_context_manager.should_ask_for_confirmation(trip_info, persona.to_dict()):
                return handle_new_trip_request(
                    trip_info, persona.to_dict(), trip_context_manager, 
                    couchbase_service, bedrock_service
                )
            
            # Handle other conversation types
            return bedrock_service.create_response_with_context(
                user_input, "GENERAL_CHAT", persona_summary
            )
    
    except Exception as e:
        print(f"Error in trip context processing: {e}")
        return process_basic_message(user_input, bedrock_service, persona)

def handle_new_trip_request(trip_info, user_profile, trip_context_manager, couchbase_service, bedrock_service):
    """Handle new trip request with profile confirmation"""
    
    # Create trip context
    trip_id = couchbase_service.create_trip_context(
        user_id=st.session_state.user_id,
        base_profile=user_profile,
        destination=trip_info.get('destination'),
        duration=trip_info.get('duration'),
        dates=trip_info.get('dates')
    )
    
    if trip_id:
        st.session_state.current_trip_id = trip_id
        st.session_state.awaiting_confirmation = True
        
        # Generate profile confirmation message
        confirmation_message = trip_context_manager.generate_profile_confirmation(
            user_profile, trip_info
        )
        
        return confirmation_message
    else:
        return "I'd love to help you plan this trip! Could you tell me more about where you'd like to go?"

def handle_profile_confirmation_response(user_input, trip_context, trip_context_manager, 
                                       couchbase_service, bedrock_service, persona_summary):
    """Handle user's response to profile confirmation"""
    
    # Detect override intent
    override_result = trip_context_manager.detect_override_intent(user_input)
    
    if override_result["action"] == "CREATE_TRIP_CONTEXT":
        # Update trip context with overrides
        updates = {
            "overrides": override_result["overrides"],
            "confirmation_step": "details_gathering"
        }
        couchbase_service.update_trip_context(st.session_state.current_trip_id, updates)
        
        # Update trip info if provided
        trip_context_manager.update_trip_with_new_info(st.session_state.current_trip_id, user_input)
        
        # Get updated context
        updated_context = couchbase_service.get_trip_context(st.session_state.current_trip_id)
        
        # Check if we can create itinerary or need more info
        if trip_context_manager.should_create_itinerary(updated_context):
            st.session_state.awaiting_confirmation = False
            enhanced_persona_summary = trip_context_manager.create_persona_summary_from_context(updated_context)
            return bedrock_service._create_detailed_itinerary(updated_context, enhanced_persona_summary)
        else:
            missing_info = trip_context_manager.get_missing_info(updated_context)
            follow_up = trip_context_manager.generate_info_request(missing_info, updated_context)
            return override_result.get("follow_up", follow_up)
    
    else:  # USE_PROFILE_DEFAULTS
        st.session_state.awaiting_confirmation = False
        
        # Update trip to use profile defaults
        updates = {"confirmation_step": "details_gathering"}
        couchbase_service.update_trip_context(st.session_state.current_trip_id, updates)
        
        # Update trip info if provided
        trip_context_manager.update_trip_with_new_info(st.session_state.current_trip_id, user_input)
        
        # Get updated context
        updated_context = couchbase_service.get_trip_context(st.session_state.current_trip_id)
        
        # Check if we can create itinerary
        if trip_context_manager.should_create_itinerary(updated_context):
            return bedrock_service._create_detailed_itinerary(updated_context, persona_summary)
        else:
            missing_info = trip_context_manager.get_missing_info(updated_context)
            return trip_context_manager.generate_info_request(missing_info, updated_context)

def process_basic_message(user_input, bedrock_service, persona):
    """Fallback message processing without trip context"""
    
    formatted_types = format_traveler_types(persona.traveler_types)
    formatted_budget = format_budget_style(persona.budget_style)
    formatted_companions = format_companions(persona.travel_companions)
    formatted_activities = format_activities(persona.activity_preferences)
    persona_summary = f"Travel style: {', '.join(formatted_types)}; Budget: {formatted_budget}; Traveling: {formatted_companions}; Interests: {', '.join(formatted_activities)}"
    
    return bedrock_service.create_travel_plan(user_input, persona_summary)

if __name__ == "__main__":
    main()

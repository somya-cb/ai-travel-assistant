# ==========================================
# app/pages/onboarding.py
# ==========================================
"""Travel persona onboarding flow"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent.parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from models.travel_persona import *
from services.persona_service import PersonaService

def show_onboarding():
    """Main onboarding flow"""
    
    st.title("🧳 Welcome to Your AI Travel Assistant!")
    st.markdown("### Let's create your personalized travel profile")
    
    # Initialize session state
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    if 'onboarding_responses' not in st.session_state:
        st.session_state.onboarding_responses = {}
    
    # Progress bar
    total_steps = 12
    progress = st.session_state.onboarding_step / total_steps
    st.progress(progress)
    st.write(f"Step {st.session_state.onboarding_step + 1} of {total_steps}")
    
    # Show current question
    if st.session_state.onboarding_step == 0:
        show_question_1()
    elif st.session_state.onboarding_step == 1:
        show_question_2()
    elif st.session_state.onboarding_step == 2:
        show_question_3()
    elif st.session_state.onboarding_step == 3:
        show_question_4()
    elif st.session_state.onboarding_step == 4:
        show_question_5()
    elif st.session_state.onboarding_step == 5:
        show_question_6()
    elif st.session_state.onboarding_step == 6:
        show_question_7()
    elif st.session_state.onboarding_step == 7:
        show_question_8()
    elif st.session_state.onboarding_step == 8:
        show_question_9()
    elif st.session_state.onboarding_step == 9:
        show_question_10()
    elif st.session_state.onboarding_step == 10:
        show_question_11()
    elif st.session_state.onboarding_step == 11:
        show_question_12()
    else:
        show_completion()

def show_question_1():
    """Question 1: Traveler Types"""
    st.header("What describes you as a traveler?")
    st.markdown("*Select up to 3 travel types that resonate with you most.*")
    
    traveler_options = [
        ("cultural_explorer", "🏛 The Cultural Explorer", "Museums, historical sites, local traditions"),
        ("adventure_seeker", "🧗 The Adventure Seeker", "Extreme sports, challenging activities, adrenaline rush"),
        ("luxury_traveler", "💎 The Luxury Traveler", "Premium experiences, high-end accommodations, exclusive access"),
        ("social_butterfly", "🎉 The Social Butterfly", "Meeting locals, group activities, vibrant nightlife"),
        ("nature_lover", "🌿 The Nature Lover", "National parks, wildlife, outdoor activities"),
        ("budget_backpacker", "🎒 The Budget Backpacker", "Affordable travel, authentic experiences, local transportation"),
        ("wellness_guru", "🧘 The Wellness Guru", "Spas, yoga retreats, healthy living, mindfulness"),
        ("foodie", "🍲 The Foodie", "Local cuisine, cooking classes, food tours, restaurants"),
        ("solo_wanderer", "👤 The Solo Wanderer", "Independent exploration, self-discovery, flexible itineraries"),
        ("family_vacationer", "👨‍👩‍👧‍👦 The Family Vacationer", "Kid-friendly activities, family bonding, safe destinations"),
    ]
    
    selected_types = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(traveler_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"traveler_{value}"):
                selected_types.append(value)
                st.caption(description)
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other (describe your travel style)")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your travel style:", key="traveler_custom")
    
    # Validation and navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if len(selected_types) > 3:
            st.error("Please select up to 3 options only")
        elif len(selected_types) == 0 and not custom_text:
            st.warning("Please select at least one travel type")
        else:
            if st.button("Next →", use_container_width=True):
                st.session_state.onboarding_responses['traveler_types'] = selected_types
                if custom_text:
                    st.session_state.onboarding_responses['traveler_types_custom'] = custom_text
                st.session_state.onboarding_step += 1
                st.rerun()

def show_question_2():
    """Question 2: Vacation Experience"""
    st.header("What's your ideal vacation experience?")
    st.markdown("*Choose your primary preference*")
    
    experience_options = [
        ("cultural_immersion", "🏛 Cultural Immersion", "Deep dive into local history, art, and traditions"),
        ("beach_relaxation", "🌊 Beach & Relaxation", "Sun, sand, and leisure activities"),
        ("nature_adventure", "🏔 Nature & Adventure", "Hiking, wildlife, outdoor exploration"),
        ("city_discovery", "🏙 City Discovery", "Urban exploration, architecture, modern attractions"),
        ("culinary_journey", "🍷 Culinary Journey", "Food-focused travel, wine tours, cooking experiences"),
        ("wellness_retreat", "🧘 Wellness & Retreat", "Spa treatments, meditation, health-focused activities"),
    ]
    
    selected_experience = st.radio(
        "Select your primary vacation preference:",
        options=[option[0] for option in experience_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in experience_options if opt[0] == x), x),
        key="vacation_experience"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other vacation experience")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your ideal vacation:", key="vacation_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['vacation_experience'] = selected_experience
            if custom_text:
                st.session_state.onboarding_responses['vacation_experience_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_3():
    """Question 3: Accommodation Style"""
    st.header("What's your accommodation style preference?")
    st.markdown("*Select all that apply*")
    
    accommodation_options = [
        ("luxury_hotels", "🏨 Luxury Hotels", "5-star service, premium amenities"),
        ("boutique_hotels", "🏩 Boutique Hotels", "Unique character, personalized service"),
        ("vacation_rentals", "🏠 Vacation Rentals", "Apartments, houses, local neighborhoods"),
        ("unique_stays", "🏕 Unique Stays", "Treehouses, glamping, unusual accommodations"),
        ("budget_hotels", "🏨 Budget Hotels/Hostels", "Clean, affordable, basic amenities"),
        ("camping", "⛺ Camping", "Tents, RVs, outdoor sleeping"),
        ("resorts", "🏖 Resorts", "All-inclusive, beach/mountain resorts"),
        ("local_stays", "🏡 Local Stays", "Homestays, guesthouses, family-run places"),
    ]
    
    selected_accommodations = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(accommodation_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"accommodation_{value}"):
                selected_accommodations.append(value)
                st.caption(description)
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other accommodation preference")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your accommodation preference:", key="accommodation_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if len(selected_accommodations) == 0 and not custom_text:
            st.warning("Please select at least one accommodation type")
        else:
            if st.button("Next →", use_container_width=True):
                st.session_state.onboarding_responses['accommodation_preferences'] = selected_accommodations
                if custom_text:
                    st.session_state.onboarding_responses['accommodation_preferences_custom'] = custom_text
                st.session_state.onboarding_step += 1
                st.rerun()

def show_question_4():
    """Question 4: Travel Companions"""
    st.header("Who do you typically travel with?")
    st.markdown("*Choose your most common travel style*")
    
    companion_options = [
        ("solo", "👤 Solo", "Independent travel, personal exploration"),
        ("romantic_partner", "💑 Romantic Partner", "Couple's getaways, intimate experiences"),
        ("family_with_kids", "👨‍👩‍👧‍👦 Family with Kids", "Child-friendly activities and accommodations"),
        ("group_of_friends", "👥 Group of Friends", "Shared experiences, group activities"),
        ("organized_groups", "🎓 Organized Groups", "Tours, travel groups, structured itineraries"),
        ("extended_family", "👨‍👩‍👧‍👦 Extended Family", "Multi-generational trips"),
    ]
    
    selected_companion = st.radio(
        "Select your typical travel companion:",
        options=[option[0] for option in companion_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in companion_options if opt[0] == x), x),
        key="travel_companions"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other travel companion type")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe who you travel with:", key="companions_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['typical_companions'] = selected_companion
            if custom_text:
                st.session_state.onboarding_responses['typical_companions_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_5():
    """Question 5: Budget Style"""
    st.header("What's your spending budget style?")
    st.markdown("*Select your typical approach*")
    
    budget_options = [
        ("budget_conscious", "💰 Budget-Conscious", "Under $100/day, seek deals and discounts"),
        ("mid_range", "💳 Mid-Range", "$100-300/day, balance of comfort and value"),
        ("luxury", "💎 Luxury", "$300-500/day, premium experiences matter"),
        ("ultra_luxury", "👑 Ultra-Luxury", "$500+/day, money is no object"),
        ("depends_on_trip", "🎯 Depends on Trip", "Budget varies by destination and purpose"),
    ]
    
    selected_budget = st.radio(
        "Select your budget style:",
        options=[option[0] for option in budget_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in budget_options if opt[0] == x), x),
        key="budget_style"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other budget approach")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your budget approach:", key="budget_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['budget_style'] = selected_budget
            if custom_text:
                st.session_state.onboarding_responses['budget_style_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_6():
    """Question 6: Daily Rhythm"""
    st.header("What's your daily rhythm preference?")
    st.markdown("*Choose what describes you best*")
    
    rhythm_options = [
        ("early_bird", "🌅 Early Bird", "Up at sunrise, make the most of daylight"),
        ("day_explorer", "🌞 Day Explorer", "Active during typical daytime hours"),
        ("evening_person", "🌆 Evening Person", "Prefer afternoon/evening activities"),
        ("night_owl", "🌙 Night Owl", "Love nightlife, late dinners, evening entertainment"),
        ("flexible", "🔄 Flexible", "Adapt to destination and activities"),
    ]
    
    selected_rhythm = st.radio(
        "Select your daily rhythm:",
        options=[option[0] for option in rhythm_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in rhythm_options if opt[0] == x), x),
        key="daily_rhythm"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other daily rhythm")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your daily rhythm:", key="rhythm_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['daily_rhythm'] = selected_rhythm
            if custom_text:
                st.session_state.onboarding_responses['daily_rhythm_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_7():
    """Question 7: Dining Preferences"""
    st.header("What's your dining preference style?")
    st.markdown("*Select all that apply*")
    
    dining_options = [
        ("fine_dining", "🍽 Fine Dining", "Michelin stars, upscale restaurants"),
        ("street_food", "🍜 Street Food", "Local markets, food stalls, authentic flavors"),
        ("local_favorites", "🏠 Local Favorites", "Where locals eat, hidden gems"),
        ("international_cuisine", "🌍 International Cuisine", "Familiar foods, hotel restaurants"),
        ("healthy_options", "🥗 Healthy Options", "Organic, vegetarian, wellness-focused"),
        ("food_drink_tours", "🍺 Food & Drink Tours", "Guided culinary experiences"),
        ("cooking_classes", "🍳 Cooking Classes", "Learn to make local dishes"),
    ]
    
    selected_dining = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(dining_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"dining_{value}"):
                selected_dining.append(value)
                st.caption(description)
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other dining preference")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your dining preference:", key="dining_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if len(selected_dining) == 0 and not custom_text:
            st.warning("Please select at least one dining preference")
        else:
            if st.button("Next →", use_container_width=True):
                st.session_state.onboarding_responses['dining_styles'] = selected_dining
                if custom_text:
                    st.session_state.onboarding_responses['dining_styles_custom'] = custom_text
                st.session_state.onboarding_step += 1
                st.rerun()

def show_question_8():
    """Question 8: Activity Preferences"""
    st.header("What activities excite you most?")
    st.markdown("*Select up to 5 that appeal to you*")
    
    activity_options = [
        ("beach_activities", "🏖 Beach Activities", "Swimming, water sports, sunbathing"),
        ("hiking_trekking", "🥾 Hiking & Trekking", "Nature trails, mountain climbing"),
        ("arts_culture", "🎭 Arts & Culture", "Museums, galleries, theater, music"),
        ("shopping", "🛍 Shopping", "Local markets, boutiques, souvenirs"),
        ("food_wine", "🍷 Food & Wine", "Tastings, tours, culinary experiences"),
        ("nightlife", "🌃 Nightlife", "Bars, clubs, live music, entertainment"),
        ("historical_sites", "🏛 Historical Sites", "Ancient ruins, monuments, heritage sites"),
        ("wildlife_nature", "🦎 Wildlife & Nature", "Safaris, bird watching, natural reserves"),
        ("adventure_sports", "🚁 Adventure Sports", "Skydiving, bungee jumping, extreme activities"),
        ("photography", "📸 Photography", "Scenic spots, Instagram-worthy locations"),
        ("wellness", "🧘 Wellness", "Spas, yoga, meditation, relaxation"),
        ("festivals_events", "🎪 Festivals & Events", "Local celebrations, concerts, seasonal events"),
    ]
    
    selected_activities = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(activity_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"activity_{value}"):
                selected_activities.append(value)
                st.caption(description)
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other activities")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe other activities you enjoy:", key="activities_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if len(selected_activities) > 5:
            st.error("Please select up to 5 activities only")
        elif len(selected_activities) == 0 and not custom_text:
            st.warning("Please select at least one activity")
        else:
            if st.button("Next →", use_container_width=True):
                st.session_state.onboarding_responses['activity_preferences'] = selected_activities
                if custom_text:
                    st.session_state.onboarding_responses['activity_preferences_custom'] = custom_text
                st.session_state.onboarding_step += 1
                st.rerun()

def show_question_9():
    """Question 9: Exploration Style"""
    st.header("How do you prefer to explore destinations?")
    st.markdown("*Choose your exploration style*")
    
    exploration_options = [
        ("independent_exploration", "🗺 Independent Exploration", "Self-guided, flexible itinerary"),
        ("guided_tours", "👥 Guided Tours", "Structured tours with local guides"),
        ("digital_guided", "📱 Digital Guided", "Apps, audio guides, self-paced with tech"),
        ("walking_tours", "🚶 Walking Tours", "On foot, intimate neighborhood exploration"),
        ("group_tours", "🚌 Group Tours", "Bus tours, organized group activities"),
        ("active_exploration", "🏃 Active Exploration", "Biking, hiking, adventure-based discovery"),
        ("local_recommendations", "🎯 Local Recommendations", "Ask locals, spontaneous discoveries"),
    ]
    
    selected_exploration = st.radio(
        "Select your exploration style:",
        options=[option[0] for option in exploration_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in exploration_options if opt[0] == x), x),
        key="exploration_style"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other exploration style")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your exploration style:", key="exploration_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['exploration_style'] = selected_exploration
            if custom_text:
                st.session_state.onboarding_responses['exploration_style_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_10():
    """Question 10: Planning Style"""
    st.header("What's your planning style?")
    st.markdown("*Choose what describes you best*")
    
    planning_options = [
        ("detailed_planner", "📋 Detailed Planner", "Every hour scheduled, reservations made in advance"),
        ("structured_flexibility", "🎯 Structured Flexibility", "Key activities planned, time for spontaneity"),
        ("go_with_flow", "🌊 Go with the Flow", "Minimal planning, decide day-by-day"),
        ("destination_focused", "📍 Destination Focused", "Plan must-sees, fill in gaps organically"),
        ("spontaneous_adventurer", "🎲 Spontaneous Adventurer", "Last-minute decisions, embrace uncertainty"),
    ]
    
    selected_planning = st.radio(
        "Select your planning style:",
        options=[option[0] for option in planning_options],
        format_func=lambda x: next((f"{opt[1]} - {opt[2]}" for opt in planning_options if opt[0] == x), x),
        key="planning_style"
    )
    
    # Custom option
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other planning style")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe your planning style:", key="planning_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['planning_style'] = selected_planning
            if custom_text:
                st.session_state.onboarding_responses['planning_style_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_11():
    """Question 11: Dietary Restrictions"""
    st.header("Any dietary restrictions or preferences?")
    st.markdown("*Select all that apply*")
    
    dietary_options = [
        ("no_restrictions", "🥩 No Restrictions", "Eat everything"),
        ("vegetarian", "🌱 Vegetarian", "No meat"),
        ("vegan", "🌿 Vegan", "No animal products"),
        ("pescatarian", "🐟 Pescatarian", "Fish but no meat"),
        ("gluten_free", "🍞 Gluten-Free", "Celiac or gluten sensitivity"),
        ("lactose_free", "🥛 Lactose-Free", "Dairy restrictions"),
        ("religious_dietary", "🕌 Religious Dietary Laws", "Halal, Kosher, etc."),
    ]
    
    selected_dietary = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(dietary_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"dietary_{value}"):
                selected_dietary.append(value)
                st.caption(description)
    
    # Food allergies input
    st.markdown("---")
    allergies_enabled = st.checkbox("🚫 Food Allergies")
    allergies_text = ""
    if allergies_enabled:
        allergies_text = st.text_input("Please specify your food allergies:", key="food_allergies")
    
    # Custom dietary restrictions
    custom_enabled = st.checkbox("➕ Other dietary restrictions")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe other dietary restrictions:", key="dietary_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state.onboarding_responses['dietary_restrictions'] = selected_dietary
            if allergies_text:
                st.session_state.onboarding_responses['food_allergies'] = allergies_text
            if custom_text:
                st.session_state.onboarding_responses['dietary_restrictions_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_question_12():
    """Question 12: Accessibility Needs"""
    st.header("Any accessibility needs or preferences?")
    st.markdown("*Select all that apply*")
    
    accessibility_options = [
        ("no_special_needs", "🌿 No Special Needs", "Standard accessibility is sufficient"),
        ("mobility_assistance", "♿ Mobility Assistance", "Wheelchair accessible accommodations/activities"),
        ("hearing_assistance", "👂 Hearing Assistance", "Sign language, visual aids"),
        ("vision_assistance", "👁 Vision Assistance", "Audio descriptions, tactile experiences"),
        ("physical_limitations", "🩼 Physical Limitations", "Limited walking, need frequent rest"),
        ("cognitive_considerations", "🧠 Cognitive Considerations", "Clear instructions, simple navigation"),
    ]
    
    selected_accessibility = []
    
    # Create columns for better layout
    cols = st.columns(2)
    for i, (value, label, description) in enumerate(accessibility_options):
        col = cols[i % 2]
        with col:
            if st.checkbox(label, key=f"accessibility_{value}"):
                selected_accessibility.append(value)
                st.caption(description)
    
    # Custom accessibility needs
    st.markdown("---")
    custom_enabled = st.checkbox("➕ Other accessibility needs")
    custom_text = ""
    if custom_enabled:
        custom_text = st.text_input("Describe other accessibility needs:", key="accessibility_custom")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col3:
        if st.button("Complete Profile →", use_container_width=True):
            st.session_state.onboarding_responses['accessibility_needs'] = selected_accessibility
            if custom_text:
                st.session_state.onboarding_responses['accessibility_needs_custom'] = custom_text
            st.session_state.onboarding_step += 1
            st.rerun()

def show_completion():
    """Show completion page and create persona"""
    st.header("🎉 Profile Complete!")
    st.markdown("### Your personalized travel profile has been created!")
    
    # Create persona from responses
    persona_service = PersonaService()
    user_id = st.session_state.get('user_id', 'demo_user')  # In production, get from auth
    
    try:
        persona = persona_service.create_persona_from_responses(
            user_id, 
            st.session_state.onboarding_responses
        )
        
        # Store persona in session state
        st.session_state.travel_persona = persona
        st.session_state.persona_completed = True
        
        # Display persona summary
        st.markdown("## 📊 Your Travel Persona Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎭 Your Travel Types")
            for traveler_type in persona.traveler_types:
                type_labels = {
                    TravelerType.CULTURAL_EXPLORER: "🏛 Cultural Explorer",
                    TravelerType.ADVENTURE_SEEKER: "🧗 Adventure Seeker",
                    TravelerType.LUXURY_TRAVELER: "💎 Luxury Traveler",
                    TravelerType.SOCIAL_BUTTERFLY: "🎉 Social Butterfly",
                    TravelerType.NATURE_LOVER: "🌿 Nature Lover",
                    TravelerType.BUDGET_BACKPACKER: "🎒 Budget Backpacker",
                    TravelerType.WELLNESS_GURU: "🧘 Wellness Guru",
                    TravelerType.FOODIE: "🍲 Foodie",
                    TravelerType.SOLO_WANDERER: "👤 Solo Wanderer",
                    TravelerType.FAMILY_VACATIONER: "👨‍👩‍👧‍👦 Family Vacationer"
                }
                st.write(f"• {type_labels.get(traveler_type, traveler_type.value)}")
            
            st.markdown("### 🏨 Accommodation Style")
            if persona.accommodation_preferences:
                for acc_type in persona.accommodation_preferences:
                    acc_labels = {
                        AccommodationType.LUXURY_HOTELS: "🏨 Luxury Hotels",
                        AccommodationType.BOUTIQUE_HOTELS: "🏩 Boutique Hotels",
                        AccommodationType.VACATION_RENTALS: "🏠 Vacation Rentals",
                        AccommodationType.UNIQUE_STAYS: "🏕 Unique Stays",
                        AccommodationType.BUDGET_HOTELS: "🏨 Budget Hotels/Hostels",
                        AccommodationType.CAMPING: "⛺ Camping",
                        AccommodationType.RESORTS: "🏖 Resorts",
                        AccommodationType.LOCAL_STAYS: "🏡 Local Stays"
                    }
                    st.write(f"• {acc_labels.get(acc_type, acc_type.value)}")
            
            st.markdown("### 💰 Budget Style")
            if persona.budget_style:
                budget_labels = {
                    BudgetStyle.BUDGET_CONSCIOUS: "💰 Budget-Conscious ($50-100/day)",
                    BudgetStyle.MID_RANGE: "💳 Mid-Range ($100-300/day)",
                    BudgetStyle.LUXURY: "💎 Luxury ($300-500/day)",
                    BudgetStyle.ULTRA_LUXURY: "👑 Ultra-Luxury ($500+/day)",
                    BudgetStyle.DEPENDS_ON_TRIP: "🎯 Depends on Trip"
                }
                st.write(budget_labels.get(persona.budget_style, persona.budget_style.value))
        
        with col2:
            st.markdown("### 🎯 Favorite Activities")
            if persona.activity_preferences:
                activity_labels = {
                    ActivityType.BEACH_ACTIVITIES: "🏖 Beach Activities",
                    ActivityType.HIKING_TREKKING: "🥾 Hiking & Trekking",
                    ActivityType.ARTS_CULTURE: "🎭 Arts & Culture",
                    ActivityType.SHOPPING: "🛍 Shopping",
                    ActivityType.FOOD_WINE: "🍷 Food & Wine",
                    ActivityType.NIGHTLIFE: "🌃 Nightlife",
                    ActivityType.HISTORICAL_SITES: "🏛 Historical Sites",
                    ActivityType.WILDLIFE_NATURE: "🦎 Wildlife & Nature",
                    ActivityType.ADVENTURE_SPORTS: "🚁 Adventure Sports",
                    ActivityType.PHOTOGRAPHY: "📸 Photography",
                    ActivityType.WELLNESS: "🧘 Wellness",
                    ActivityType.FESTIVALS_EVENTS: "🎪 Festivals & Events"
                }
                for activity in persona.activity_preferences:
                    st.write(f"• {activity_labels.get(activity, activity.value)}")
            
            st.markdown("### 🕐 Daily Rhythm")
            if persona.daily_rhythm:
                rhythm_labels = {
                    DailyRhythm.EARLY_BIRD: "🌅 Early Bird",
                    DailyRhythm.DAY_EXPLORER: "🌞 Day Explorer",
                    DailyRhythm.EVENING_PERSON: "🌆 Evening Person",
                    DailyRhythm.NIGHT_OWL: "🌙 Night Owl",
                    DailyRhythm.FLEXIBLE: "🔄 Flexible"
                }
                st.write(rhythm_labels.get(persona.daily_rhythm, persona.daily_rhythm.value))
            
            st.markdown("### 👥 Travel Companions")
            if persona.typical_companions:
                companion_labels = {
                    TravelCompanion.SOLO: "👤 Solo",
                    TravelCompanion.ROMANTIC_PARTNER: "💑 Romantic Partner",
                    TravelCompanion.FAMILY_WITH_KIDS: "👨‍👩‍👧‍👦 Family with Kids",
                    TravelCompanion.GROUP_OF_FRIENDS: "👥 Group of Friends",
                    TravelCompanion.ORGANIZED_GROUPS: "🎓 Organized Groups",
                    TravelCompanion.EXTENDED_FAMILY: "👨‍👩‍👧‍👦 Extended Family"
                }
                st.write(companion_labels.get(persona.typical_companions, persona.typical_companions.value))
        
        # Show special considerations if any
        if persona.dietary_restrictions or persona.accessibility_needs:
            st.markdown("## 🔧 Special Considerations")
            
            if persona.dietary_restrictions:
                st.markdown("### 🍽 Dietary Restrictions")
                for restriction in persona.dietary_restrictions:
                    st.write(f"• {restriction.replace('_', ' ').title()}")
            
            if persona.accessibility_needs:
                st.markdown("### ♿ Accessibility Needs")
                for need in persona.accessibility_needs:
                    st.write(f"• {need.replace('_', ' ').title()}")
        
        # Show custom responses if any
        custom_responses = {k: v for k, v in st.session_state.onboarding_responses.items() 
                          if k.endswith('_custom') and v}
        if custom_responses:
            st.markdown("## 💭 Your Custom Responses")
            for key, value in custom_responses.items():
                clean_key = key.replace('_custom', '').replace('_', ' ').title()
                st.write(f"**{clean_key}:** {value}")
        
        st.markdown("---")
        st.success("🎯 **Your AI Travel Assistant is now personalized!** All future trip recommendations will be tailored to your unique travel style.")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                # Reset onboarding
                st.session_state.onboarding_step = 0
                st.session_state.onboarding_responses = {}
                st.session_state.persona_completed = False
                if 'travel_persona' in st.session_state:
                    del st.session_state.travel_persona
                st.rerun()
        
        with col2:
            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state.onboarding_step = 0  # Go back to editing
                st.rerun()
        
        with col3:
            if st.button("🧳 Start Planning!", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        
        # Show recommendation weights (for development/debugging)
        with st.expander("🔍 View Recommendation Weights (Development)"):
            st.write("**Activity Weights:**")
            st.json(persona.activity_weights)
            st.write("**Budget Range:**")
            st.json(persona.budget_range)
            st.write("**Accommodation Filters:**")
            st.json(persona.get_accommodation_filter())
    
    except Exception as e:
        st.error(f"Error creating persona: {str(e)}")
        st.markdown("### 🔧 Debug Information")
        st.json(st.session_state.onboarding_responses)

# ==========================================
# app/main.py (Updated)
# ==========================================
"""
Updated main app with onboarding flow
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import modules
from pages.onboarding import show_onboarding
from services.itinerary_service import ItineraryService
from services.ai_service import AIService
from models.travel_persona import TravelPersona

# Configure Streamlit page
st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "onboarding"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "demo_user"  # In production, get from auth
    if 'persona_completed' not in st.session_state:
        st.session_state.persona_completed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'bookings' not in st.session_state:
        st.session_state.bookings = []
    if 'current_itinerary' not in st.session_state:
        st.session_state.current_itinerary = None
    
    # Check if persona is completed
    if not st.session_state.persona_completed and 'travel_persona' not in st.session_state:
        st.session_state.current_page = "onboarding"
    
    # Navigation
    if st.session_state.current_page == "onboarding":
        show_onboarding()
    elif st.session_state.current_page == "chat":
        show_chat_interface()
    else:
        show_onboarding()

def show_chat_interface():
    """Show the main chat interface with persona-driven recommendations"""
    
    # Initialize services
    itinerary_service = ItineraryService()
    ai_service = AIService()
    
    # Sidebar with persona summary
    with st.sidebar:
        st.title("🧳 Travel Assistant")
        st.markdown("### Your AI-powered travel companion")
        
        # Show persona summary
        if 'travel_persona' in st.session_state:
            persona = st.session_state.travel_persona
            st.markdown("### 👤 Your Travel Profile")
            
            # Show top traveler types
            if persona.traveler_types:
                st.write("**Travel Style:**")
                for traveler_type in persona.traveler_types[:2]:  # Show top 2
                    type_emojis = {
                        "cultural_explorer": "🏛",
                        "adventure_seeker": "🧗",
                        "luxury_traveler": "💎",
                        "social_butterfly": "🎉",
                        "nature_lover": "🌿",
                        "budget_backpacker": "🎒",
                        "wellness_guru": "🧘",
                        "foodie": "🍲",
                        "solo_wanderer": "👤",
                        "family_vacationer": "👨‍👩‍👧‍👦"
                    }
                    emoji = type_emojis.get(traveler_type.value, "🎯")
                    name = traveler_type.value.replace('_', ' ').title()
                    st.write(f"{emoji} {name}")
            
            # Show budget style
            if persona.budget_style:
                budget_emojis = {
                    "budget_conscious": "💰",
                    "mid_range": "💳",
                    "luxury": "💎",
                    "ultra_luxury": "👑",
                    "depends_on_trip": "🎯"
                }
                emoji = budget_emojis.get(persona.budget_style.value, "💰")
                name = persona.budget_style.value.replace('_', ' ').title()
                st.write(f"**Budget:** {emoji} {name}")
            
            # Edit profile button
            if st.button("✏️ Edit Profile"):
                st.session_state.current_page = "onboarding"
                st.session_state.persona_completed = False
                st.rerun()
        
        st.markdown("---")
        
        # Booking history
        st.markdown("### 📋 Recent Bookings")
        if st.session_state.bookings:
            for booking in st.session_state.bookings[-3:]:  # Show last 3 bookings
                st.write(f"✅ {booking['type']}: {booking['name']}")
        else:
            st.write("No bookings yet")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.current_itinerary = None
            st.rerun()

    # Main interface
    st.title("✈️ AI Travel Assistant")
    st.markdown("*Plan your perfect trip with AI-powered recommendations*")
    
    # Show personalized welcome message
    if 'travel_persona' in st.session_state and not st.session_state.chat_history:
        persona = st.session_state.travel_persona
        
        # Create personalized welcome message
        traveler_types_text = ""
        if persona.traveler_types:
            type_names = [t.value.replace('_', ' ').title() for t in persona.traveler_types]
            traveler_types_text = ", ".join(type_names)
        
        welcome_message = f"""
        👋 **Welcome back!** Based on your profile as a **{traveler_types_text}**, I'm ready to help you plan amazing trips!
        
        I know you prefer:
        • **Budget:** {persona.budget_style.value.replace('_', ' ').title() if persona.budget_style else 'Flexible'}
        • **Activities:** {', '.join([a.value.replace('_', ' ').title() for a in persona.activity_preferences[:3]]) if persona.activity_preferences else 'Various activities'}
        • **Accommodation:** {', '.join([a.value.replace('_', ' ').title() for a in persona.accommodation_preferences[:2]]) if persona.accommodation_preferences else 'Various types'}
        
        Just tell me where you'd like to go and I'll create a personalized itinerary just for you! 🎯
        """
        
        st.info(welcome_message)

    # Chat interface
    chat_container = st.container()

    # User input
    user_input = st.chat_input("Tell me about your travel plans... (e.g., 'I want to visit Paris for 5 days')")

    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Process user input through AI service with persona
        try:
            persona = st.session_state.get('travel_persona', None)
            response = ai_service.process_user_input_with_persona(
                user_input, 
                persona,
                st.session_state.chat_history
            )
            
            # Generate itinerary if destination is specified
            if response.get('generate_itinerary'):
                itinerary = itinerary_service.generate_persona_itinerary(
                    response['destination'],
                    persona,
                    response.get('duration', 3)
                )
                st.session_state.current_itinerary = itinerary
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response['message']
            })
            
        except Exception as e:
            st.error(f"Sorry, I encountered an error: {str(e)}")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I apologize, but I'm having some technical difficulties. Please try again."
            })

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Display current itinerary (if any)
    if st.session_state.current_itinerary:
        display_persona_itinerary(st.session_state.current_itinerary)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 <strong>Powered by Couchbase Capella + AWS Bedrock</strong></p>
        <p>Personalized recommendations based on your unique travel profile</p>
    </div>
    """, unsafe_allow_html=True)

def display_persona_itinerary(itinerary):
    """Display itinerary with persona-driven highlights"""
    st.markdown("---")
    st.header(f"🗺️ Your Personalized {itinerary.destination} Itinerary")
    
    # Show personalization note
    if 'travel_persona' in st.session_state:
        persona = st.session_state.travel_persona
        st.info(f"✨ **Personalized for you:** This itinerary is tailored for {', '.join([t.value.replace('_', ' ').title() for t in persona.traveler_types])} with {persona.budget_style.value.replace('_', ' ') if persona.budget_style else 'flexible'} budget preferences.")
    
    # Rest of itinerary display logic...
    # (Similar to previous itinerary display but with persona-aware messaging)

if __name__ == "__main__":
    main()
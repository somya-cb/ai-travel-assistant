# app/main.py
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


import streamlit as st
from services.persona_handler import load_or_create_persona
from services.trip_input_handler import trip_mode_selector
from services.couchbase_service import get_recommended_destinations, save_itinerary
from services.destination_card import display_destination_cards
from services.itinerary_builder import generate_itinerary
from services.recommendation_service import get_recommendations
from services.hotel_service import search_hotels, format_hotel_for_display
from services.hotel_cards import display_hotel_cards, display_hotel_search, display_hotel_details
from services.config import load_config

# ── Setup ────────────────────────────────────────────────
st.set_page_config(page_title="AI Travel Agent", layout="wide")
st.title("🌍 AI Travel Agent")

config = load_config("config.json")

# ── Session State Initialization ─────────────────────────
if "step" not in st.session_state:
    st.session_state.step = "persona"

st.session_state.setdefault("persona", {})
st.session_state.setdefault("destination_results", [])
st.session_state.setdefault("selected_destination", None)
st.session_state.setdefault("dates", {})
st.session_state.setdefault("hotel_results", [])
st.session_state.setdefault("selected_hotel", None)
st.session_state.setdefault("show_hotel_details", False)

# ── Step 1: Persona ──────────────────────────────────────
if st.session_state.step == "persona":
    persona = load_or_create_persona()
    if persona:
        st.session_state.persona = persona
        st.session_state.step = "trip_mode"
        st.rerun()

# ── Step 2: Trip Mode Selection ──────────────────────────
elif st.session_state.step == "trip_mode":
    st.subheader("🧭 How would you like to plan your trip?")
    
    mode, filters = trip_mode_selector()
    
    if mode is not None:
        # Get recommendations immediately
        with st.spinner("🔍 Finding destinations..."):
            results = get_recommendations(
                search_mode=mode,
                user_persona=st.session_state.persona,
                filters=filters,
                debug=True
            )

        st.session_state.destination_results = results
        st.session_state.step = "destination_select"
        st.rerun()

# ── Step 3: Destination Selection ─────────────────────────
elif st.session_state.step == "destination_select":
    st.subheader("🏖️ Choose Your Destination")

    if not st.session_state.destination_results:
        st.warning("No results. Returning to search.")
        st.session_state.step = "trip_mode"
        st.rerun()

    # Back button
    if st.button("← Back to Planning Method"):
        st.session_state.step = "trip_mode"
        st.session_state.destination_results = []
        st.session_state.selected_destination = None
        st.rerun()

    # Display destination cards
    display_destination_cards(st.session_state.destination_results)

# ── Step 4: Travel Dates ─────────────────────────────────
elif st.session_state.step == "date_select":
    st.subheader("📅 Choose Your Travel Dates")
    dest = st.session_state.selected_destination

    # Back button
    if st.button("← Back to Destinations"):
        st.session_state.step = "destination_select"
        st.session_state.selected_destination = None
        st.rerun()

    if dest:
        city = dest.get('city', 'Unknown')
        country = dest.get('country', '')
        st.markdown(f"**Destination:** {city}, {country}")

    start = st.date_input("Start Date", key="start_date")
    end = st.date_input("End Date", key="end_date")

    if start and end and start < end:
        num_days = (end - start).days + 1
        st.markdown(f"**Duration:** {num_days} days")

        # Store dates in session state immediately
        st.session_state.dates = {"start": str(start), "end": str(end), "days": num_days}

        # ── Hotel Selection Options ─────────────────────────
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🛏️ Browse Hotels First", type="primary", use_container_width=True):
                destination_city = dest.get("city")
                destination_country = dest.get("country")

                with st.spinner("🔍 Searching for hotels..."):
                    hotel_results = search_hotels(destination_city, destination_country)
                    
                    if hotel_results:
                        st.session_state.hotel_results = hotel_results
                        st.session_state.step = "hotel_select"
                        st.success(f"Found {len(hotel_results)} hotels!")
                        st.rerun()
                    else:
                        st.warning("No hotels found in this area.")
        
        with col2:
            if st.button("⏭️ Skip Hotel Selection", use_container_width=True):
                # Clear any previous hotel selection
                st.session_state.selected_hotel = None
                st.session_state.step = "generate"
                st.rerun()

    else:
        st.warning("Please select a valid date range.")

# ── Step 5: Hotel Selection ──────────────────────────────
elif st.session_state.step == "hotel_select":
    st.subheader("🏨 Browse Hotels")

    # Back button
    if st.button("← Back to Date Selection"):
        st.session_state.step = "date_select"
        st.session_state.hotel_results = []
        st.session_state.selected_hotel = None
        st.session_state.show_hotel_details = False
        st.rerun()

    hotels = st.session_state.hotel_results

    if hotels:
        display_hotel_cards(hotels)

        # If a hotel is selected for details, show detailed view
        if st.session_state.get("show_hotel_details") and st.session_state.get("selected_hotel"):
            display_hotel_details(st.session_state.selected_hotel)

    else:
        st.warning("No hotels to display.")

# ── Step 6: Itinerary Generation ─────────────────────────
elif st.session_state.step == "generate":
    # Back button
    if st.session_state.get("hotel_results"):
        # If we have hotel results, user came from hotel selection
        back_button_text = "← Back to Hotel Selection"
        back_step = "hotel_select"
    else:
        # User skipped hotel selection, go back to dates
        back_button_text = "← Back to Date Selection"  
        back_step = "date_select"
    
    if st.button(back_button_text):
        st.session_state.step = back_step
        st.rerun()

    with st.spinner("📋 Building your personalized itinerary..."):
        itinerary = generate_itinerary(
            persona=st.session_state.persona,
            destination=st.session_state.selected_destination,
            dates=st.session_state.dates,
            hotel=st.session_state.selected_hotel
        )

    st.success("Here is your personalized itinerary!")
    st.markdown(itinerary, unsafe_allow_html=True)

    # Save itinerary button
    if st.button("💾 Save This Itinerary"):
        if st.session_state.get("persona") and st.session_state.persona.get("user_id"):
            doc_key = save_itinerary(
                user_id=st.session_state.persona["user_id"],
                itinerary_text=itinerary,
                metadata={
                    "destination": st.session_state.selected_destination,
                    "dates": st.session_state.dates,
                    "hotel": st.session_state.selected_hotel
                }
            )
            st.success(f"Itinerary saved! (Doc ID: {doc_key})")
        else:
            st.warning("Missing user info. Cannot save itinerary.")

    if st.button("🌍 Plan Another Trip"):
        for key in ["destination_results", "selected_destination", "dates", "hotel_results", "selected_hotel", "show_hotel_details"]:
            st.session_state.pop(key, None)
        st.session_state.step = "trip_mode"
        st.rerun()
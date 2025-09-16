# app/main.py

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st
from src.services.persona_handler import load_or_create_persona
from src.services.trip_input_handler import trip_mode_selector
from src.services.couchbase_service import get_recommended_destinations
from src.services.destination_card import display_destination_cards
from src.services.itinerary_builder import generate_itinerary
from src.services.recommendation_service import get_recommendations
from src.services.hotel_service import search_hotels, format_hotel_for_display
from src.services.hotel_cards import display_hotel_cards, display_hotel_search, display_hotel_details
from config import load_config

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
    mode, filters = trip_mode_selector()

    if mode is not None:
        with st.spinner("🔍 Finding destinations..."):
            results = get_recommendations(
                search_mode=mode,
                user_persona=st.session_state.persona,
                filters=filters
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


    # Display all destination cards 
    display_destination_cards(st.session_state.destination_results)

# ── Step 4: Travel Dates ─────────────────────────────────
elif st.session_state.step == "date_select":
    st.subheader("📅 Choose Your Travel Dates")
    dest = st.session_state.selected_destination

    if dest:
        city = dest.get('city', 'Unknown')
        country = dest.get('country', '')
        st.markdown(f"**Destination:** {city}, {country}")

    start = st.date_input("Start Date", key="start_date")
    end = st.date_input("End Date", key="end_date")

    if start and end and start < end:
        num_days = (end - start).days + 1
        st.markdown(f"**Duration:** {num_days} days")

        # ── Show Hotels Button ─────────────────────────────
        if st.button("🛏️ Show me hotels in the area"):
            destination_city = dest.get("city")
            destination_country = dest.get("country")
            st.session_state.hotel_results = search_hotels(destination_city, destination_country)

            st.session_state.hotel_results = search_hotels(destination_city, destination_country)
            st.session_state.step = "hotel_select"
            st.rerun()

        if st.button("🧳 Generate My Itinerary"):
            st.session_state.dates = {"start": str(start), "end": str(end), "days": num_days}
            st.session_state.step = "generate"
            st.rerun()
    else:
        st.warning("Please select a valid date range.")

# ── Step 5: Hotel Selection ──────────────────────────────
elif st.session_state.step == "hotel_select":
    st.subheader("🏨 Browse Hotels")

    # Show raw hotel search results (IDs)
    st.markdown("### Debug: Raw Hotel IDs")
    st.json(st.session_state.hotel_results)

    hotels = []
    raw_hotels = {}
    for doc_id in st.session_state.hotel_results:
        hotel = format_hotel_for_display(doc_id)
        if hotel:
            hotels.append(hotel)
            raw_hotels[doc_id] = hotel  # collect raw output for debugging

    # Show raw hotel docs before rendering cards
    st.markdown("### Debug: Raw Hotel Documents (formatted for display)")
    st.json(raw_hotels)

    if hotels:
        display_hotel_cards(hotels)

        if st.session_state.selected_hotel:
            st.markdown("### Debug: Selected Hotel")
            st.json(st.session_state.selected_hotel)
            display_hotel_details(st.session_state.selected_hotel)

        if st.button("✅ Use this hotel and continue", key="confirm_hotel"):
            st.session_state.step = "generate"
            st.rerun()
    else:
        st.warning("No hotels to display.")

    if st.button("← Back to Date Selection", key="back_to_dates"):
        st.session_state.step = "date_select"
        st.rerun()


# ── Step 6: Itinerary Generation ─────────────────────────
elif st.session_state.step == "generate":
    with st.spinner("📋 Building your personalized itinerary..."):
        itinerary = generate_itinerary(
            persona=st.session_state.persona,
            destination=st.session_state.selected_destination,
            dates=st.session_state.dates,
            hotel=st.session_state.selected_hotel
        )

    st.success("Here is your personalized itinerary!")
    st.markdown(itinerary, unsafe_allow_html=True)

    if st.button("🌍 Plan Another Trip"):
        for key in ["destination_results", "selected_destination", "dates", "hotel_results", "selected_hotel"]:
            st.session_state.pop(key, None)
        st.session_state.step = "trip_mode"
        st.rerun()
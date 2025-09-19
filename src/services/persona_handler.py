# persona_handler.py

import streamlit as st
from services.couchbase_service import get_persona_by_user_id, save_persona

def load_or_create_persona():
    st.subheader("✍️ Tell us about your travel style")

    user_id = st.text_input("Enter your email (to save your profile)", key="user_id")

    if not user_id:
        st.warning("Please enter your email to continue.")
        return None

    # Fetch existing persona from Couchbase
    if "checked_persona" not in st.session_state:
        existing = get_persona_by_user_id(user_id)
        if existing:
            st.session_state.checked_persona = existing
        else:
            st.session_state.checked_persona = None

    if st.session_state.checked_persona:
        st.success("Loaded your saved travel preferences.")
        return st.session_state.checked_persona

    # Persona form
    with st.form("persona_form"):
        travel_style = st.selectbox("What's your travel style?", ["Relaxation", "Adventure", "Cultural", "Luxury", "Backpacking", "Mixed"])
        budget = st.selectbox("Budget preference?", ["Budget", "Mid-range", "Luxury"])
        activities = st.multiselect(
            "Favorite activities",
            ["Beaches", "Hiking", "Museums", "Shopping", "Food tours", "Nightlife", "Nature", "History"]
        )
        companions = st.multiselect("Who do you usually travel with?", ["Solo", "Partner", "Kids", "Friends", "Parents"])

        submitted = st.form_submit_button("Save My Preferences")

        if submitted:
            persona = {
                "user_id": user_id,
                "travel_style": travel_style.lower(),
                "budget": budget.lower(),
                "activities": [a.lower() for a in activities],
                "companions": [c.lower() for c in companions]
            }

            save_persona(user_id, persona)
            st.success("Preferences saved!")
            return persona

    return None

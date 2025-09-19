import streamlit as st
from services.couchbase_service import get_unique_values, get_cities_by_country, get_countries_by_region

def get_dropdown_data():
    """Get all unique values for dropdowns from the database"""
    try:
        # Cache this data in session state to avoid repeated DB calls
        if 'dropdown_data' not in st.session_state:
            with st.spinner("Loading destination data..."):
                st.session_state.dropdown_data = {
                    'regions': get_unique_values('region'),
                    'countries': get_unique_values('country'),
                    'cities': get_unique_values('city'),
                    'budget_levels': get_unique_values('budget_level')
                }
        return st.session_state.dropdown_data
    except Exception as e:
        st.error(f"Error loading destination data: {e}")
        return {
            'regions': ["Africa", "Asia", "Europe", "North America", "South America"],
            'countries': [],
            'cities': [],
            'budget_levels': ["budget", "mid_range", "luxury"]
        }

def trip_mode_selector():
    
    mode = st.radio(
        "Choose a planning method:",
        ["🎲 Surprise Me", "🔍 Search & Filter"],
        index=0,
        key="trip_mode_radio"
    )
    
    filters = {}
    
    if mode == "🔍 Search & Filter":
        st.markdown("### 🔎 Filter Destinations")
        
        # Get dropdown data
        dropdown_data = get_dropdown_data()
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Region selection
            regions_dropdown = [""] + sorted(dropdown_data['regions'])
            selected_region = st.selectbox("Select a region", regions_dropdown, key="region_select")
            
            # Country selection - filtered by region if selected
            if selected_region:
                try:
                    countries_in_region = get_countries_by_region(selected_region)
                    countries = [""] + sorted(countries_in_region)
                except:
                    countries = [""] + sorted(dropdown_data['countries'])
            else:
                countries = [""] + sorted(dropdown_data['countries'])
            
            selected_country = st.selectbox("Select a country", countries, key="country_select")
        
        with col2:
            # City selection - filtered by country if selected
            if selected_country:
                try:
                    cities_in_country = get_cities_by_country(selected_country)
                    cities = [""] + sorted(cities_in_country)
                except:
                    cities = [""] + sorted(dropdown_data['cities'])
            else:
                cities = [""] + sorted(dropdown_data['cities'])
            
            selected_city = st.selectbox("Select a city", cities, key="city_select")
            
            # Budget selection
            budget_levels = [""] + sorted(dropdown_data['budget_levels'])
            selected_budget = st.selectbox("Budget Level", budget_levels, key="budget_select")
        
        # Additional filters
        st.markdown("### 🎯 Additional Preferences")
        
        col3, col4 = st.columns(2)
        with col3:
            min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1, key="min_rating")
            
        with col4:
            search_text = st.text_input("Describe your ideal trip", 
                                      placeholder="e.g., 'romantic getaway', 'adventure sports'",
                                      key="search_text")
        
        # Show current selections
        if any([selected_region, selected_country, selected_city, selected_budget, search_text, min_rating > 0]):
            st.markdown("### 📝 Current Filters:")
            filter_summary = []
            if selected_region: filter_summary.append(f"**Region:** {selected_region}")
            if selected_country: filter_summary.append(f"**Country:** {selected_country}")
            if selected_city: filter_summary.append(f"**City:** {selected_city}")
            if selected_budget: filter_summary.append(f"**Budget:** {selected_budget}")
            if min_rating > 0: filter_summary.append(f"**Min Rating:** {min_rating}⭐")
            if search_text: filter_summary.append(f"**Theme:** {search_text}")
            
            st.markdown(" • ".join(filter_summary))
        
        if st.button("🔍 Find Destinations", type="primary"):
            filters = {
                "region": selected_region if selected_region else None,
                "country": selected_country if selected_country else None,
                "city": selected_city if selected_city else None,
                "budget_level": selected_budget if selected_budget else None,
                "search_text": search_text.strip() if search_text else None,
                "min_rating": min_rating if min_rating > 0 else None
            }
            return "filter_search", filters
        else:
            return None, None
    
    else:  # Surprise Me
        if st.button("🎲 Surprise Me with Recommendations", type="primary"):
            return "surprise", None
        else:
            return None, None


def reset_filters():
    """Reset all filter-related session state"""
    filter_keys = ["region_select", "country_select", "city_select", "budget_select", 
                   "min_rating", "search_text", "dropdown_data"]
    for key in filter_keys:
        if key in st.session_state:
            del st.session_state[key]
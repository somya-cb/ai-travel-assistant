import streamlit as st
from services.hotel_service import search_hotels, format_hotel_for_display

# -------------------------------
# Hotel Search Interface
# -------------------------------
def display_hotel_search(destination):
    """Display hotel search interface and results"""
    city = destination.get('city', 'Unknown')
    county = destination.get('county', 'Unknown')

    st.subheader(f"🏨 Hotels in {city}, {county}")

    if st.button("🔍 Search for Hotels", type="primary"):
        with st.spinner(f"Searching for hotels in {city}..."):
            
            hotels = search_hotels(city, county)
            
            if hotels:
                st.session_state.hotel_results = hotels
                st.success(f"Found {len(hotels)} hotels!")
                st.rerun()
            else:
                st.warning("No hotels found in this area.")

# -------------------------------
# Hotel List Display
# -------------------------------
def display_hotel_cards(hotels):
    if not hotels:
        st.info("🏨 No hotels to display.")
        return

    st.markdown(f"📋 Found {len(hotels)} hotels")
    st.markdown("---")

    for i, hotel in enumerate(hotels):
        with st.container():
            col_left, col_right = st.columns([4, 1])

            with col_left:
                # Hotel Name
                hotel_name = hotel.get('name', 'Unknown Hotel')
                st.markdown(f"### 🏨 {hotel_name}")

                # Location
                city = hotel.get('city', '')
                county = hotel.get('county', '')
                location = f"{city}, {county}" if city or county else "Location not specified"
                st.markdown(f"📍 {location}")

                # Rating
                rating = hotel.get('rating')
                if rating:
                    try:
                        rating_val = float(rating)
                        stars = "⭐" * int(rating_val)
                        st.markdown(f"{stars} {rating_val}/5")
                    except (ValueError, TypeError):
                        st.markdown(f"⭐ {rating}")

                # Short Description
                description = hotel.get("description", "")
                if description:
                    truncated_desc = description[:500] + ("..." if len(description) > 500 else "")
                    st.markdown(f"*{truncated_desc}*")


                # Amenities
                facilities = hotel.get("facilities", []) or hotel.get("HotelFacilities", [])
                if facilities:
                    # Split by common separators
                    if len(facilities) == 1:
                        # Splitting by common separators: comma, semicolon, or space
                        fac_text = facilities[0].replace("  ", " ").replace("•", ",").split(",")
                        fac_text = [f.strip() for f in fac_text if f.strip()]
                    else:
                        fac_text = [f.strip() for f in facilities if f.strip()]

                    # Display as list
                    st.markdown("**🔧 Amenities & Facilities:**")
                    for f in fac_text:
                        st.markdown(f"- {f}")


            with col_right:
                st.markdown("<br><br>", unsafe_allow_html=True)  # spacing at top
                if st.button("See Details", key=f"details_{hotel.get('id', i)}"):
                    st.session_state.selected_hotel = hotel
                    st.session_state.show_hotel_details = True
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Pick This Hotel", key=f"pick_{hotel.get('id', i)}"):
                    st.session_state.selected_hotel = hotel
                    st.session_state.step = "generate"
                    st.rerun()

        st.markdown("---")

    # Skip option at the bottom
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⏭️ Skip Hotel Selection", use_container_width=True):
            st.session_state.selected_hotel = None
            st.session_state.step = "generate"
            st.rerun()

# -------------------------------
# Hotel Details View
# -------------------------------
def display_hotel_details(hotel):
    """Simple detailed view of selected hotel"""
    st.subheader(f"🏨 {hotel['name']}")

    if st.button("← Back to Hotels"):
        st.session_state.show_hotel_details = False
        st.session_state.pop('selected_hotel', None)
        st.rerun()



    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Basic info
        st.markdown(f"**📍 Location:** {hotel.get('address', 'Address not available')}")
        
        rating = hotel.get('rating', '')
        if rating:
            try:
                rating_val = float(rating)
                stars = "⭐" * int(rating_val)
                st.markdown(f"**⭐ Rating:** {stars} {rating_val}/5")
            except (ValueError, TypeError):
                st.markdown(f"**⭐ Rating:** {rating}")

        # Description
        if hotel.get('description'):
            st.markdown("**📝 About This Hotel:**")
            st.write(hotel['description'])

        # All facilities
        if hotel.get('facilities'):
            st.markdown("**🔧 Amenities & Facilities:**")
            facilities = hotel['facilities']
            
            # Display in 3 columns
            cols = st.columns(3)
            for i, facility in enumerate(facilities):
                with cols[i % 3]:
                    st.markdown(f"• {facility}")

    with col2:
        # Contact info
        st.markdown("### Contact Information")
        if hotel.get('phone'):
            st.markdown(f"📞 {hotel['phone']}")
        if hotel.get('website'):
            st.markdown(f"🌐 [Visit Website]({hotel['website']})")

        # Map if coordinates available
        if hotel.get('latitude') and hotel.get('longitude'):
            try:
                st.markdown("### Location")
                st.map([{"lat": float(hotel['latitude']), "lon": float(hotel['longitude'])}])
            except (ValueError, TypeError):
                st.info("Map not available")

        # Pick hotel button
        st.markdown("---")
        if st.button("✅ Pick This Hotel", 
                   type="primary"):
            st.session_state.selected_hotel = hotel
            st.session_state.step = "generate"
            st.rerun()

# -------------------------------
# Hotel Preview on Destination Card
# -------------------------------
def display_hotel_preview(destination):
    """Simple hotel availability preview"""
    city = destination.get("city", "")
    county = destination.get("county", "")
    hotel_count = 120
    min_price = 89
    return f"🛏️ **{hotel_count}+ hotels** available from **${min_price}/night** in {city}, {county}"
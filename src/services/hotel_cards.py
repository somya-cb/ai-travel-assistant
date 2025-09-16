import streamlit as st
from src.services.hotel_service import search_hotels, format_hotel_for_display

def display_hotel_search(destination):
    """Display hotel search interface and results"""
    city = destination.get('city', 'Unknown')
    country = destination.get('country', 'Unknown')

    st.subheader(f"🏨 Hotels in {city}, {country}")

    if st.button("🔍 Search for Hotels", type="primary", use_container_width=True):
        with st.spinner(f"Searching for hotels in {city}..."):

            hotel_ids = search_hotels(city, country)

            print("=== RAW HOTEL IDS FROM SEARCH ===")
            print(hotel_ids)
            st.write("Raw result from `search_hotels()`:")
            st.write(hotel_ids)

            hotels = []
            for doc_id in hotel_ids:
                formatted = format_hotel_for_display(doc_id)
                if formatted:
                    hotels.append(formatted)

            if hotels:
                st.session_state.hotel_results = hotels
                st.rerun()
            else:
                st.warning("No valid hotels found.")


def display_hotel_cards(hotels):
    if not hotels:
        st.info("No hotels to display.")
        return

    st.success(f"Found {len(hotels)} hotels!")

    for hotel in hotels:
        if hotel is None:
            st.warning("Skipped invalid hotel")
            continue
        st.markdown(f"🆔 **Hotel ID:** `{hotel['id']}`")
        st.markdown(f"**🏨 Name:** {hotel.get('name', 'Unknown')}")
        st.markdown(f"📍 **Address:** {hotel.get('address', 'N/A')}")
        st.markdown("---")


def display_hotel_details(hotel):
    """Detailed view of selected hotel"""
    st.subheader(f"🏨 {hotel['name']}")

    if st.button("← Back to Hotels"):
        st.session_state.show_hotel_details = False
        st.session_state.pop('selected_hotel', None)
        st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**📍 Address:** {hotel['address']}")
        st.markdown(f"**⭐ Rating:** {hotel['rating']}")
        if hotel['description']:
            st.markdown("**📝 Description:**")
            st.write(hotel['description'])

        if hotel['facilities']:
            st.markdown("**🔧 Facilities:**")
            cols = st.columns(3)
            for i, facility in enumerate(hotel['facilities']):
                with cols[i % 3]:
                    st.markdown(f"• {facility}")

    with col2:
        if hotel['phone']:
            st.markdown(f"**📞 Phone:** {hotel['phone']}")
        if hotel['website']:
            st.markdown(f"**🌐 Website:** [Visit Hotel Website]({hotel['website']})")
        if hotel.get('latitude') and hotel.get('longitude'):
            try:
                st.map([{"lat": float(hotel['latitude']), "lon": float(hotel['longitude'])}])
            except:
                st.info("Map coordinates available but not displayable")


def display_saved_hotels():
    """Display saved hotels summary"""
    if 'saved_hotels' not in st.session_state or not st.session_state.saved_hotels:
        return

    st.subheader("📌 Your Saved Hotels")

    for hotel in st.session_state.saved_hotels:
        with st.expander(f"🏨 {hotel['name']} - {hotel['rating']}"):
            st.markdown(f"📍 {hotel['address']}")
            if hotel['phone']:
                st.markdown(f"📞 {hotel['phone']}")
            if hotel['website']:
                st.markdown(f"🌐 [Website]({hotel['website']})")


def display_hotel_preview(destination):
    """Preview hotel availability on destination card"""
    city = destination.get("city", "")
    country = destination.get("country", "")
    hotel_count = 120
    min_price = 89
    return f"🛏️ **{hotel_count}+ hotels** available from **${min_price}/night** in *{city}, {country}*"

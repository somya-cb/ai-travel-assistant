# destination_card.py

import streamlit as st

def display_destination_cards(destinations):
    st.subheader("🌎 Matching Destinations")

    if not destinations:
        st.warning("No destinations matched your filters.")
        return None

    # Show destinations in a grid
    cols = st.columns(2)  

    for i, dest in enumerate(destinations):
        with cols[i % 2]:
            # Create a card
            with st.container():
                st.markdown("---")  
                
                # Destination title
                city = dest.get('city', 'Unknown')
                country = dest.get('country', 'Unknown')
                region = dest.get('region', '')
                
                title = f"**{city}, {country}**"
                if region and region.lower() != country.lower():
                    title += f" *({region})*"
                
                st.markdown(title)
                
                # Description 
                description = dest.get("short_description", "No description available")
                if description:
                    # Truncate long descriptions
                    if len(description) > 200:
                        description = description[:200] + "..."
                    st.markdown(f"📝 {description}")
                
                # Display tags if they exist
                tags = dest.get("tags", [])
                if tags:
                    # Show tags in a more visual way
                    tag_text = " ".join([f"`{tag}`" for tag in tags[:5]])  # Limit to 5 tags
                    if len(tags) > 5:
                        tag_text += f" +{len(tags)-5} more"
                    st.markdown(f"🏷️ {tag_text}")
                
                # Display additional info if available
                budget_level = dest.get("budget_level", "")
                if budget_level:
                    st.markdown(f"💰 Budget: `{budget_level.title()}`")
                
                # Display rating or score if available
                score = dest.get("score", dest.get("rating", ""))
                if score:
                    st.markdown(f"⭐ Score: `{score}`")
                
                # Use unique key and check session state
                button_key = f"choose_{dest.get('id', i)}"
                if st.button(f"✈️ Choose {city}", key=button_key, type="primary", use_container_width=True):
                    # Store selection in session state instead of returning immediately
                    st.session_state.selected_destination = dest
                    st.session_state.step = "date_select"
                    st.rerun()
                
                st.markdown("") 

    return None
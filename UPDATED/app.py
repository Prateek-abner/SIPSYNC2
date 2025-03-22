# app.py

import streamlit as st
from backend import generate_response
from maps import geocode_address, find_nearby_stores, display_interactive_map
# Uncomment the below line to use Google Maps API instead
# from google_maps import geocode_address_google as geocode_address, find_nearby_places as find_nearby_stores, display_google_map as display_interactive_map
from youtube import search_youtube
import time
import re

# Set page configuration
st.set_page_config(
    page_title="SipSync: Daily Brew Matchmaker",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #2e7d32;
    }
    .stButton button {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
    }
    .small-font {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Main title and description
st.title("🍵 SipSync: Daily Brew Matchmaker")
st.markdown("""
Welcome to **SipSync**, your personal brew matchmaker! Whether you're feeling under the weather or just need a moment of relaxation, 
we'll help you find the perfect drink or light food to soothe your mind and body. Simply describe your ailment, and we'll recommend the best option for you.
""")

# Drink type selection
drink_types = ["tea", "coffee", "milkshake", "light_food"]
drink_icons = {"tea": "🍵", "coffee": "☕", "milkshake": "🥤", "light_food": "🍽️"}

selected_drink = st.radio(
    "What type of recommendation are you looking for?",
    options=drink_types,
    format_func=lambda x: f"{drink_icons[x]} {x.replace('_', ' ').title()}"
)

# User input for ailment
user_input = st.text_input(
    "What's bothering you today?",
    placeholder="e.g., sore throat, can't sleep, headache"
)

# Sanitize input
def sanitize_input(text):
    # Remove special characters and convert to lowercase
    if text:
        return re.sub(r'[^a-zA-Z\s]', '', text).lower().strip()
    return ""

# Initialize session state variables if not present
if 'recommendation' not in st.session_state:
    st.session_state['recommendation'] = None
if 'location_set' not in st.session_state:
    st.session_state['location_set'] = False
if 'stores' not in st.session_state:
    st.session_state['stores'] = []

# Button to find recommendation
if st.button("Find My Brew"):
    if not user_input:
        st.warning("Please enter an ailment.")
    else:
        # Sanitize the input
        clean_input = sanitize_input(user_input)
        
        with st.spinner("Finding your perfect brew..."):
            recommendation = generate_response(clean_input, drink_type=selected_drink)
            st.session_state['recommendation'] = recommendation
            
            if recommendation["status"] == "success":
                st.markdown(f"## {drink_icons[selected_drink]} {recommendation['drink']} for {recommendation['ailment'].title()}")
                st.markdown(f"*{recommendation['personalized_message']}*")

                # Create two columns for layout
                col1, col2 = st.columns([2, 1])
                
                # Benefits section
                with col1:
                    with st.expander("✨ Benefits", expanded=True):
                        for benefit in recommendation["benefits"]:
                            st.markdown(f"- {benefit}")

                # Ingredients section
                with col2:
                    with st.expander("📜 Ingredients", expanded=True):
                        for ingredient in recommendation["ingredients"]:
                            st.markdown(f"- {ingredient}")

                # Brewing tip
                st.markdown(f"**🍶 Preparation Tip:** {recommendation['brewing_tip']}")
                
                # YouTube videos
                st.markdown("### 📺 Learn More: YouTube Videos")
                
                with st.spinner("Fetching videos..."):
                    videos = search_youtube(recommendation["youtube_keywords"])
                
                if videos:
                    video_cols = st.columns(min(3, len(videos)))
                    for i, video in enumerate(videos[:3]):
                        with video_cols[i]:
                            st.markdown(f"#### {video['title']}")
                            st.markdown(f"[![Thumbnail]({video['thumbnail']})]({video['url']})")
                            st.markdown(f"[Watch Video]({video['url']})")
                else:
                    st.info("No videos found. Try searching YouTube directly for preparation tips.")
            else:
                st.error(recommendation["message"])
                st.markdown("Please try one of these ailments instead: sore throat, can't sleep, headache")

# Google Maps Integration
st.sidebar.header("📍 Find Nearby Stores")
st.sidebar.markdown("Find stores near you that might carry ingredients for your recommendation.")

address = st.sidebar.text_input("Enter your address:", value="New Delhi, India")

if st.sidebar.button("Find Stores"):
    if not st.session_state.get('recommendation'):
        st.sidebar.warning("Please generate a recommendation first by clicking 'Find My Brew'.")
    else:
        with st.spinner("Finding your location..."):
            latitude, longitude = geocode_address(address)
            
        if latitude and longitude:
            st.session_state['location_set'] = True
            
            # Get ingredients from the recommendation
            ingredients = st.session_state['recommendation'].get("ingredients", [])
            
            with st.spinner(f"Searching for stores with {', '.join(ingredients)}..."):
                # Pass entire ingredients list to the find_nearby_stores function
                stores = find_nearby_stores(latitude, longitude, ingredients)
                st.session_state['stores'] = stores
                
            st.sidebar.success(f"Found {len(stores)} stores near {address}")
        else:
            st.sidebar.error("Could not find location. Please check the address and try again.")

# Display map if location is set
if st.session_state.get('location_set'):
    # Get the saved values
    latitude, longitude = geocode_address(address)
    stores = st.session_state.get('stores', [])
    
    if latitude and longitude:
        # Get ingredients from the recommendation
        ingredients = st.session_state['recommendation'].get("ingredients", []) if st.session_state.get('recommendation') else []
        
        # Create a tab for the map
        map_tab, recommendation_tab = st.tabs(["📍 Map", "🍵 Your Recommendation"])
        
        with map_tab:
            display_interactive_map(latitude, longitude, stores, ingredients)
            
        with recommendation_tab:
            if st.session_state.get('recommendation'):
                rec = st.session_state['recommendation']
                st.markdown(f"## {drink_icons[selected_drink]} {rec['drink']} for {rec['ailment'].title()}")
                st.markdown(f"*{rec['personalized_message']}*")
                
                # Benefits and ingredients in columns
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("### ✨ Benefits")
                    for benefit in rec["benefits"]:
                        st.markdown(f"- {benefit}")
                
                with col2:
                    st.markdown("### 📜 Ingredients")
                    for ingredient in rec["ingredients"]:
                        st.markdown(f"- {ingredient}")
                
                st.markdown(f"**🍶 Preparation Tip:** {rec['brewing_tip']}")

# Footer
st.markdown("---")
st.markdown("<p class='small-font'>SipSync: Daily Brew Matchmaker - Your personal wellness companion</p>", unsafe_allow_html=True)

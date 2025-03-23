# app.py

import streamlit as st
from backend import generate_response
from maps import geocode_address, find_nearby_stores, display_interactive_map
# Uncomment the below line to use Google Maps API instead
# from google_maps import geocode_address_google as geocode_address, find_nearby_places as find_nearby_stores, display_google_map as display_interactive_map
from youtube import search_youtube
import time
import re
from language_support import (
    SUPPORTED_LANGUAGES, detect_language, translate_recommendation,
    get_language_name
)
from user_profile import UserProfile
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
import json
import uuid

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
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stProgress .st-bo {
        background-color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    try:
        st.session_state['user_id'] = str(uuid.uuid4())
    except Exception as e:
        st.error("Error initializing user session. Please refresh the page.")
        st.stop()

if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

if 'profile' not in st.session_state:
    try:
        st.session_state['profile'] = UserProfile(st.session_state['user_id'])
    except Exception as e:
        st.error("Error loading user profile. Please try refreshing the page.")
        st.stop()

# Load Lottie animation
def load_lottie_url(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f"Error loading Lottie animation: {e}")
        return None

lottie_tea = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")

# Sidebar
with st.sidebar:
    st.title("🎯 Navigation")
    selected = option_menu(
        menu_title=None,
        options=["Home", "Profile", "Analytics", "Settings"],
        icons=["house", "person", "graph-up", "gear"],
        default_index=0
    )
    
    # Language selector
    st.write("---")
    st.write("🌍 Language / Langue / Idioma")
    selected_language = st.selectbox(
        "",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=get_language_name,
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state['language'])
    )
    if selected_language != st.session_state['language']:
        st.session_state['language'] = selected_language
        st.session_state['profile'].preferences['language'] = selected_language
        st.session_state['profile'].save_profile()
        st.rerun()

if selected == "Home":
    # Main title and description
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("🍵 SipSync: Daily Brew Matchmaker")
        st.markdown("""
        Welcome to **SipSync**, your personal brew matchmaker! Whether you're feeling under the weather 
        or just need a moment of relaxation, we'll help you find the perfect drink to soothe your mind and body.
        """)
    with col2:
        st_lottie(lottie_tea, height=200)

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

    # Get user location
    location_col1, location_col2 = st.columns(2)
    with location_col1:
        address = st.text_input("Enter your location for weather-aware recommendations:", value="")
    with location_col2:
        if address:
            latitude, longitude = geocode_address(address)
        else:
            latitude, longitude = None, None

    # Generate recommendation
    if st.button("Find My Brew"):
        if not user_input:
            st.warning("Please enter an ailment.")
        else:
            try:
                with st.spinner("Finding your perfect brew..."):
                    # Detect input language
                    try:
                        input_lang, _ = detect_language(user_input)
                    except Exception as e:
                        st.warning("Language detection failed. Proceeding with English.")
                        input_lang = 'en'
                    
                    # Generate recommendation
                    try:
                        recommendation = generate_response(
                            user_input,
                            drink_type=selected_drink,
                            latitude=latitude,
                            longitude=longitude
                        )
                    except Exception as e:
                        st.error("Failed to generate recommendation. Please try again.")
                        st.stop()
                    
                    # Translate if needed
                    if st.session_state['language'] != 'en':
                        try:
                            recommendation = translate_recommendation(
                                recommendation,
                                st.session_state['language']
                            )
                        except Exception as e:
                            st.warning("Translation failed. Showing original recommendation.")
                    
                    # Save to user profile
                    try:
                        st.session_state['profile'].add_recommendation(recommendation)
                    except Exception as e:
                        st.warning("Failed to save recommendation to profile.")
                    
                    if recommendation["status"] == "success":
                        try:
                            # Display recommendation
                            st.markdown(f"## {drink_icons[selected_drink]} {recommendation['drink']}")
                            st.markdown(f"*{recommendation['personalized_message']}*")

                            # Benefits and ingredients
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                with st.expander("✨ Benefits", expanded=True):
                                    for benefit in recommendation.get("benefits", []):
                                        st.markdown(f"- {benefit}")
                            with col2:
                                with st.expander("📜 Ingredients", expanded=True):
                                    for ingredient in recommendation.get("ingredients", []):
                                        st.markdown(f"- {ingredient}")

                            # Sustainability score
                            st.write("---")
                            st.write("🌱 Sustainability Score")
                            sustainability_score = recommendation.get("sustainability_score", 0)
                            st.progress(min(max(sustainability_score / 5.0, 0), 1))
                            st.write("Eco-friendly Tips:")
                            for tip in recommendation.get("eco_friendly_tips", []):
                                st.markdown(f"- {tip}")

                            # Cultural origin and scientific evidence
                            st.write("---")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("🌍 Cultural Origin")
                                st.info(recommendation.get("cultural_origin", "Information not available"))
                            with col2:
                                st.write("🔬 Scientific Evidence")
                                st.info(recommendation.get("scientific_evidence", "Information not available"))

                            # Weather adjustment if applicable
                            if recommendation.get("weather_adjusted"):
                                st.write("---")
                                st.write("🌤️ Weather-Adjusted Recommendation")
                                st.info("This recommendation has been adjusted based on your local weather conditions.")

                            # Brewing tip
                            st.write("---")
                            st.write("🍶 Preparation Instructions")
                            st.success(recommendation.get("brewing_tip", "Simple preparation recommended"))

                            # Map integration
                            if latitude and longitude:
                                try:
                                    st.write("---")
                                    st.write("🗺️ Nearby Stores")
                                    with st.spinner("Finding stores..."):
                                        stores = find_nearby_stores(latitude, longitude, recommendation.get("ingredients", []))
                                        if stores:
                                            display_interactive_map(latitude, longitude, stores, recommendation.get("ingredients", []))
                                        else:
                                            st.info("No stores found nearby. Try expanding your search area.")
                                except Exception as e:
                                    st.warning("Unable to load store locations. Please check your internet connection.")

                            # YouTube videos
                            try:
                                st.write("---")
                                st.write("📺 Learn More")
                                with st.spinner("Loading videos..."):
                                    videos = search_youtube(recommendation.get("youtube_keywords", ""))
                                    if videos:
                                        video_cols = st.columns(min(3, len(videos)))
                                        for i, video in enumerate(videos[:3]):
                                            with video_cols[i]:
                                                st.markdown(f"#### {video['title']}")
                                                st.markdown(f"[![Thumbnail]({video['thumbnail']})]({video['url']})")
                                                st.markdown(f"[Watch Video]({video['url']})")
                                    else:
                                        st.info("No related videos found.")
                            except Exception as e:
                                st.warning("Unable to load YouTube videos. Please check your internet connection.")
                                
                        except Exception as e:
                            st.error("Error displaying recommendation. Please try again.")
                    else:
                        st.error(recommendation.get("message", "An error occurred. Please try again."))
            except Exception as e:
                st.error("An unexpected error occurred. Please try again.")

elif selected == "Profile":
    st.title("👤 User Profile")
    
    # Display user stats
    stats = st.session_state['profile'].get_recommendation_stats()
    if stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recommendations", stats['total_recommendations'])
        with col2:
            st.metric("Unique Ailments", stats['unique_ailments'])
        with col3:
            st.metric("Avg. Sustainability", f"{stats['avg_sustainability']:.1f}/5.0")
            
        # Personal suggestions
        st.write("---")
        st.write("🎯 Personalized Suggestions")
        suggestions = st.session_state['profile'].get_personalized_suggestions()
        for suggestion in suggestions:
            st.info(suggestion['message'])
            
elif selected == "Analytics":
    st.title("📊 Analytics Dashboard")
    
    # Generate visualizations
    visualizations = st.session_state['profile'].generate_insights_visualizations()
    if visualizations:
        # Display charts
        st.plotly_chart(visualizations['ailment_distribution'], use_container_width=True)
        st.plotly_chart(visualizations['sustainability_trend'], use_container_width=True)
        st.plotly_chart(visualizations['weather_usage'], use_container_width=True)
    else:
        st.info("Start getting recommendations to see your analytics!")
        
elif selected == "Settings":
    st.title("⚙️ Settings")
    
    # User preferences
    st.write("### Preferences")
    preferences = st.session_state['profile'].preferences
    
    # Drink preference
    preferred_drink = st.selectbox(
        "Default Drink Type",
        options=["tea", "coffee", "milkshake", "light_food"],
        index=["tea", "coffee", "milkshake", "light_food"].index(
            preferences.get('preferred_drink_type', 'tea')
        )
    )
    
    # Dietary restrictions
    dietary = st.multiselect(
        "Dietary Restrictions",
        options=["Vegan", "Vegetarian", "Gluten-free", "Dairy-free"],
        default=preferences.get('dietary_restrictions', [])
    )
    
    # Sustainability focus
    sustainability = st.checkbox(
        "Focus on Sustainable Options",
        value=preferences.get('sustainability_focus', True)
    )
    
    # Save changes
    if st.button("Save Preferences"):
        st.session_state['profile'].update_preferences({
            'preferred_drink_type': preferred_drink,
            'dietary_restrictions': dietary,
            'sustainability_focus': sustainability
        })
        st.success("Preferences saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    "<p class='small-font'>SipSync: Daily Brew Matchmaker - Your personal wellness companion</p>",
    unsafe_allow_html=True
)

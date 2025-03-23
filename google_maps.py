# google_maps.py

import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

def geocode_address_google(address):
    """
    Convert an address into latitude and longitude using Google Maps Geocoding API.
    
    Args:
        address (str): The address to geocode.
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails.
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": GOOGLE_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
    except Exception as e:
        st.error(f"Geocoding error: {e}")
    
    return None, None

def find_nearby_places(latitude, longitude, ingredients=None, radius=3000):
    """
    Find nearby places using Google Places API.
    
    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        ingredients (list): List of ingredients to search for.
        radius (int): Search radius in meters.
        
    Returns:
        list: List of nearby places.
    """
    if not GOOGLE_API_KEY:
        st.error("Google API key is missing. Please add it to your .env file.")
        return []
    
    # Create search types based on ingredients
    search_types = ["cafe", "grocery_or_supermarket", "store"]
    
    # Create keywords based on ingredients
    keywords = ["cafe", "coffee", "tea"]
    if ingredients:
        keywords.extend(ingredients)
    
    places = []
    
    try:
        # First search by type
        for place_type in search_types:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": place_type,
                "key": GOOGLE_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    places.extend(data["results"])
            
            # Respect API rate limits
            time.sleep(0.2)
        
        # Then search by keyword for more specific places
        for keyword in keywords:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "keyword": keyword,
                "key": GOOGLE_API_KEY
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    places.extend(data["results"])
            
            # Respect API rate limits
            time.sleep(0.2)
        
        # Remove duplicates by place_id
        unique_places = {}
        for place in places:
            if place["place_id"] not in unique_places:
                unique_places[place["place_id"]] = place
        
        # Format places for display
        formatted_places = []
        for place_id, place in unique_places.items():
            # Get place type
            place_type = "Store"
            if "types" in place:
                if "cafe" in place["types"]:
                    place_type = "Cafe"
                elif "grocery_or_supermarket" in place["types"]:
                    place_type = "Supermarket"
                elif "store" in place["types"]:
                    place_type = "Store"
            
            formatted_place = {
                "name": place["name"],
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "address": place.get("vicinity", "Address not available"),
                "type": place_type,
                "rating": place.get("rating", "Not rated"),
                "place_id": place_id
            }
            formatted_places.append(formatted_place)
        
        # Sort places by relevance (cafes first, then supermarkets, then other stores)
        formatted_places.sort(key=lambda x: 
                             (0 if x["type"] == "Cafe" else 
                              1 if x["type"] == "Supermarket" else 2))
        
        return formatted_places
    
    except Exception as e:
        st.error(f"Error finding places: {e}")
        return []

def get_place_details(place_id):
    """
    Get detailed information about a place using Google Places API.
    
    Args:
        place_id (str): The Google Place ID.
        
    Returns:
        dict: Place details.
    """
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,opening_hours,rating,review",
            "key": GOOGLE_API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                return data["result"]
    except Exception as e:
        st.error(f"Error getting place details: {e}")
    
    return None

def display_google_map(latitude, longitude, places=None, ingredients=None):
    """
    Display an interactive map with markers for nearby places.
    
    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        places (list): List of nearby places.
        ingredients (list): List of ingredients being searched for.
    """
    st.write("### 🗺️ Find Nearby Stores")
    
    if ingredients:
        st.write(f"Showing places that might have: **{', '.join(ingredients)}**")
    
    # Create a Folium map centered on the user's location
    m = folium.Map(location=[latitude, longitude], zoom_start=14)

    # Add a marker for the user's location
    folium.Marker(
        location=[latitude, longitude],
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

    # Add markers for nearby places
    if places:
        # Create marker clusters to handle many places
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        
        for place in places:
            # Choose icon based on place type
            icon_color = "green"
            icon_name = "store"
            
            if place["type"] == "Cafe":
                icon_color = "red"
                icon_name = "coffee"
            elif place["type"] == "Supermarket":
                icon_color = "orange"
                icon_name = "shopping-cart"
            
            # Create popup content
            popup_content = f"""
            <b>{place['name']}</b><br>
            Type: {place['type']}<br>
            Address: {place['address']}<br>
            Rating: {place['rating']}
            """
            
            folium.Marker(
                location=[place["latitude"], place["longitude"]],
                popup=popup_content,
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa")
            ).add_to(marker_cluster)

    # Display the map
    folium_static(m)

    # Display place details
    if places:
        # Group places by type
        place_types = {}
        for place in places:
            place_type = place["type"]
            if place_type not in place_types:
                place_types[place_type] = []
            place_types[place_type].append(place)
        
        # Display places by type
        st.write("### 🏪 Nearby Places")
        
        # First show cafes
        if "Cafe" in place_types:
            with st.expander(f"Cafes ({len(place_types['Cafe'])})", expanded=True):
                for i, place in enumerate(place_types["Cafe"]):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"#### {i+1}. {place['name']}")
                        st.write(f"📍 Address: {place['address']}")
                        if place['rating'] != "Not rated":
                            st.write(f"⭐ Rating: {place['rating']}/5")
                    with col2:
                        if st.button(f"Details", key=f"cafe_{i}"):
                            details = get_place_details(place["place_id"])
                            if details:
                                st.write(f"**Phone:** {details.get('formatted_phone_number', 'Not available')}")
                                if "website" in details:
                                    st.write(f"**Website:** [{details['website']}]({details['website']})")
                                if "opening_hours" in details:
                                    st.write("**Opening Hours:**")
                                    for hour in details["opening_hours"].get("weekday_text", []):
                                        st.write(f"- {hour}")
                    st.write("---")
        
        # Then show supermarkets
        if "Supermarket" in place_types:
            with st.expander(f"Supermarkets ({len(place_types['Supermarket'])})", expanded=True):
                for i, place in enumerate(place_types["Supermarket"]):
                    st.write(f"#### {i+1}. {place['name']}")
                    st.write(f"📍 Address: {place['address']}")
                    if place['rating'] != "Not rated":
                        st.write(f"⭐ Rating: {place['rating']}/5")
                    st.write("---")
        
        # Then show other stores
        if "Store" in place_types:
            with st.expander(f"Other Stores ({len(place_types['Store'])})", expanded=False):
                for i, place in enumerate(place_types["Store"]):
                    st.write(f"#### {i+1}. {place['name']}")
                    st.write(f"📍 Address: {place['address']}")
                    if place['rating'] != "Not rated":
                        st.write(f"⭐ Rating: {place['rating']}/5")
                    st.write("---")
    else:
        st.info("No places found nearby. Try expanding your search area or checking a different location.")

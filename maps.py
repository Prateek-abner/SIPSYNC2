# maps.py

import folium
import streamlit as st
from streamlit_folium import folium_static
import requests
import time

def geocode_address(address):
    """
    Convert an address into latitude and longitude using OpenStreetMap's Nominatim API.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "SipSync/1.0"  # Required by Nominatim's ToS
    }
    params = {
        "q": address,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        # Add delay to respect usage policy
        time.sleep(1)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return None, None

def find_nearby_stores(latitude, longitude, ingredients):
    """
    Find nearby stores that might have the requested ingredients.
    
    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        ingredients (list): List of ingredients to search for.
    """
    try:
        # Build a query for tea/coffee shops and stores for ingredients
        keywords = ["cafe", "tea", "coffee", "supermarket", "grocery", "market"]
        
        # Add more specific queries based on ingredients
        if isinstance(ingredients, list) and ingredients:
            for ingredient in ingredients:
                if "milk" in ingredient.lower():
                    keywords.extend(["dairy", "milk"])
                if "honey" in ingredient.lower():
                    keywords.append("organic")
                if "ginger" in ingredient.lower() or "herbs" in ingredient.lower():
                    keywords.extend(["spice", "herbalist"])
        
        # Build Overpass query for multiple shop types
        query_parts = []
        for keyword in keywords:
            query_parts.append(f'node[~".*{keyword}.*"~"."](around:3000,{latitude},{longitude});')
        
        # Add specific shop types
        shop_types = ["cafe", "coffee_shop", "tea", "supermarket", "convenience", "herbalist", "spices", "health_food"]
        for shop in shop_types:
            query_parts.append(f'node["shop"="{shop}"](around:3000,{latitude},{longitude});')
        
        # Add amenities like cafes
        query_parts.append(f'node["amenity"="cafe"](around:3000,{latitude},{longitude});')
        
        # Combined query
        query = f"""
        [out:json];
        (
            {' '.join(query_parts)}
        );
        out body;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data=query)
        
        # Add delay to respect usage policy
        time.sleep(1)
        
        if response.status_code == 200:
            data = response.json()
            stores = []
            seen_names = set()  # To avoid duplicate stores
            
            for element in data.get("elements", []):
                if "tags" in element and "name" in element.get("tags", {}):
                    name = element["tags"]["name"]
                    
                    # Skip if we've already seen this store
                    if name in seen_names:
                        continue
                    seen_names.add(name)
                    
                    # Get store type/category
                    store_type = "Store"
                    if "shop" in element["tags"]:
                        store_type = element["tags"]["shop"].replace("_", " ").title()
                    elif "amenity" in element["tags"] and element["tags"]["amenity"] == "cafe":
                        store_type = "Cafe"
                    
                    # Get a proper address if available
                    address = "Address not available"
                    if "addr:street" in element["tags"]:
                        street = element["tags"].get("addr:street", "")
                        housenumber = element["tags"].get("addr:housenumber", "")
                        city = element["tags"].get("addr:city", "")
                        if street and housenumber:
                            address = f"{housenumber} {street}, {city}" if city else f"{housenumber} {street}"
                        elif street:
                            address = f"{street}, {city}" if city else street
                    
                    store = {
                        "name": name,
                        "latitude": element["lat"],
                        "longitude": element["lon"],
                        "address": address,
                        "type": store_type
                    }
                    stores.append(store)
            
            # Sort stores by type (cafes and tea shops first)
            stores.sort(key=lambda x: 0 if x["type"] in ["Cafe", "Tea", "Coffee Shop"] else 1)
            
            return stores
    except Exception as e:
        print(f"Store search error: {e}")
    
    return []

def display_interactive_map(latitude, longitude, stores=None, ingredients=None):
    """
    Display an interactive Folium map with markers for nearby stores.
    """
    st.write("### 🗺️ Find Nearby Stores")
    
    if ingredients:
        st.write(f"Showing stores that might have: **{', '.join(ingredients)}**")
    
    # Create a Folium map centered on the user's location
    m = folium.Map(location=[latitude, longitude], zoom_start=14)

    # Add a marker for the user's location
    folium.Marker(
        location=[latitude, longitude],
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

    # Add markers for nearby stores with different icons based on type
    if stores:
        # Create marker clusters to handle many stores
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        
        for store in stores:
            # Choose icon based on store type
            icon_color = "green"
            icon_name = "shopping-bag"
            
            if "cafe" in store["type"].lower() or "coffee" in store["type"].lower():
                icon_color = "red" 
                icon_name = "coffee"
            elif "tea" in store["type"].lower():
                icon_color = "purple"
                icon_name = "leaf"
            elif "supermarket" in store["type"].lower():
                icon_color = "orange"
                icon_name = "shopping-cart"
            
            folium.Marker(
                location=[store["latitude"], store["longitude"]],
                popup=f"<b>{store['name']}</b><br>Type: {store['type']}<br>{store['address']}",
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa")
            ).add_to(marker_cluster)

    # Display the map
    folium_static(m)

    # Display store details
    if stores:
        # Group stores by type
        store_types = {}
        for store in stores:
            store_type = store["type"]
            if store_type not in store_types:
                store_types[store_type] = []
            store_types[store_type].append(store)
        
        # Display stores by type
        st.write("### 🏪 Nearby Stores")
        
        # First show cafes/tea shops
        priority_types = ["Cafe", "Tea", "Coffee Shop"]
        for store_type in priority_types:
            if store_type in store_types:
                with st.expander(f"{store_type}s ({len(store_types[store_type])})", expanded=True):
                    for i, store in enumerate(store_types[store_type]):
                        st.write(f"#### {i+1}. {store['name']}")
                        st.write(f"📍 Address: {store['address']}")
                        st.write("---")
        
        # Then show other types
        for store_type, stores in store_types.items():
            if store_type not in priority_types:
                with st.expander(f"{store_type}s ({len(stores)})", expanded=False):
                    for i, store in enumerate(stores):
                        st.write(f"#### {i+1}. {store['name']}")
                        st.write(f"📍 Address: {store['address']}")
                        st.write("---")
    else:
        st.info("No stores found nearby. Try expanding your search area or checking a different location.")

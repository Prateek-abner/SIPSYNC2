# backend.py

import cohere
import os
import json
import random
from datetime import datetime
import requests
from dotenv import load_dotenv
import re
from googleapiclient.discovery import build
from train import (  # Import prompts and configurations from train.py
    COHERE_TEA_RECOMMENDATION_PROMPT,
    COHERE_PERSONALIZED_MESSAGE_PROMPT,
    COHERE_BREWING_TIP_PROMPT,
    COHERE_DAILY_TEA_DESCRIPTION_PROMPT,
    YOUTUBE_API_CONFIG
)

# Load API key from .env
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize Cohere Client
co = cohere.Client(COHERE_API_KEY)

# Load herbal tea recommendations database
def load_tea_data():
    try:
        with open("tea_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading tea database: {e}")
        # Fallback to minimal dataset if file is missing or invalid
        return {
            "sore throat": {
                "tea": "Ginger Tea",
                "benefits": ["Anti-inflammatory", "Soothes irritation", "Boosts immunity"],
                "ingredients": ["Fresh ginger root (1-inch piece)", "Lemon slice", "Honey", "Water (2 cups)"],
                "recipe": [
                    "Peel and thinly slice the ginger root",
                    "Bring water to a boil in a small pot",
                    "Add ginger slices and simmer for 5-10 minutes",
                    "Remove from heat, add lemon slice and honey to taste",
                    "Strain and enjoy while warm"
                ],
                "youtube_keywords": "ginger tea for sore throat benefits",
                "scientific_evidence": "Contains gingerol, which has anti-inflammatory and antioxidant properties. Studies show it may help reduce pain and inflammation."
            }
        }

# Load tea database
TEA_MATCHES = load_tea_data()

# Create synonym mapping for common ailments
AILMENT_SYNONYMS = {
    "sore throat": ["throat pain", "scratchy throat", "throat irritation", "pharyngitis"],
    "can't sleep": ["insomnia", "sleeplessness", "trouble sleeping", "sleep issues", "sleep problems"],
    "indigestion": ["upset stomach", "stomach ache", "dyspepsia", "heartburn", "acid reflux", "bloating"],
    "stress": ["anxiety", "tension", "nervous", "worried", "overwhelmed"],
    "headache": ["migraine", "head pain", "tension headache", "head pressure"],
    "cold": ["common cold", "runny nose", "stuffy nose", "congestion", "cough", "sore throat"],
    "fatigue": ["tired", "exhaustion", "low energy", "lethargy", "lack of energy"],
    "anxiety": ["nervousness", "worry", "panic", "anxious", "uneasy"]
}

def search_youtube(query):
    """
    Search YouTube for videos related to the query using the YouTube Data API.
    """
    try:
        # Initialize the YouTube API client
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        
        # Perform the search
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=YOUTUBE_API_CONFIG["max_results"],
            order=YOUTUBE_API_CONFIG["order"]
        )
        response = request.execute()
        
        # Extract video details
        videos = []
        for item in response["items"]:
            video = {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "channel": item["snippet"]["channelTitle"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "description": item["snippet"]["description"]
            }
            videos.append(video)
        
        return videos
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        # Fallback to mock data if API fails
        return [
            {
                "title": f"How to Prepare {query.title()} Tea",
                "url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
                "channel": "Herbal Wellness Academy",
                "thumbnail": f"https://img.youtube.com/vi/example{random.randint(1,5)}/mqdefault.jpg",
                "description": "Learn how to prepare this tea for maximum benefits."
            }
        ]

def find_best_match(user_input, tea_matches, synonyms_map):
    """
    Find the best matching ailment using direct matching, synonym matching,
    and fuzzy matching as a fallback.
    """
    user_input = user_input.lower()
    
    # Direct match
    for ailment in tea_matches:
        if ailment in user_input or user_input in ailment:
            return ailment
    
    # Synonym match
    for ailment, synonyms in synonyms_map.items():
        for synonym in synonyms:
            if synonym in user_input or user_input in synonym:
                return ailment
    
    # No direct match found, will use Cohere for recommendations
    return None

def get_seasonal_recommendations():
    """
    Return seasonally appropriate tea recommendations based on current month.
    """
    month = datetime.now().month
    
    if 3 <= month <= 5:  # Spring
        return ["peppermint", "nettle", "dandelion"], "Spring is a great time for detoxifying teas."
    elif 6 <= month <= 8:  # Summer
        return ["hibiscus", "peppermint", "lemon balm"], "Cooling teas are perfect for the summer heat."
    elif 9 <= month <= 11:  # Fall
        return ["ginger", "cinnamon", "elderberry"], "Support your immunity with these fall favorites."
    else:  # Winter
        return ["ginger", "echinacea", "elderberry"], "These warming teas are perfect for cold winter days."

def get_fun_tea_fact():
    """
    Return a random interesting fact about tea.
    """
    facts = [
        "Tea is the second most consumed beverage in the world after water.",
        "There are five main types of tea: black, green, white, oolong, and pu-erh.",
        "A cup of herbal tea typically contains zero calories if unsweetened.",
        "The antioxidants in tea may help protect against certain types of cancer.",
        "Tea has been used medicinally for over 5,000 years.",
        "Herbal teas aren't true teas as they don't come from the Camellia sinensis plant.",
        "The word 'tea' comes from the Chinese 'tê', which was the word in the Amoy dialect for the plant.",
        "Tea contains L-theanine, an amino acid that can help reduce stress and improve focus.",
        "Chamomile tea contains apigenin, an antioxidant that binds to certain receptors in your brain that may promote sleepiness.",
        "The ritual of drinking tea has been shown to have psychological benefits beyond the properties of the tea itself."
    ]
    return random.choice(facts)

def extract_symptom_severity(user_input):
    """
    Extract the potential severity of symptoms from user input.
    Returns a warning message if symptoms sound severe.
    """
    severe_indicators = [
        "severe", "extreme", "unbearable", "intense", "excruciating", 
        "worst", "debilitating", "agonizing", "can't function",
        "days", "weeks", "month", "chronic", "recurring"
    ]
    
    for indicator in severe_indicators:
        if indicator in user_input.lower():
            return ("Your symptoms sound significant. While tea may provide some relief, "
                   "please consider consulting a healthcare professional for persistent or severe conditions.")
    
    return None

def generate_cohere_tea_recommendation(ailment):
    """
    Use Cohere API to suggest the most appropriate tea when no direct match is found.
    """
    tea_options = [value["tea"] for value in TEA_MATCHES.values()]
    
    prompt = COHERE_TEA_RECOMMENDATION_PROMPT.format(ailment=ailment, tea_options=", ".join(tea_options))
    
    try:
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=10,
            temperature=0.2
        )
        suggested_tea = response.generations[0].text.strip()
        
        # Extract just the tea name using regex in case the model adds extra text
        tea_pattern = re.compile(r'([A-Za-z]+)(\s+Tea)', re.IGNORECASE)
        match = tea_pattern.search(suggested_tea)
        
        if match:
            return match.group(0).title()
        return suggested_tea
    except Exception as e:
        print(f"Error with Cohere API: {e}")
        # Fallback to a common recommendation
        return "Chamomile Tea"

def generate_response(ailment):
    """
    Generate a comprehensive, personalized tea recommendation using Cohere API.
    """
    if not ailment or ailment.strip() == "":
        return {
            "status": "error",
            "message": "Please provide a description of your ailment or symptoms."
        }
        
    ailment = ailment.lower().strip()
    
    # Check for best matching ailment
    best_match = find_best_match(ailment, TEA_MATCHES, AILMENT_SYNONYMS)
    
    # Extract severity warning if any
    severity_warning = extract_symptom_severity(ailment)
    
    # If no direct match, use Cohere to suggest a tea
    if not best_match:
        suggested_tea_name = generate_cohere_tea_recommendation(ailment)
        
        # Find the ailment that corresponds to this tea
        for key, value in TEA_MATCHES.items():
            if value["tea"].lower() == suggested_tea_name.lower():
                best_match = key
                break
    
    # If still no match (or failed API call), return error with suggestions
    if not best_match:
        seasonal_teas, seasonal_msg = get_seasonal_recommendations()
        return {
            "status": "no_match",
            "message": f"I don't have a specific recommendation for '{ailment}'. Try describing your symptoms differently or explore our suggestions.",
            "seasonal_recommendations": seasonal_teas,
            "seasonal_message": seasonal_msg,
            "fun_fact": get_fun_tea_fact()
        }
    
    # Get the tea data for the best match
    tea_data = TEA_MATCHES[best_match]
    
    # Get time context for personalization
    current_time = datetime.now()
    hour = current_time.hour
    time_context = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"
    season = "spring" if 3 <= current_time.month <= 5 else "summer" if 6 <= current_time.month <= 8 else "fall" if 9 <= current_time.month <= 11 else "winter"
    
    # Generate personalized message using Cohere
    prompt = COHERE_PERSONALIZED_MESSAGE_PROMPT.format(
        ailment=ailment,
        tea=tea_data["tea"],
        benefits=", ".join(tea_data["benefits"]),
        time_context=time_context,
        season=season
    )
    
    try:
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            k=0,
            p=0.75
        )
        
        personalized_message = response.generations[0].text.strip()
    except Exception as e:
        print(f"Error with Cohere API personalization: {e}")
        # Fallback to template message if API fails
        personalized_message = (
            f"For your {ailment}, I recommend {tea_data['tea']}. "
            f"It's known for its {tea_data['benefits'][0].lower()} properties, which may help provide relief. "
            f"It's especially nice to drink in the {time_context}. I hope you feel better soon!"
        )
    
    # Get preparation tips using Cohere
    try:
        prep_prompt = COHERE_BREWING_TIP_PROMPT.format(
            tea=tea_data["tea"],
            ailment=ailment
        )
        
        prep_response = co.generate(
            model="command",
            prompt=prep_prompt,
            max_tokens=80,
            temperature=0.5
        )
        
        brewing_tip = prep_response.generations[0].text.strip()
    except Exception as e:
        print(f"Error with Cohere API brewing tip: {e}")
        brewing_tip = f"Pro tip: For maximum benefit, steep {tea_data['tea'].lower()} for 5-7 minutes using water just below boiling point."
    
    # Return comprehensive response
    return {
        "status": "success",
        "ailment": best_match,
        "original_query": ailment,
        "tea_data": tea_data,
        "personalized_message": personalized_message,
        "brewing_tip": brewing_tip,
        "videos": search_youtube(tea_data["youtube_keywords"]),
        "severity_warning": severity_warning,
        "fun_fact": get_fun_tea_fact() if random.random() > 0.5 else None,
        "seasonal_context": f"This tea is particularly beneficial during {season} months."
    }

# Function to provide daily tea recommendation
def get_daily_recommendation():
    """Provide a daily tea recommendation based on current needs."""
    today = datetime.now()
    # Use the day of year to cycle through recommendations
    day_of_year = today.timetuple().tm_yday
    teas = list(TEA_MATCHES.values())
    recommended_tea = teas[day_of_year % len(teas)]
    
    # Generate creative description
    try:
        prompt = COHERE_DAILY_TEA_DESCRIPTION_PROMPT.format(tea=recommended_tea["tea"])
        
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        description = response.generations[0].text.strip()
    except Exception as e:
        print(f"Error generating daily tea description: {e}")
        description = (
            f"{recommended_tea['tea']} is our Tea of the Day! Known for its {', '.join(recommended_tea['benefits'][:2]).lower()} properties, "
            f"this remarkable tea can be your perfect companion today."
        )
    
    return {
        "tea": recommended_tea['tea'],
        "benefits": recommended_tea['benefits'][:2],
        "description": description,
        "image_url": f"tea_{recommended_tea['tea'].lower().replace(' ', '_')}.jpg"
    }

# Advanced function to suggest complementary herbs
def suggest_complementary_herbs(tea_name):
    """Suggest complementary herbs that pair well with the recommended tea."""
    complementary_herbs = {
        "Ginger Tea": ["Lemon", "Honey", "Turmeric", "Cinnamon"],
        "Chamomile Tea": ["Lavender", "Lemon Balm", "Mint", "Honey"],
        "Peppermint Tea": ["Fennel", "Ginger", "Lemon", "Anise"],
        "Lavender Tea": ["Chamomile", "Lemon Balm", "Rose", "Valerian"],
        "Elderberry Tea": ["Echinacea", "Rose Hips", "Cinnamon", "Ginger"],
        "Lemon Balm Tea": ["Chamomile", "Mint", "Valerian", "Passionflower"]
    }
    
    default_complements = ["Honey", "Lemon", "Ginger", "Cinnamon"]
    
    return complementary_herbs.get(tea_name, default_complements)

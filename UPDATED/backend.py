# backend.py

import cohere
import os
import google.generativeai as genai
from dotenv import load_dotenv
from train import RECOMMENDATIONS, COHERE_PERSONALIZED_MESSAGE_PROMPT
from fuzzywuzzy import process
import re

# Load API keys from .env
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

# Initialize Cohere Client
co = cohere.Client(COHERE_API_KEY)

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def preprocess_input(user_input):
    """
    Preprocess user input to extract keywords.
    """
    # Convert to lowercase and remove special characters
    user_input = user_input.lower()
    user_input = re.sub(r'[^a-zA-Z\s]', '', user_input)
    return user_input.strip()

def find_closest_ailment(user_input):
    """
    Find the closest matching ailment using fuzzy matching.
    """
    ailments = list(RECOMMENDATIONS.keys())
    closest_match, score = process.extractOne(user_input, ailments)
    return closest_match if score > 70 else None  # Only return if the match is above 70% confidence

def generate_response(user_input, drink_type="tea"):
    """
    Generate a personalized recommendation based on the user's input.
    """
    # Preprocess input and find the closest matching ailment
    processed_input = preprocess_input(user_input)
    closest_ailment = find_closest_ailment(processed_input)
    
    # If no close match is found, use Google Generative AI for a custom response
    if not closest_ailment:
        prompt = f"Suggest a drink or light food for someone who is feeling {user_input}. Provide a short, friendly recommendation."
        try:
            response = model.generate_content(prompt)
            return {
                "status": "success",
                "ailment": user_input,
                "drink": "Custom Recommendation",
                "benefits": ["General wellness"],
                "brewing_tip": response.text,
                "ingredients": ["Varies based on availability"],
                "youtube_keywords": f"{user_input} relief",
                "personalized_message": response.text
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"No recommendation found for '{user_input}'. Try a different ailment."
            }
    
    # Use the closest matching ailment to fetch recommendations
    recommendation = RECOMMENDATIONS[closest_ailment]
    drink = recommendation[drink_type]
    benefits = recommendation["benefits"]
    brewing_tip = recommendation["brewing_tip"]
    ingredients = recommendation["ingredients"]
    youtube_keywords = recommendation["youtube_keywords"]

    # Generate personalized message using Cohere
    prompt = COHERE_PERSONALIZED_MESSAGE_PROMPT.format(
        ailment=closest_ailment,
        drink=drink,
        benefits=", ".join(benefits),
        brewing_tip=brewing_tip
    )
    
    try:
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        personalized_message = response.generations[0].text.strip()
    except Exception as e:
        print(f"Error with Cohere API: {e}")
        personalized_message = (
            f"For your {closest_ailment}, I recommend {drink}. "
            f"It's known for its {benefits[0].lower()} properties, which may help provide relief. "
            f"Here's a tip: {brewing_tip}"
        )
    
    return {
        "status": "success",
        "ailment": closest_ailment,
        "drink": drink,
        "benefits": benefits,
        "brewing_tip": brewing_tip,
        "ingredients": ingredients,
        "youtube_keywords": youtube_keywords,
        "personalized_message": personalized_message
    }

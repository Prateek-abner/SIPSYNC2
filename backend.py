# backend.py

import cohere
import os
import google.generativeai as genai
from dotenv import load_dotenv
from train import RECOMMENDATIONS, COHERE_PERSONALIZED_MESSAGE_PROMPT, WEATHER_RECOMMENDATIONS
from fuzzywuzzy import process
import re
import requests
from datetime import datetime

# Load API keys from .env
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize Cohere Client
co = cohere.Client(COHERE_API_KEY)

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class RecommendationError(Exception):
    """Custom exception for recommendation-related errors"""
    pass

def get_weather(latitude, longitude):
    """
    Get current weather conditions to adjust recommendations.
    """
    if not WEATHER_API_KEY:
        print("Warning: Weather API key not found")
        return None
        
    if not latitude or not longitude:
        return None
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}"
        response = requests.get(url, timeout=10)  # Add timeout
        if response.status_code == 200:
            data = response.json()
            temp = data.get('main', {}).get('temp')
            if not temp:
                return None
            temp = temp - 273.15  # Convert to Celsius
            conditions = data.get('weather', [{}])[0].get('main', '').lower()
            
            if temp < 15:
                return "cold"
            elif temp > 25:
                return "hot"
            elif conditions in ['rain', 'drizzle', 'thunderstorm']:
                return "rainy"
    except requests.RequestException as e:
        print(f"Weather API error: {e}")
    except (KeyError, IndexError, ValueError) as e:
        print(f"Weather data parsing error: {e}")
    except Exception as e:
        print(f"Unexpected weather API error: {e}")
    return None

def preprocess_input(user_input):
    """
    Preprocess user input to extract keywords and sentiment.
    """
    if not user_input or not isinstance(user_input, str):
        raise RecommendationError("Invalid input: Please provide a valid text description")
        
    try:
        # Convert to lowercase and remove special characters
        user_input = user_input.lower()
        user_input = re.sub(r'[^a-zA-Z\s]', '', user_input)
        
        # Extract severity indicators
        severity = "mild"
        if any(word in user_input for word in ["severe", "terrible", "extreme"]):
            severity = "severe"
        elif any(word in user_input for word in ["moderate", "quite", "rather"]):
            severity = "moderate"
            
        processed_input = user_input.strip()
        if not processed_input:
            raise RecommendationError("Invalid input: Please provide a valid description")
            
        return processed_input, severity
    except Exception as e:
        raise RecommendationError(f"Error processing input: {str(e)}")

def find_closest_ailment(user_input):
    """
    Find the closest matching ailment using fuzzy matching with context awareness.
    """
    if not user_input:
        return None
        
    try:
        ailments = list(RECOMMENDATIONS.keys())
        # Get top 3 matches
        matches = process.extractBests(user_input, ailments, score_cutoff=60, limit=3)
        
        if not matches:
            return None
            
        # If we have an exact match, use it
        if matches[0][1] > 90:
            return matches[0][0]
            
        # Use Gemini to select the most appropriate match
        prompt = f"""
        Given the user's description: '{user_input}'
        And these potential matches: {[m[0] for m in matches]}
        Which ailment is the most appropriate match? Consider synonyms and related symptoms.
        Return ONLY the ailment name, nothing else.
        """
        
        try:
            response = model.generate_content(prompt)
            suggested_ailment = response.text.strip().lower()
            if suggested_ailment in ailments:
                return suggested_ailment
        except Exception as e:
            print(f"Gemini API error: {e}")
        
        # Fall back to the highest fuzzy match
        return matches[0][0] if matches[0][1] > 70 else None
    except Exception as e:
        print(f"Error finding closest ailment: {e}")
        return None

def generate_response(user_input, drink_type="tea", latitude=None, longitude=None):
    """
    Generate a personalized recommendation based on the user's input and context.
    """
    if not user_input:
        return {
            "status": "error",
            "message": "Please provide a description of how you're feeling",
            "ailment": ""
        }
        
    if drink_type not in ["tea", "coffee", "milkshake", "light_food"]:
        return {
            "status": "error",
            "message": "Invalid drink type selected",
            "ailment": ""
        }
    
    try:
        # Get weather conditions if location is provided
        weather_condition = get_weather(latitude, longitude) if latitude and longitude else None
        
        # Preprocess input and find the closest matching ailment
        processed_input, severity = preprocess_input(user_input)
        closest_ailment = find_closest_ailment(processed_input)
        
        # If no close match is found, use Gemini for a custom response
        if not closest_ailment:
            prompt = f"""
            Suggest a {drink_type} or light food for someone who is feeling {user_input}.
            Consider:
            - Severity: {severity}
            - Weather: {weather_condition if weather_condition else 'unknown'}
            Provide a detailed, evidence-based recommendation with preparation instructions.
            Format the response as a brief paragraph.
            """
            try:
                response = model.generate_content(prompt)
                if not response or not response.text:
                    raise RecommendationError("Failed to generate recommendation")
                    
                custom_response = {
                    "status": "success",
                    "ailment": processed_input,
                    "drink": f"Custom {drink_type.title()} Recommendation",
                    "benefits": ["Relieves " + processed_input, "Promotes wellness"],
                    "brewing_tip": response.text,
                    "ingredients": ["Natural ingredients", "Based on availability"],
                    "youtube_keywords": f"natural remedies for {processed_input}",
                    "personalized_message": response.text,
                    "sustainability_score": 4.0,
                    "eco_friendly_tips": ["Choose organic ingredients", "Use reusable containers"],
                    "weather_adjusted": bool(weather_condition),
                    "cultural_origin": "Various Traditional Medicines",
                    "scientific_evidence": "Based on natural healing principles"
                }
                return custom_response
            except Exception as e:
                print(f"Error generating custom response: {e}")
                return {
                    "status": "error",
                    "message": f"Unable to generate recommendation for '{user_input}'. Please try a different description.",
                    "ailment": processed_input
                }
        
        # Use the closest matching ailment to fetch recommendations
        recommendation = RECOMMENDATIONS[closest_ailment].copy()
        
        # Adjust recommendation based on weather if available
        if weather_condition and weather_condition in WEATHER_RECOMMENDATIONS:
            weather_rec = WEATHER_RECOMMENDATIONS[weather_condition]
            recommendation['ingredients'].extend(weather_rec['boost'])
            recommendation['brewing_tip'] += f" Weather tip: {''.join(weather_rec['boost'])}"
        
        # Generate personalized message using Cohere
        try:
            prompt = COHERE_PERSONALIZED_MESSAGE_PROMPT.format(
                ailment=closest_ailment,
                drink=recommendation[drink_type],
                benefits=", ".join(recommendation["benefits"]),
                brewing_tip=recommendation["brewing_tip"],
                cultural_origin=recommendation["cultural_origin"],
                scientific_evidence=recommendation["scientific_evidence"],
                sustainability_score=recommendation["sustainability_score"],
                eco_friendly_tips=", ".join(recommendation["eco_friendly_tips"])
            )
            
            response = co.generate(
                model="command",
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            personalized_message = response.generations[0].text.strip()
        except Exception as e:
            print(f"Error with Cohere API: {e}")
            personalized_message = (
                f"For your {closest_ailment}, I recommend {recommendation[drink_type]}. "
                f"It's known for its {recommendation['benefits'][0].lower()} properties and has roots in {recommendation['cultural_origin']}. "
                f"{recommendation['scientific_evidence']}. Here's a tip: {recommendation['brewing_tip']}"
            )
        
        # Add required fields to response
        recommendation['weather_adjusted'] = bool(weather_condition)
        recommendation['personalized_message'] = personalized_message
        recommendation['status'] = "success"
        recommendation['ailment'] = closest_ailment
        recommendation['drink'] = recommendation[drink_type]
        
        return recommendation
        
    except RecommendationError as e:
        return {
            "status": "error",
            "message": str(e),
            "ailment": user_input
        }
    except Exception as e:
        print(f"Unexpected error in generate_response: {e}")
        return {
            "status": "error",
            "message": "An unexpected error occurred. Please try again.",
            "ailment": user_input
        }
